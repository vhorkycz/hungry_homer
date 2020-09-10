Dokumentace Hladového Homéra
============================


Kreslicí knihovna
-----------------

Pro kreslení používám knihovnu [pyglet](https://pypi.org/project/pyglet/)
([dokumentace](https://pyglet.readthedocs.io/en/latest/)).
Dočetl jsem se, že je [prý](https://steveasleep.com/pyglettutorial.html) rychlejší a přehlednější
než [Pygame](https://pypi.org/project/pygame/), nejrozšířenější knihovna pro vytváření grafických her v Pythonu,
ale žádné pořádné srovnání jsem nenašel
a sám jsem Pygame nezkoušel, takže to nedovedu posoudit.
Zato jsem několikrát narazil na jednu nevýhodu Pygletu,
a to že se málo používá a je o něm málo informací.

Pro pohyb a srážky předmětů jsem možná mohl využít [Pymunk](https://pypi.org/project/pymunk/),
místo toho, abych to flikoval sám (viz níže), ale nezkoušel jsem ho.


Vytvoření úrovně
----------------

Předměty úrovně se vytvářejí podle mapy úrovně v textovém souboru, např.:

```
XXX/XXXXXXXXXXX
X   l         X
X   b      *  X
X X        <  X
X*X *     *   X
XXXXXXXX      X
X             X
X *      L    X
X     XXXXXXXXX
X     *  X   _X
X        X    X
X     ^  X *  X
X H      X    X
X     *       X
XXXXXXXXXXXXXXX
```

Každý znak představuje jeden bod mřížky stejně veliké jako každý předmět (20 na 20 px).

| znak(y) | obrázek | předmět | poznámka |
| --- | --- | --- | --- |
| `H` | ![](hungry_homer/resources_dir/homer_up.png) | Homér | |
| `urdlURDL` | ![](hungry_homer/resources_dir/circular_watcher_up.png) | okružní hlídač | první, resp. druhé čtyři znaky představují hlídače majícího zeď po pravé, resp. levé straně a mířícího po řadě nahoru, doprava, dolů, doleva |
| `^>v<` | ![](hungry_homer/resources_dir/linear_watcher_up.png) | přímkový hlídač | mířící po řadě nahoru, doprava, dolů, doleva |
| `X` | ![](hungry_homer/resources_dir/brick.png) | cihla | |
| `*` | ![](hungry_homer/resources_dir/food.png) | jídlo | |
| `b` | ![](hungry_homer/resources_dir/bell_silent.png) | zvon | |
| `_` | ![](hungry_homer/resources_dir/key.png) | klíč | |
| `/` | ![](hungry_homer/resources_dir/gate_closed.png) ![](hungry_homer/resources_dir/gate_opened.png) | brána (zavřená/otevřená) | |


Pohyb předmětů
--------------

Pohyblivé předměty, tj. hráč (Homér) a hlídači, se pohybují po mřížce,
jejíž body jsou stejně velké jako předměty,
a smějí se zastavit jenom v nich a jenom v nich se také mohou otočit (ze svého pohledu) na stranu
(dozadu se mohou otočit kdykoliv; o jiný úhel se otočit nesmějí).
(Nejjednodušší by bylo, aby se předměty vždycky posunuly o celou svou velikost, tj. o 20 px --
ale to by vypadlo ohavně; proto se při každém překreslení pohnou předměty jen o 2 px.)

Když na sebe narazí hlídači, obrátí se (okružní změní stranu, po které má zeď, přímkový se otočí dozadu);
když na sebe narazí Homér a hlídač, poprvé dostane varování, aby neloupal perníček, a podruhé prohraje
(ale jednou může zazvonit na zvonek a pak se mu na chvíli nic nestane).
Tyto srážky se zjišťují tak, že se pohyblivé předměty pořád (při každém překreslení) navzájem ptají,
jestli do sebe vrazily (tj. jestli vzdálenost jejich dolních levých rohů je rovná jejich velikosti nebo menší),
a podle toho jednají.
Pro každý předmět to tedy má lineární časovou složitost (dohromady tedy kvadratickou) --
ale pohyblivých předmětů je celkem málo, a kdyby se srážky měly zjišťovat z mapy, bylo by to zbytečně složité.

Ale z mapy předměty zjišťují to, jestli nechtějí projít zdí:
když jsou v bodě mřížky, spočítají, do kterého bodu míří,
a zjistí, jestli je v něm v mapě znak pro cihlu (nebo dveře)
-- to má tedy pro každý předmět konstantní časovou složitost a to je výhodné,
protože cihel je celkem dost a nehýbou se (a jsou vždycky přesně v bodě mřížky).


Mizení předmětů
---------------

Zmizet ze hry může jen jídlo nebo klíč, a to když je Homér úplně překryje
(tj. když se rovnají jejich dolní levé rohy).

U konkurence může hráč zacinkat zvonkem a jíst hlídače, ale to je ošklivé,
takže to tady není možné, a místo toho hráči jenom na chvíli nic nehrozí,
protože se hlídači kochají tou krásou;
jinak by se ale jejich mizení v zásadě nijak nelišilo.

