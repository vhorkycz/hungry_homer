#!/usr/bin/env python3

import pyglet

from hungry_homer import objects


class State:
    """Base class for window states."""

    def __init__(self, game):
        """Initialize a state."""
        self.game = game
        self.key = self.game.key
        self.key_handler = self.game.key_handler
        self.batch = pyglet.graphics.Batch()

    def update(self):
        """This should be implemented in the actual state class."""
        raise NotImplementedError


class MenuItem(pyglet.text.Label):
    """A menu item, now only for levels."""

    def __init__(self, *args, game, i, selected, text, **kwargs):
        """Initializes a menu item."""
        self.game = game
        self.i = i
        self.selected = selected
        self.actual_text = text
        super().__init__(*args, text=text, **kwargs)

    def update(self):
        """Highlights the item if selected."""
        if self.selected:
            self.text = "> " + self.actual_text + " <"
        else:
            self.text = self.actual_text

    def action(self):
        """Opens the level."""
        self.game.state = Level(self.game, self.game.maps[self.i])


class Menu(State):
    """Menu for choosing a level."""

    def __init__(self, game):
        """Initializes the menu."""
        super().__init__(game)
        self.items = None
        self.selected_i = 0
        self.setup_items()

    def setup_items(self):
        """Initializes the menu items and centres them."""
        self.items = []
        item_count = len(self.game.maps)
        font_size = 20
        x = self.game.width // 2
        anchor_x = "center"
        y = (self.game.height + item_count * font_size) // 2
        for i in range(len(self.game.maps)):
            item = MenuItem(
                game=self.game,
                x=x, anchor_x=anchor_x, y=y,
                i=i,
                text=f"Level {i+1}",
                batch=self.batch,
                font_size=font_size,
                color=(0, 0, 0, 255),   # black
                selected=(i == self.selected_i)
                )
            self.items.append(item)
            y -= font_size * 2

    def on_key_press(self, symbol, modifiers):
        """Selects another item, calls its action, or closes the game."""
        if symbol in (self.key.DOWN, self.key.UP):
            direction = 1 if symbol == self.key.DOWN else -1
            self.select(direction)
        elif symbol == self.key.RETURN:
            self.items[self.selected_i].action()
        elif symbol == pyglet.window.key.ESCAPE:
            self.game.close()

    def select(self, direction):
        """
        Selects previous/next item (unless the top or bottom one was
        selected before).
        """
        new_i = self.selected_i + direction
        if 0 <= new_i < len(self.items):
            self.items[self.selected_i].selected = False
            self.selected_i = new_i
            self.items[self.selected_i].selected = True

    def update(self):
        """Highlights the selected item."""
        for item in self.items:
            item.update()


class Level(State):
    """A game level class."""

    def __init__(self, game, map_):
        """Initializes a level."""
        super().__init__(game)
        self.map = map_

        self.object_size = 20
        self.object_speed = 2
        self.object_directions = (
            (0, 1),    # up
            (1, 0),    # right
            (0, -1),   # down
            (-1, 0),   # left
            (0, 0)     # stay
            )

        # when two objects overlap, this decides which should be on top
        self.subgroups = {
            "background": pyglet.graphics.OrderedGroup(0),
	    "watchers": pyglet.graphics.OrderedGroup(1),
            "homer": pyglet.graphics.OrderedGroup(2)
            }

        self.objects = None
        self.food_count = 0
        self.setup_objects()

        self.paused = False

    def setup_objects(self):
        """Initializes objects from the level map."""

        self.objects = {
            "homer": [],
            "watchers": [],
            "gate": [],
            "collectibles": [],
            "bell": [],
            "bricks": []
            }
        self.food_count = 0

        circular_watchers = "urdlURDL"
        linear_watchers = "^>v<"
        watchers = circular_watchers + linear_watchers

        for i, row in enumerate(self.map):
            for j, symbol in enumerate(row):
                # skip empty positions
                if symbol in " .":
                    continue

                batch_group = None
                if symbol == "H":
                    batch_group = "homer"
                elif symbol in watchers:
                    batch_group = "watchers"
                else:
                    batch_group = "background"

                group = None
                if symbol in circular_watchers:
                    class_ = objects.CircularWatcher
                    group = "watchers"
                elif symbol in linear_watchers:
                    class_ = objects.LinearWatcher
                    group = "watchers"
                elif symbol == "X":
                    class_ = objects.Brick
                    group = "bricks"
                elif symbol == "*":
                    class_ = objects.Food
                    group = "collectibles"
                    self.food_count += 1
                elif symbol == "H":
                    class_ = objects.Homer
                    group = "homer"
                elif symbol == "_":
                    class_ = objects.Key
                    group = "collectibles"
                elif symbol == "/":
                    class_ = objects.Gate
                    group = "gate"
                elif symbol == "b":
                    class_ = objects.Bell
                    # not really a collectible, but it doesn't matter here
                    group = "collectibles"

                arguments = {
                    "game": self.game,
                    "level": self,
                    "map_position": (j, i),
                    "batch": self.batch,
                    "group": self.subgroups[batch_group]
                    }

                if symbol in circular_watchers:
                    arguments["direction_i"] = (
                        circular_watchers.index(symbol) % 4
                        )
                    arguments["side"] = 1 if symbol.islower() else -1
                elif symbol in linear_watchers:
                    arguments["direction_i"] = (
                        linear_watchers.index(symbol) % 4
                        )

                object_ = class_(**arguments)
                self.objects[group].append(object_)

    def complete(self, dt):
        """Returns to menu after Homer wins and selects the next level."""
        self.game.menu.select(1)
        self.game.state = self.game.menu

    def is_forbidden(self, position, direction_i=4, has_key=False):
        """
        Checks whether a moving object can move to the position in
        the given direction.
        """
        x = position[0] + self.game.object_directions[direction_i][0]
        y = position[1] + self.game.object_directions[direction_i][1]
        forbidden = "X." if has_key else "X./"
        # don't go outside the window
        if not (
            0 <= x < self.game.grid_width
            and 0 <= y < self.game.grid_height
            ):
            return True
        return self.map[y][x] in forbidden

    def on_key_press(self, symbol, modifiers):
        """Pauses the game or returns to the menu."""
        if symbol == self.key.P:
            self.paused = not self.paused
        elif symbol == self.key.ESCAPE:
            self.game.state = self.game.menu

    def update(self):
        """Updates the objects and handles their collisions."""
        # don't do anything when paused
        if self.paused:
            return

        # update all the objects
        for group in self.objects.values():
            for object_ in group:
                object_.update()

        # handle collisions
        # Homer + watcher
        for watcher in self.objects["watchers"]:
            self.objects["homer"][0].handle_collision(watcher)
        # Homer + collectible
        for collectible in self.objects["collectibles"]:
            self.objects["homer"][0].handle_collision(collectible)
            collectible.handle_collision(self.objects["homer"][0])
        # Homer + gate
        self.objects["homer"][0].handle_collision(self.objects["gate"][0])
        
        # watcher + watcher
        for first in self.objects["watchers"]:
            for second in self.objects["watchers"]:
                if first is second:
                    continue
                first.handle_collision(second)

        # remove things taken by Homer
        collectibles_to_delete = [
            collectible for collectible in self.objects["collectibles"]
            if not collectible.exists
            ]
        self.objects["collectibles"] = [
            collectible for collectible in self.objects["collectibles"]
            if collectible.exists
            ]
        for collectible in collectibles_to_delete:
            collectible.delete()
