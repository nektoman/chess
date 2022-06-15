from flask import session
from flask_socketio import leave_room, send, emit, join_room

from .. import socketio
from . import rooms
from ..chess_game import coord_to_chess, coord_from_chess, create_game_room_if_init, Player


def update_lobby_list():
    rooms_spectate = [{'room': key,
                       'players': [{'name': player_name} for player_name, player in value.get_players().items()]} for key, value in rooms.items() ]
    emit('update_lobby_list',
         {'rooms_join': [{'room': key,
                          'creator': value.creator} for key, value in rooms.items() if value.have_empty_slot()],
          'rooms_spectate': rooms_spectate },
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
    create_game_room_if_init(rooms, session['room'], session['name'])
    if not session['spectator']:
        rooms[room].add_player(Player(session['name']))
    else:
        rooms[room].add_spectator(Player(session['name']))
    join_room(room)
    send(f'{session["name"]} connected', room=room)
    emit('set_team', {'team': rooms[room].get_user_by_name(session['name']).get_team()})
    update_lobby_list()
    set_figures()


@socketio.on('disconnect', namespace='/chess')
def chess_disconnect():
    room = session['room']
    leave_room(room)
    send(f"{session['name']} disconnected", room=room)
    update_lobby_list()


@socketio.on('move_to', namespace='/chess')
def move_to(move):
    game_room = rooms[session['room']]
    game_room.move(x_from=move['x_from'], y_from=move['y_from'], x_to=move['x_to'], y_to=move['y_to'])
    if not game_room.in_play():
        emit('game_result', {'result': game_room.get_game_result()})
    set_figures()


@socketio.on('get_pointers', namespace='/chess')
def set_pointers(coord):
    room = session['room']
    moves = rooms[room].get_legal_moves(coord_from_chess(coord['x'], coord['y']))
    coords = [coord_to_chess(move) for move in moves]
    pointers = [{'x': coordinate[0], 'y': coordinate[1]} for coordinate in coords]
    emit('set_pointers',
         {'pointers': pointers})


@socketio.on('get_figures', namespace='/chess')
def set_figures():
    room = session['room']
    figures = rooms[room].get_figures()
    json_figures = {'figures': [{'x': figure.get_chess_x(),
                                 'y': figure.get_chess_y(),
                                 'name': figure.get_name(),
                                 'team': figure.get_team()} for figure in figures],
                    'active_team': rooms[room].get_active_team()}
    emit('set_figures', json_figures, room=session.get('room'))
