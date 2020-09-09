#!/usr/bin/env python3

"""Module with classes for all the level objects."""

import pyglet
key = pyglet.window.key


# set directory with images
pyglet.resource.path = ['@hungry_homer.resources_dir']
pyglet.resource.reindex()
# object images
images = {
    "homer": pyglet.image.ImageGrid(
        pyglet.resource.image("homer.png"), 1, 4
        ),
    "brick": pyglet.resource.image("brick.png"),
    "circular_watcher": pyglet.image.ImageGrid(
        pyglet.resource.image("circular_watcher.png"), 1, 4
        ),
    "linear_watcher": pyglet.image.ImageGrid(
        pyglet.resource.image("linear_watcher.png"), 1, 4
        ),
    "key": pyglet.resource.image("key.png"),
    "gate": pyglet.image.ImageGrid(
        pyglet.resource.image("gate.png"), 1, 2
        ),
    "food": pyglet.resource.image("food.png"),
    "bell": pyglet.image.ImageGrid(
        pyglet.resource.image("bell.png"), 1, 5
        )
    }


class Object(pyglet.sprite.Sprite):
    """Base class for all level objects."""

    def __init__(self, game, level, map_position, *args, **kwargs):
        """Initializes an object."""
        self.game = game
        self.level = level
        self.size = self.game.object_size
        self.map_position = map_position
        self.in_place = True    # i. e. at exactly one point of the grid
        self.exists = True
        super().__init__(
            *args, **kwargs,
            x=(map_position[0] * self.size),
            y=(map_position[1] * self.size)
            )

    def update(self):
        """Updates the object (should be called every frame)."""
        pass

    def handle_collision(self, other):
        """Updates the object after colliding with another one."""
        pass

    def collides(self, other):
        """
        Finds whether the object collides with another one, i. e.
        whether they at least touch with their corners.
        """
        return (
            abs(other.x - self.x) <= self.size
            and abs(other.y - self.y) <= self.size
            )

    def overlaps(self, other):
        """
        Finds whether the object completely overlaps another one, i. e.
        whether they have the same coordinates.
        """
        return other.x == self.x and other.y == self.y


class Brick(Object):
    """An obstacle through which noone can go."""

    def __init__(self, *args, **kwargs):
        """Initializes a brick."""
        super().__init__(img=images["brick"], *args, **kwargs)


class Gate(Object):
    """
    Gate which gets opened when Homer collects the key. Homer must enter
    it to win.
    """

    def __init__(self, *args, **kwargs):
        """Initializes the gate."""
        self.image_grid = images["gate"]
        super().__init__(*args, img=self.image_grid[0], **kwargs)
        self.opened = False

    def open(self):
        """Updates image according to whether the gate is opened."""
        if self.level.objects["homer"][0].has_key:
            self.opened = True
        if self.opened:
            self.image = self.image_grid[1]
        else:
            self.image = self.image_grid[0]



class MovingObject(Object):
    """Base class for moving objects."""

    def __init__(self, image_grid, *args, **kwargs):
        """Initializes a moving object."""
        self.image_grid = image_grid
        super().__init__(*args, img=self.image_grid[0], **kwargs)
        self.speed = self.game.object_speed
        self.directions = self.game.object_directions
        self.direction_i = 4

    def update(self):
        """
        Updates moving object's coordinates and image orientation
        according to its direction.
        """
        # update coordinates
        self.x += self.directions[self.direction_i][0] * self.speed
        self.y += self.directions[self.direction_i][1] * self.speed
        self.in_place = (
            self.x % self.size == 0
            and self.y % self.size == 0
            )
        if self.in_place:
            self.map_position = (
                self.x // self.size,
                self.y // self.size
                )
        # update image orientation
        if self.direction_i < 4:
            # BUG: orientation should be changed also when trying to
            # move into a wall (this manifests only in a corner)
            self.image = self.image_grid[self.direction_i]


