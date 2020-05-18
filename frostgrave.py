#!/usr/bin/env python3

from flask import Flask, g, session, render_template, abort, request, flash, redirect, url_for
# from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import random
from werkzeug.utils import secure_filename
from pathlib import Path


UPLOAD_FOLDER = 'static/images'
SHORT_UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg'}


app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.globals.update(zip=zip)

USER_ID = 'narcispr'
COMBAT_LIST = 'initial'
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

mini_fields = ['rowid', 'type', 'name', 'list', 'user', 'M', 'F', 'S', 'A', 'W', 'H',
               'cwp_name', 'cwp_damage_mod', 'cwp_armour_mod', 'swp_name', 'swp_range', 'swp_damage_mod', 'encounter_value']
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

def get_members(list=None):
    db = get_db()
    if list is None:
        cur = db.execute("SELECT rowid, * FROM minis WHERE user=\"{}\" AND H > 0 ORDER BY name".format(USER_ID))
    else:
        cur = db.execute("SELECT rowid, * FROM minis WHERE user=\"{}\" AND list=\"{}\" AND H > 0 ORDER BY name".format(USER_ID, list))
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
    if 'list_name' in session:
        team = get_members(session['list_name'])
    else:
        team = get_members()
    m = get_stats(mini)
    return render_template('select_minis.html', mini=m, team=team)

@app.route('/', methods=['POST'])
def show_post(list_name=None):
    list_n = request.form.get('list_n')
    if list_n == '__all__':
        try:
            del session['list_name']
        except:
            pass
    else:
        session['list_name'] = list_n
    return redirect(url_for('show'))

@app.route('/')
def show(list_name=None):
    db = get_db()
    cur = db.execute("SELECT list FROM minis WHERE user=\"{}\" ORDER BY name".format(USER_ID)).fetchall()
    list_names = set()
    for l in cur:
        list_names.add(l[0])
    if not 'list_name' in session:
        cur = db.execute("SELECT rowid, * FROM minis WHERE user=\"{}\" ORDER BY name".format(USER_ID))
        active_list = None
    else:
        cur = db.execute("SELECT rowid, * FROM minis WHERE H > 0 AND user=\"{}\" AND list=\"{}\" ORDER BY name".format(USER_ID, session['list_name']))
        active_list = session['list_name']
    minis = cur.fetchall()

    figs_path = list()
    for m in minis:
        if os.path.exists(os.path.join(UPLOAD_FOLDER, "mini_fig_{}.png".format(m[0]))):
            figs_path.append(os.path.join(SHORT_UPLOAD_FOLDER, "mini_fig_{}.png".format(m[0])))
        elif os.path.exists(os.path.join(UPLOAD_FOLDER, "mini_fig_{}.jpg".format(m[0]))):
            figs_path.append(os.path.join(SHORT_UPLOAD_FOLDER, "mini_fig_{}.jpg".format(m[0])))
        elif m[mini_fields.index('type')] == 0:
            figs_path.append("static/wizard.png")
        elif m[mini_fields.index('type')] == 1:
            figs_path.append("static/apprentice.png")
        elif m[mini_fields.index('type')] == 2:
            figs_path.append("static/soldier.png")
        elif m[mini_fields.index('type')] == 3:
            figs_path.append("static/monster.png")
        else:
            figs_path.append("")
    return render_template('show_minis.html', minis=minis, list_names=list_names, active_list=active_list, figs_path=figs_path)

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
    s_dice = random.randrange(20) + 1
    t_dice = random.randrange(20) + 1

    s_mod = int(request.form['S'])

    cover = int(request.form.get('cover'))
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
    p1_dice = random.randrange(20) + 1
    p2_dice = random.randrange(20) + 1

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
    db.execute("DELETE FROM spells WHERE mini_id = {}".format(mini))
    db.commit()
    path = os.path.join(app.config['UPLOAD_FOLDER'], "mini_fig_{}.png".format(mini))
    if os.path.exists(path):
        os.remove(path)
    path = os.path.join(app.config['UPLOAD_FOLDER'], "mini_fig_{}.jpg".format(mini))
    if os.path.exists(path):
        os.remove(path)
    
    return redirect(url_for('show'))


@app.route('/add_mini/')
def add_mini():
    if 'list_name' in session:
        return render_template('add_mini.html', default_list=session['list_name'])
    else:
        return render_template('add_mini.html', default_list="")

@app.route('/edit_mini/<int:mini>')
def edit_mini(mini):
    mini = get_stats(mini)
    return render_template('edit_mini.html', mini=mini)

