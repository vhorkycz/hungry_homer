Hungry Homer
============

**Hungry Homer** is a game inspired by [Hungry Horace](https://en.wikipedia.org/wiki/Horace_(video_game_series)#Hungry_Horace)
(which was in turn inspired by [Pac-Man](https://en.wikipedia.org/wiki/Pac-Man))
which I've done as a requirement for NPRG031 programming course at MFF UK.


Requirements
------------

 * Python 3.7 or higher
 * [pyglet](https://pypi.org/project/pyglet/)


Installation
------------

Run `git clone https://github.com/vhorkycz/hungry_homer/` in your terminal,
go to the repository directory, and then run
`pip install . --user`
(or create a virtual environment, and run `pip install .` in it).


How to play
-----------

 * run `hungry_homer`
 
 - select a level with arrows
 
 - move with arrows
 - don't bump into watchers (at most once per level)
    - if you do, for a moment (indicated by flashing) it won't matter if you bump into one again
    - you can once ring a bell to make watchers too busy marvelling at it (but you can't eat them, that would be nasty)
 - to win, take all the food, open the gate with the key and get to the gate
 - you lose if you bump into a watcher twice (after that, the current level is restarted)

 - pause with P
 - close with ESC

| image | object | description |
| --- | --- | --- |
| ![](hungry_homer/resources_dir/homer_up.png) | Homer | you! |
| ![](hungry_homer/resources_dir/circular_watcher_up.png) | circular watcher | always keeps a wall on their left/right side, switches the side after bumping into another watcher |
| ![](hungry_homer/resources_dir/linear_watcher_up.png) | linear watcher | moves horizontally/vertically, turns around after bumping into a wall or another watcher |
| ![](hungry_homer/resources_dir/brick.png) | brick | noone can go through it |
| ![](hungry_homer/resources_dir/food.png) | food | take all of it |
| ![](hungry_homer/resources_dir/key.png) | key | you have to take it to open the gate |
| ![](hungry_homer/resources_dir/bell_silent.png) | bell | ring it so that watchers leave you alone for a moment (only once!) |
| ![](hungry_homer/resources_dir/gate_closed.png) | gate closed | |
| ![](hungry_homer/resources_dir/gate_opened.png) | gate opened | go through it to complete the level |


Technical documentation
-----------------------

See docstrings of individual classes and their methods and [Czech documentation](dokumentace.md) for a few details.


Known bugs
----------

 * pausing the game doesn't pause scheduled functions such as stopping Homer's invincibility
 * player's image orientation doesn't change when trying to move into a wall (this manifests only in a corner)