class Homer(MovingObject):
    """Player's object."""

    def __init__(self, *args, **kwargs):
        """Initializes Homer."""
        super().__init__(image_grid=images["homer"], *args, **kwargs)
        self.key = self.game.key
        self.key_handler = self.game.key_handler
        self.food_count = 0
        self.has_key = False
        self.bump_count = 0
        self.invincible = False
        self.lost = False
        self.won = False

    def update(self):
        """Updates Homers's direction etc."""

        # vanish if lost
        if self.lost:
            if self.opacity > 0:
                self.opacity -= 5
            # restart the level
            else:
                self.level.setup_objects()
        else:
            # flash if invincible (after bumping into a watcher or
            # winning)
            if self.invincible and self.opacity == 255:
                self.opacity = 100
            else:
                self.opacity = 255

            # after winning slowly go away
            if self.won:
                self.speed = 1

            else:
                # register new direction
                for i, key in enumerate(
                    (self.key.UP, self.key.RIGHT,
                     self.key.DOWN, self.key.LEFT)
                    ):
                    if self.key_handler[key]:
                        new_direction_i = i
                        break
                # no key pressed => don't move
                else:
                    new_direction_i = 4

                # stop before moving into a brick
                if (
                    self.in_place
                    and self.level.is_forbidden(
                        self.map_position, new_direction_i,
                        has_key=self.has_key
                        )
                    ):
                    new_direction_i = 4

                # actually change direction
                if (
                    # only if in place
                    self.in_place
                    # or if Homer turns around
                    or (
                        new_direction_i < 4
                        and abs(self.direction_i - new_direction_i) == 2
                        )
                    ):
                    self.direction_i = new_direction_i

        # change coordinates accordingly
        super().update()

    def handle_collision(self, other):
        """Updates Homer after colliding with collectibles or watchers."""

        # watchers
        if (
            self.collides(other)
            and isinstance(other, Watcher)
            and not self.invincible
            ):
            if self.bump_count == 1:
                self.lost = True
                # dramatically fly down
                self.speed = 4
                self.direction_i = 2
            else:
                self.bump_count += 1
                self.invincible = True
                self.game.clock.schedule_once(
                    self.end_invincibility, 1.0
                    )

        # collectibles + gate + bell
        if self.overlaps(other):
            if isinstance(other, Food):
                self.food_count += 1
            elif isinstance(other, Key):
                self.has_key = True
                self.level.objects["gate"][0].open()
            elif (
                isinstance(other, Gate)
                and self.food_count == self.level.food_count
                # only if Homer didn't already enter the gate
                and not self.won
                ):
                # now it doesn't matter whether a watcher happens to
                # touch Homer (and this also does that cool flashing)
                self.invincible = True
                self.won = True
                self.game.clock.schedule_once(
                    self.level.complete, 1.0
                    )
            elif (
                isinstance(other, Bell)
                # Homer can ring it only once
                and not other.rung
                ):
                self.invincible = True
                # if already invincible, prevent premature end_invincibility
                self.game.clock.unschedule(self.end_invincibility)
                self.game.clock.schedule_once(
                    self.end_invincibility, 3.0
                    )

    def end_invincibility(self, dt):
        """Ends invincibility after bumping into a watcher."""
        self.invincible = False


class Watcher(MovingObject):
    """Base class for watchers."""


class CircularWatcher(Watcher):
    """A watcher who always keeps a wall on his left/right side."""

    def __init__(self, side, direction_i, *args, **kwargs):
        """Initializes a circular watcher."""
        super().__init__(image_grid=images["circular_watcher"], *args, **kwargs)
        self.direction_i = direction_i
        self.side = side

    def update(self):
        """
        Always keeps a wall on the given side. (If no wall is there,
        they turn to the side; if a wall is ahead, they turn to the
        other side.)
        """
        if self.in_place:
            # no wall on the given side => turn to the side
            if not self.level.is_forbidden(
                self.map_position, (self.direction_i + self.side) % 4
                ):
                self.direction_i = (self.direction_i + self.side) % 4
            else:
                # wall ahead => turn to the other side
                # (this may happen only twice, unless the watcher is
                # completely enclosed which really shouldn't happen)
                i = 0
                while (
                    self.level.is_forbidden(
                        self.map_position, self.direction_i
                        )
                    and i <= 2
                    ):
                    self.direction_i = (self.direction_i - self.side) % 4
                    i += 1
        super().update()

    def handle_collision(self, other):
        """Changes the side after bumping into another watcher."""
        if self.collides(other) and isinstance(other, Watcher):
            self.side *= -1
            self.direction_i = (self.direction_i + 2) % 4


class LinearWatcher(Watcher):
    """A watcher who moves horizontally/vertically."""

    def __init__(self, direction_i, *args, **kwargs):
        """Initializes a linear watcher."""
        super().__init__(image_grid=images["linear_watcher"], *args, **kwargs)
        self.direction_i = direction_i

    def update(self):
        """Turns around after bumping into wall."""
        if self.in_place:
            # wall ahead
            if self.level.is_forbidden(
                self.map_position, self.direction_i
                ):
                self.turn_around()
        super().update()

    def turn_around(self):
        """Turns around."""
        self.direction_i = (self.direction_i + 2) % 4

    def handle_collision(self, other):
        """Turns around after bumping into another watcher."""
        # return
        if self.collides(other) and isinstance(other, Watcher):
            self.turn_around()


class Collectible(Object):
    """Base class for objects which Homer can take."""

    def handle_collision(self, other):
        """
        Marks itself as to be deleted after it is completely overlapped
        by Homer.
        """
        if self.overlaps(other) and isinstance(other, Homer):
            self.exists = False


class Food(Collectible):
    """Food which can be eaten by Homer."""

    def __init__(self, *args, **kwargs):
        """Initializes food."""
        super().__init__(img=images["food"], *args, **kwargs)


class Key(Collectible):
    """Key which opens the gate after Homer gets it."""

    def __init__(self, *args, **kwargs):
        """Initializes the key."""
        super().__init__(img=images["key"], *args, **kwargs)

class Bell(Object):
    """Bell which Homer can ring once."""

    def __init__(self, *args, **kwargs):
        """Initializes a bell."""
        self.image_grid = images["bell"]
        self.rung = False
        super().__init__(*args, img=self.image_grid[0], **kwargs)

    def handle_collision(self, other):
        """
        Rings if Homer hasn't rung it yet.
        """
        if not self.rung and self.overlaps(other) and isinstance(other, Homer):
            self.rung = True
            self.image = pyglet.image.Animation.from_image_sequence(
                images["bell"][:4], duration=0.1
                )
            self.game.clock.schedule_once(
                self.stop_ringing, 3.0
                )

    def stop_ringing(self, dt):
        """Stops ringing."""
        self.image = self.image_grid[4]

