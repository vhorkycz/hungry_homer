#!/usr/bin/env python3

from importlib import resources

import pyglet

from hungry_homer import states


class Game(pyglet.window.Window):

    def __init__(self):
        """Initializes the game window."""
        self.grid_width = 32
        self.grid_height = 24
        self.object_size = 20
        self.object_speed = 2
        self.object_directions = (
            (0, 1),    # up
            (1, 0),    # right
            (0, -1),   # down
            (-1, 0),   # left
            (0, 0)     # stay
            )
        super().__init__(
            width=(self.grid_width * self.object_size),
            height=(self.grid_height * self.object_size),
            caption="Hungry Homer"
            )

        # set background colour as white
        pyglet.gl.glClearColor(1, 1, 1, 1)
        # register key input
        self.key = pyglet.window.key
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)

        self.clock = pyglet.clock

        self.maps_location = "hungry_homer.level_maps"
        self.maps = self.__read_maps()

        self.menu = states.Menu(game=self)
        self.state = self.menu

    def on_draw(self):
        """Clears the window and draws the current state batch."""
        self.clear()
        self.state.batch.draw()

    def update(self, dt):
        """Calls the current state to update itself."""
        # ignore dt, always move by some number of pixels
        self.state.update()

    def run(self):
        """Runs game window and updates it every 1/120 s."""
        self.clock.schedule_interval(self.update, 1/120)
        pyglet.app.run()

    def on_key_press(self, symbol, modifiers):
        """Call the current state's on_key_press."""
        self.state.on_key_press(symbol, modifiers)

    def __read_maps(self):
        """
        Reads maps from map_dir as lists of lists of elements (from bottom
        to top row), and pads them, so they get centred with given window
        width and height.
        """
        map_paths = sorted([
            path for path in resources.contents(self.maps_location)
            if path.endswith(".txt")
            ])
        maps = []
        for path in map_paths:
            with resources.open_text(self.maps_location, path) as file:
                map_ = [list(line.rstrip()) for line in file]
                # reverse <= pyglet counts from the bottom left corner
                map_.reverse()
                # if a map is smaller than window size, pad it,
                # so it gets centred
                map_height = len(map_)
                map_width = max((len(row) for row in map_))
                if map_height > self.grid_height or map_width > self.grid_width:
                    raise ValueError(
                        f"map in {path!r} is too big"
                        + f" ({map_width}x{map_height},"
                        + f" maximum is {self.grid_width}x{self.grid_height})"
                        )
                padding_row_count = (self.grid_height - map_height) // 2
                padding_column_count = (self.grid_width - map_width) // 2
                padded = []
                # pad from the bottom
                padded.extend([["."] * self.grid_width] * padding_row_count)
                # pad from the left and the right
                for row in map_:
                    new_row = ["."] * padding_column_count + row
                    new_row += ["."] * (self.grid_width - len(new_row))
                    padded.append(new_row)
                # pad from the top
                padded.extend(
                    [["."] * self.grid_width] * (self.grid_height - len(padded))
                    )
                maps.append(padded)
        return maps

    def __print_maps(self):
        """Prints maps."""
        for map_ in self.maps:
            for row in map_:
                print("".join(row))
            print()
