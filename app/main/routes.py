from functools import wraps
from flask import render_template, url_for, session, redirect, request

from . import main, rooms
from .forms import LoginForm, CreateRoomForm
from ..chess_game import create_game_room_if_init


def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'name' not in session:
            return redirect(url_for('main.login'))
        else:
            return f(*args, **kwargs)
    return wrapped


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    message = 'Introduce yourself, please'
    if request.method == 'POST' and form.validate_on_submit():
        session['name'] = request.form.get('name')
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form, message=message)


@main.route('/', methods=['GET', 'POST'])
@authenticated_only
def index():
    form = CreateRoomForm()
    if form.validate_on_submit():
        session['room'] = form.room.data
        create_game_room_if_init(rooms, session['room'], session['name'])
        return redirect(url_for('main.chess'))
    return render_template('index.html', username=session['name'], form=form)


@main.route("/chess")
@authenticated_only
def chess():
    if request.args.get('room') != '' and request.args.get('room') is not None:
        session['room'] = request.args.get('room')
    if session['name'] == '' or session['room'] == '':
        return redirect(url_for('main.index'))
    create_game_room_if_init(rooms, session['room'], session['name'])
    if "spect" in request.args:
        session['spectator'] = True
    else:
        session['spectator'] = False
    return render_template('chess.html', name=session['name'], room=session['room'])
