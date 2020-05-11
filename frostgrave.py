#!/usr/bin/env python3

from flask import Flask, g, session, render_template, abort, request, flash, redirect, url_for
# from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import datetime
from random import randrange

app = Flask(__name__)
app.config.from_object(__name__)

USER_ID = 'narcispr'
COMBAT_LIST = 'initial'


mini_fields = ['rowid', 'type', 'name', 'list', 'user', 'M', 'F', 'S', 'A', 'W', 'H', 
               'cwp_name', 'cwp_damage_mod', 'cwp_armour_mod', 'swp_name', 'swp_range', 'swp_damage_mod']
spell_fields = ['rowid', 'mini_id', 'name', 'cast_value', 'description']

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

def get_members(list):
    db = get_db()
    cur = db.execute("SELECT rowid, * FROM minis WHERE user=\"{}\" AND list=\"{}\" AND H > 0".format(USER_ID, list))
    return cur.fetchall()

def get_stats(id):
    db = get_db()
    cur = db.execute("SELECT rowid, * FROM minis WHERE rowid={} AND user=\"{}\"".format(id, USER_ID))
    
    # col_name_list = [t[0] for t in cur.description]
    # print(col_name_list)
    
    stats = cur.fetchall()
    if len(stats) == 1:
        return stats[0]
    else:
        print("Error retrieving min stats for id={} and user=\"{}\"".format(id, USER_ID))
        return None

@app.route('/fight_select/<int:mini>')
def fight_select(mini):
    team = get_members(COMBAT_LIST)
    m = get_stats(mini)
    return render_template('select_minis.html', mini=m, team=team)

@app.route('/')
def show():
    db = get_db()
    cur = db.execute("SELECT rowid, * FROM minis WHERE user=\"{}\" ".format(USER_ID))
    minis = cur.fetchall()
    return render_template('show_minis.html', minis=minis)

@app.route('/fight/', methods=['POST'])
def fight():
    s1 = get_stats(request.form.get('mini1'))
    s2 = get_stats(request.form.get('mini2'))
        
    combat_type = request.form.get('fight') == 'combat'
    msg = ''
    if not combat_type and s1[mini_fields.index('swp_range')] <= 0:
        msg = 'Mini {} has no weapon suitable for shooting'.format(s1[mini_fields.index('ńame')])
    
    return render_template('fight.html', s1=s1, s2=s2, combat_type=combat_type, msg=msg)
    
@app.route('/shoot/', methods=['POST'])
def shoot():
    s1 = get_stats(request.form['mini1'])
    s2 = get_stats(request.form['mini2'])
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
    
    health = int(s2[mini_fields.index('H')])
    new_health = max(health - damage, 0)
    
    return render_template('shoot_results.html', s1=s1, s2=s2, s_dice=s_dice, t_dice=t_dice, s_mod=s_mod, t_mod=t_mod, damage=damage,
                           health=health, new_health=new_health, w_mod=int(request.form.get('w1_m')), armour=int(request.form.get('armour')))

@app.route('/combat/', methods=['POST'])
def combat():
    s1 = get_stats(request.form.get('mini1'))
    s2 = get_stats(request.form.get('mini2'))
    p1_dice = randrange(20) + 1
    p2_dice = randrange(20) + 1
    
    sup1 = max(int(request.form.get('sup1')) - int(request.form.get('sup2')), 0) * 2
    sup2 = max(int(request.form.get('sup2')) - int(request.form.get('sup1')), 0) * 2
    p1_mod = int(request.form.get('F1')) + sup1
    p2_mod = int(request.form.get('F2')) + sup2

    damage1 = 0
    damage2 = 0
    winner = 0
    if (p1_dice + p1_mod) > (p2_dice + p2_mod):
        damage2 = max(p1_dice + p1_mod + int(request.form.get('wp1')) - int(request.form.get('a2')), 0)
        winner = 1
    elif (p1_dice + p1_mod) < (p2_dice + p2_mod):
        damage1 = max(p2_dice + p2_mod + int(request.form.get('wp2')) - int(request.form.get('a1')), 0)
        winner = 2
    else:
        damage2 = max(p1_dice + p1_mod + int(request.form.get('wp1')) - int(request.form.get('a2')), 0)
        damage1 = max(p2_dice + p2_mod + int(request.form.get('wp2')) - int(request.form.get('a1')), 0)
    
    health1 = int(s1[mini_fields.index('H')])
    health2 = int(s2[mini_fields.index('H')])
    new_health1 = max(health1 - damage1, 0)
    new_health2 = max(health2 - damage2, 0)
    
    return render_template('combat_results.html', s1=s1, s2=s2, p1_dice=p1_dice, p2_dice=p2_dice, p1_mod=p1_mod, p2_mod=p2_mod, 
                           damage1=damage1, damage2=damage2, wp1=int(request.form.get('wp1')), wp2=int(request.form.get('wp2')),
                           a1=int(request.form.get('a1')), a2=int(request.form.get('a2')), winner=winner,
                           health1=health1, new_health1=new_health1, health2=health2, new_health2=new_health2)



