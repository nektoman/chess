from flask import session
from flask_socketio import leave_room, send, emit, join_room

from .. import socketio
from . import rooms
from ..chess_game import coord_to_chess, coord_from_chess


def update_lobby_list():
    rooms_spectate = [{'room': key,
                       'players': [{'name': key} for key, value in value.players.items()]} for key, value in
                      rooms.items() if len(value.players) == 2]
    emit('update_lobby_list',
         {'rooms_join': [{'room': key,
                          'creator': value.creator} for key, value in rooms.items() if len(value.players) < 2],
          'rooms_spectate': rooms_spectate
          },
         namespace='/lobby',
         broadcast=True)


@socketio.on('connect', namespace='/lobby')
def lobby_connect(auth):
    update_lobby_list()


@socketio.on('disconnect', namespace='/lobby')
def lobby_disconnect():
    pass


@socketio.on('connect', namespace='/chess')
def chess_connect():
    room = session['room']
    if not session['spectator']:
        rooms[room].players.update({session['name']: {}})
    else:
        rooms[room].spectators.update({session['name']: {}})
    join_room(room)
    send(f'{session["name"]} connected', room=room)
    update_lobby_list()


@socketio.on('disconnect', namespace='/chess')
def chess_disconnect():
    room = session.get('room')
    leave_room(room)
    send(f'{session.get("name")} disconnected', room=room)
    update_lobby_list()


@socketio.on('move_to', namespace='/chess')
def move_to(move):
    board = rooms[session.get('room')].game.board
    figure = board.get_square(coord_from_chess(move['x_from'], move['y_from']))
    board.move(figure, coord_from_chess(move['x_to'], move['y_to']))
    set_figures()


@socketio.on('get_pointers', namespace='/chess')
def set_pointers(coord):
    room = session['room']
    moves = rooms[room].game.board.get_square(coord_from_chess(coord['x'], coord['y'])).get_available_moves()
    coords = [coord_to_chess(move) for move in moves]
    pointers = [{'x': coordinate[0], 'y': coordinate[1]} for coordinate in coords]
    emit('set_pointers',
         {'pointers': pointers})


@socketio.on('get_figures', namespace='/chess')
def set_figures():
    room = session['room']
    figures = rooms[room].game.board.get_figures()
    json_figures = {'figures':[ {'x': figure.get_chess_x(), 'y': figure.get_chess_y(), 'name': figure.name } for figure in figures ]}
    emit('set_figures', json_figures, room=session.get('room'))
