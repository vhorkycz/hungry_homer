#!/usr/bin/env python3

"""
Hungry Homer
============

 - move with arrows
 - don't bump into watchers (at most once per level)
 - take all the food and open the gate with the key
 - get to the gate

 - pause with P
 - close with ESC
"""

from hungry_homer import game

def main():
    """Runs the game."""
    game_window = game.Game()
    game_window.run()

if __name__ == "__main__":
    main()