def update_health(mini, new_health):
    db = get_db()
    db.execute("UPDATE minis SET H = {} WHERE rowid = {} AND user = \"{}\"".format(new_health, mini, USER_ID))
    db.commit()
    
@app.route('/apply_new_health/', methods=['POST'])
def apply_new_health():
    use_mini1 = request.form.get('use_mini1')
    if use_mini1 == '1':
        mini1 = request.form.get('mini1')
        health1 = request.form.get('health1')
        update_health(int(mini1), max(int(health1), 0))
    
    use_mini2 = request.form.get('use_mini2')
    if use_mini2 == '1':
        mini2 = request.form.get('mini2')
        health2 = request.form.get('health2')
        update_health(int(mini2), max(int(health2), 0))
    
    return redirect(url_for('show'))


@app.route('/delete_mini/<int:mini>')
def delete_mini(mini):
    db = get_db()
    db.execute("DELETE FROM minis WHERE rowid = {} AND USER = \"{}\"".format(mini, USER_ID))
    db.commit()
    return redirect(url_for('show'))


@app.route('/add_mini/')
def add_mini():
    return render_template('add_mini.html')

@app.route('/edit_mini/<int:mini>')
def edit_mini(mini):
    mini = get_stats(mini)
    return render_template('edit_mini.html', mini=mini)

@app.route('/add/', methods=['POST'])
def add():
    a = request.form.get('add') == "1"
    print("Add: {}".format(a))
    t = request.form.get('type')
    name = request.form.get('name')
    l = request.form.get('list')
    M = int(request.form.get('M'))
    F = int(request.form.get('F'))
    S = int(request.form.get('S'))
    A = int(request.form.get('A'))
    W = int(request.form.get('W'))
    H = int(request.form.get('H'))
    cwp_name = request.form.get('cwp_name')
    cwp_damage_mod = int(request.form.get('cwp_damage_mod'))
    cwp_armour_mod = int(request.form.get('cwp_armour_mod'))
    swp_name = request.form.get('swp_name')
    swp_range = int(request.form.get('swp_range'))
    swp_damage_mod = int(request.form.get('swp_damage_mod'))
    if a:
        command = "INSERT INTO minis (type, name, list, user, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod) VALUES ({}, \"{}\", \"{}\", \"{}\", {}, {}, {}, {}, {}, {}, \"{}\", {}, {}, \"{}\", {}, {})".format(t, name, l, USER_ID, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod)
    else:
        id = int(request.form.get('id'))
        command = "UPDATE minis SET type={}, name=\"{}\", list=\"{}\", user=\"{}\", M={}, F={}, S={}, A={}, W={}, H={}, cwp_name=\"{}\", cwp_damage_mod={}, cwp_armour_mod={}, swp_name=\"{}\", swp_range={}, swp_damage_mod={} WHERE rowid={}".format(t, name, l, USER_ID, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod, id)
    
    print(command)
    db = get_db()
    db.execute(command)
    db.commit()
    
    return redirect(url_for('show'))

@app.route('/show_spells/<int:mini>')
def show_spells(mini):
    db = get_db()
    command = "SELECT spells.rowid, * FROM spells WHERE mini_id={}".format(mini)
    cur = db.execute(command)
    spells = cur.fetchall()
    stats = get_stats(mini)
    return render_template('show_spells.html', mini=stats, spells=spells)

@app.route('/resist_spell/<int:mini>')
def resist_spell(mini):
    m = get_stats(mini)
    dice = randrange(20) + 1
    return render_template('resist_spell.html', mini=m, dice=dice)

@app.route('/resist_result/', methods=['POST'])
def resist_result():
    mini_id = int(request.form.get('mini'))
    m = get_stats(mini_id)
    empowering = int(request.form.get('empowering'))
    update_health(mini_id, m[mini_fields.index('H')] - empowering)
    return redirect(url_for('show'))

