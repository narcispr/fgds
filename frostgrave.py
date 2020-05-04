#!/usr/bin/env python3

from flask import Flask, g, session, render_template, abort, request, flash, redirect, url_for
# from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import datetime
from random import randrange

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'frostgrave.db'),
    SECRET_KEY='secret_key',
    USERNAME='admin',
    PASSWORD='1234'
))
app.config.from_envvar('ORGANIZE_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    if error is not None:
        print( "An error has been produced.")


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_members(team):
    db = get_db()
    cur = db.execute("SELECT * FROM minis WHERE team = {}".format(team))
    return cur.fetchall()

def get_stats(id):
    db = get_db()
    stats = None
    combat_weapon = None
    shoot_weapon = None
    cur = db.execute("SELECT * FROM minis WHERE id = {}".format(id))
    stats = cur.fetchall()[0]
    if stats[7] != 0: # combat weapon 
        cur = db.execute("SELECT * FROM weapons WHERE rowid = {}".format(stats[7]))
        combat_weapon = cur.fetchall()[0]
    if stats[8] != 0: # shoot weapon 
        cur = db.execute("SELECT * FROM weapons WHERE rowid = {}".format(stats[8]))
        shoot_weapon = cur.fetchall()[0]
    return stats, combat_weapon, shoot_weapon

@app.route('/')
def hello():
    minis_1 = get_members(1)
    minis_2 = get_members(2)
    return render_template('select_minis.html', team1=minis_1, team2=minis_2)
    
    
@app.route('/fight/', methods=['POST'])
def fight():
    s1, cw1, sw1 = get_stats(request.form['mini1'])
    s2, cw2, sw2 = get_stats(request.form['mini2'])
    combat_type = request.form['fight'] == 'combat'
    msg = ''
    if not combat_type and sw1 is None:
        msg = 'Mini {} has no weapon suitable for shooting'.format(s1[1])
    return render_template('fight.html', s1=s1, cw1=cw1, sw1=sw1, s2=s2, cw2=cw2, sw2=sw2, combat_type=combat_type, msg=msg)
    
@app.route('/shoot/', methods=['POST'])
def shoot():
    s1, _, _ = get_stats(request.form['mini1'])
    s2, _, _ = get_stats(request.form['mini2'])
    s_dice = randrange(20) + 1
    t_dice = randrange(20) + 1
    
    s_mod = int(request.form['S'])
    
    cover = 0
    if request.form.get('cover') == 'l_cover':
        cover = 2
    elif request.form.get('cover') == 'h_cover':
        cover = 4
    hasty = 0
    if request.form.get('hasty') == 'hasty':
        hasty = 1
    
    large = 0
    if request.form.get('large') == 'large':
        large = -2
    
    t_mod = int(request.form.get('F')) + int(request.form.get('IT')) + cover + hasty + large
    
    damage = 0
    if (s_dice + s_mod) > (t_dice + t_mod):
        d_total = s_dice + s_mod + int(request.form.get('w1_m'))
        a_total = int(request.form.get('armour'))
        damage = max(d_total - a_total, 0)
    
    health = int(s2[11])
    new_health = max(health - damage, 0)
    kill = (new_health <= 0)
    
    return render_template('combat_results.html', s1=s1[1], s2=s2[1], s_dice=s_dice, t_dice=t_dice, s_mod=s_mod, t_mod=t_mod, damage=damage,
                           health=health, new_health=new_health, w_mod=int(request.form.get('w1_m')), armour=int(request.form.get('armour')))


if __name__ == '__main__':
    app.run()