@app.route('/add/', methods=['POST'])
def add():
    a = request.form.get('add') == "1"
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
    encounter = int(request.form.get('encounter'))
    rowid = -1

    if a:
        command = "INSERT INTO minis (type, name, list, user, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod, encounter_value) VALUES ({}, \"{}\", \"{}\", \"{}\", {}, {}, {}, {}, {}, {}, \"{}\", {}, {}, \"{}\", {}, {}, {})".format(t, name, l, USER_ID, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod, encounter)
        db = get_db()
        cur = db.execute(command)
        db.commit()
        rowid = cur.lastrowid
    else:
        id = int(request.form.get('id'))
        command = "UPDATE minis SET type={}, name=\"{}\", list=\"{}\", user=\"{}\", M={}, F={}, S={}, A={}, W={}, H={}, cwp_name=\"{}\", cwp_damage_mod={}, cwp_armour_mod={}, swp_name=\"{}\", swp_range={}, swp_damage_mod={}, encounter_value={} WHERE rowid={}".format(t, name, l, USER_ID, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod, encounter, id)
        db = get_db()
        db.execute(command)
        db.commit()
        rowid = id

    if 'file' not in request.files:
        print('No file part')
    else:
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], "mini_fig_{}.{}".format(rowid, filename[-3:]))
            file.save(path)
            size = os.stat(path).st_size
            if size > 512000:
                print("Remove file {}. Too big ({})".format(path, size))
                os.remove(path)

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
    dice = random.randrange(20) + 1
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
    db.execute(command)
    db.commit()
    return redirect(url_for('show_spells', mini=mini_id))

@app.route('/cast_spell/<int:spell>')
def cast_spell(spell):
    s = get_spell(spell)
    m = get_stats(s[spell_fields.index('mini_id')])
    dice = random.randrange(20) + 1
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
    return render_template('cast_results.html', spell=s, mini=m, dice=dice, cast=cast, damage=damage)

@app.route('/add_spell/', methods=['POST'])
def add_spell():
    m = get_stats(request.form.get('mini1'))
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
    return render_template('cast_empowered.html', spell=s, mini=m, dice=dice, cast=cast, damage=damage, empowering=empowering)

@app.route('/edit_spell/<int:spell>')
def edit_spell(spell):
    s = get_spell(spell)
    m = get_stats(s[spell_fields.index('mini_id')])
    return render_template('edit_spell.html', mini=m, spell=s)

@app.route('/copy_mini/<int:mini>')
def copy_mini(mini):
    m = get_stats(mini)
    command = "INSERT INTO minis (type, name, list, user, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod) VALUES ({}, \"{}_copy\", \"{}\", \"{}\", {}, {}, {}, {}, {}, {}, \"{}\", {}, {}, \"{}\", {}, {})".format(m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], m[12], m[13], m[14], m[15], m[16])
    db = get_db()
    db.execute(command)
    db.commit()
    return redirect(url_for('show'))

@app.route('/random/')
def random_events():
    db = get_db()
    command = "SELECT rowid, * FROM minis WHERE list=\"encounter_list\""
    cur = db.execute(command).fetchall()
    rolls = set()
    for i in cur:
        rolls.add(i[mini_fields.index('encounter_value')])
    cur = list()
    if len(list(rolls)) > 0:
        encounter = random.choice(list(rolls))
        command = "SELECT rowid, * FROM minis WHERE list=\"encounter_list\" AND encounter_value={}".format(encounter)
        cur = db.execute(command).fetchall()
    active_list = "All"
    if 'list_name' in session:
        active_list = session['list_name']

    return render_template('random.html', encounter=cur, active_list=active_list)

@app.route('/add_mini_to/', methods=['POST'])
def add_mini_to():
    mini = int(request.form.get('mini_id'))
    name = request.form.get('name')
    s = get_stats(mini)
    list_name = "All"
    if 'list_name' in session:
        list_name = session['list_name']
    command = "INSERT INTO minis (type, name, list, user, M, F, S, A, W, H, cwp_name, cwp_damage_mod, cwp_armour_mod, swp_name, swp_range, swp_damage_mod, encounter_value) VALUES ({}, \"{}\", \"{}\", \"{}\", {}, {}, {}, {}, {}, {}, \"{}\", {}, {}, \"{}\", {}, {}, {})".format(s[1], name, list_name, s[4], s[5], s[6], s[7], s[8], s[9], s[10], s[11], s[12], s[13], s[14], s[15], s[16], 0)
    db = get_db()
    db.execute(command)
    db.commit()

    return render_template('empty.html', name=name, list_name=list_name)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run()