def get_spell(spell):
    db = get_db()
    cur = db.execute("SELECT rowid, * FROM spells WHERE rowid={}".format(spell))
    spell = cur.fetchall()
    if len(spell) == 1:
        return spell[0]
    else:
        print("Error retrieving spell for id={} and user=\"{}\"".format(spell, USER_ID))
        return None

@app.route('/remove_spell/<int:spell>')
def remove_spell(spell):
    s = get_spell(spell)
    mini_id = s[spell_fields.index('mini_id')]
    db = get_db()
    command = "DELETE FROM spells WHERE rowid = {}".format(spell)
    print(command)
    db.execute(command)
    db.commit()
    return redirect(url_for('show_spells', mini=mini_id))

@app.route('/cast_spell/<int:spell>')
def cast_spell(spell):
    s = get_spell(spell)
    m = get_stats(s[spell_fields.index('mini_id')])
    dice = randrange(20) + 1
    diff = s[spell_fields.index('cast_value')] - dice
    cast = False
    if diff <= 0:
        cast = True
    damage = 0
    if not cast:
        if diff > 4 and diff <= 9:
            damage = 1
        elif diff > 9 and diff <= 19:
            damage = 2
        elif diff > 20:
            damage = 5
    print("Dice: {}, Cast: {}, damage: {}".format(dice, cast, damage))
    return render_template('cast_results.html', spell=s, mini=m, dice=dice, cast=cast, damage=damage)

@app.route('/add_spell/<int:mini>')
def add_spell(mini):
    m = get_stats(mini)
    return render_template('add_spell.html', mini=m)

@app.route('/add_spell_to_mini/', methods=['POST'])
def add_spell_to_mini():
    mini_id = int(request.form.get('mini'))
    m = get_stats(mini_id)
    a = request.form.get('add') == '1'
    name = request.form.get('name')
    cost = int(request.form.get('cost'))
    description = request.form.get('description')
    if a:
        command = "INSERT INTO spells (mini_id, name, cast_value, description) VALUES ({}, \"{}\", {}, \"{}\")".format(mini_id, name, cost, description)
    else:
        spell_id = int(request.form.get('id'))
        command = "UPDATE spells SET mini_id={}, name=\"{}\", cast_value={}, description=\"{}\" WHERE rowid = {}".format(mini_id, name, cost, description, spell_id)
    
    print(command)
    db = get_db()
    db.execute(command)
    db.commit()
    command = "SELECT spells.rowid, * FROM spells WHERE mini_id={}".format(mini_id)
    cur = db.execute(command)
    spells = cur.fetchall()
    return render_template('show_spells.html', mini=m, spells=spells)

@app.route('/empowering_spell/', methods=['POST'])
def empowering_spell():
    spell_id = int(request.form.get('spell'))
    empowering = int(request.form.get('empowering'))
    dice = int(request.form.get('dice'))
    s = get_spell(spell_id)
    mini_id = s[spell_fields.index('mini_id')]
    m = get_stats(mini_id)

    diff = s[spell_fields.index('cast_value')] - dice - empowering
    cast = False
    if diff <= 0:
        cast = True
    damage = empowering
    if not cast:
        if diff > 4 and diff <= 9:
            damage += 1
        elif diff > 9 and diff <= 19:
            damage += 2
        elif diff > 20:
            damage += 5
    print("Dice: {}, Cast: {}, Empowering: {}, damage: {}".format(dice, cast, empowering, damage))
    return render_template('cast_empowered.html', spell=s, mini=m, dice=dice, cast=cast, damage=damage, empowering=empowering)

@app.route('/edit_spell/<int:spell>')
def edit_spell(spell):
    s = get_spell(spell)
    m = get_stats(s[spell_fields.index('mini_id')])
    return render_template('edit_spell.html', mini=m, spell=s)

@app.route('/copy_mini/<int:mini>')
def copy_mini(mini):
    m = get_stats(mini)
    for i in m:
        print(i)
    command = "INSERT INTO minis (type, name, list, user, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod) VALUES ({}, \"{}_copy\", \"{}\", \"{}\", {}, {}, {}, {}, {}, {}, \"{}\", {}, {}, \"{}\", {}, {})".format(m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], m[12], m[13], m[14], m[15], m[16])
    print(command)
    db = get_db()
    db.execute(command)
    db.commit()    
    return redirect(url_for('show'))

@app.route('/random/')
def random():
    return render_template('random.html')


if __name__ == '__main__':
    app.run()
