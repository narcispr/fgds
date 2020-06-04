# FG Digital Sheets
FG Digital Sheets (Fantasy Games Digital Sheets) is an open source (GPLv3) web based app that can be used as a companion APP to play games similar to Frostgrave.
It allows to create a list with all the warbands (and monsters) that will play a scenario as well as to calculate the result of hand-to-hand attacks, shoots, spell casts, ...

The application has been developed in Python 3 using Flask.

## Installation
FG Digital Sheets has few dependences. Check that you have all of them installed to run it. Using a python virtual environment can be a good idea.

* Python 3
* Flask (`pip install flask`)
* Sqlite 3 (`pip install pysqlite3 `)
* Werkzeug (`pip install -U Werkzeug`)
* pathlib (`pip install pathlib`)

Clone this repository and run the main file.

```bash
$ cd PATH_TO_REPOSITORY
$ export FLASK_APP=fgds.py 
$ flask run
```

Open a browser at `http://127.0.0.1:5000/` the web app should appear.

## How To use it
There are only 2 pages `Main` and `Random`.

### Main
From main you can select which *list* you want to use. 
There is an special list called `encounter_list` where you can define all the *monsters* that can appear randomly during a scenario. At least another list with all the player warbands and the initial monsters in the scenario must be defined.
To add a new *mini* to any list just press `Add new mini` and follow the instructions.

Once all the minis are defined and put in a single list the scenario can start.
Each mini has a menu with the following entries:
* Fight: Choose with witch *mini* you want to fight hand-to-hand or who you want to shoot. Edit the modifiers if necessaries and once ready push the *fight*/*shoot* button. All the calculations are shown. You can modify the damage (if any) and apply it or not.
* Spells: If the *mini* has any spells associated, you can see them and try to cast them.
* Resist: Allows to do a *resist* roll.
* Edit: Edit any *mini* parameters.
* Copy: Adds a new *mini* with the same parameters.
* Remove: Remove the *mini*.

### Random
From this page the following actions can be done:
* Roll a dice (d2, d6, d20, dN).
* Check initiative.
* Choose a random course for a monster.
* Roll a dice on the `encounter_list`. All the entries with the number rolled will be shown and can be added to the current active list. 

## Things to take into account.

* This is a very preliminary implementation with bugs and incomplete features. Any one is welcome to collaborate or to adapt it to any similar game. You can add issues with all the things that are not working, features you will like to see, etc.
* Because all players and monsters share the same list it is a good practice to start each *mini* name as *PN:* where *N* is the player number or *M:* for the automatically controlled monsters.
* When you add a new *mini* in the `encounter_list` an `Encounter Roll` number is asked. If two creatures have the same `Enconunter Roll` it means that they will appear toguether. In the *Random* page, the algorithm check the maximum `Encounter Roll` value in the `encounter_list` and rolls a number between 1 and this. If there are numbers no associated to *minis* is it possible that no *minis* will be selected.
* Before adding a *mini* from the `encounter_list` to the *active list* it is convinient to chnage its name.
* If some spell effect, special item, whatever, modifies a *mini* attribute, just edit the mini with the new value.
* You can move a *mini* from one list to another just editing their *list* value.
* When the *health* of a mini is 0, the mini is not shown when its list is visualized. To see it, (e.g., to change its *health*) you have to select the list named as *All*.

## Disclaimer
This is not a game, just a companion app to make things easier (or at least to try it!). It does not substitutes any rule book. In fact, only very basic rules are incorporated as equations but no tables with spells, soldiers features, creatures, ...

I have no other relation with Osprey or Joseph A. McCullough than being a fan of their games. I don't think I'm violating any copyright. However, If I'm, please contact me and we'll work it out!
