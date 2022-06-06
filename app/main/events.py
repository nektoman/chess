from flask import session
from flask_socketio import leave_room, send, emit, join_room

from .. import socketio
from . import rooms
from ..Chess.chess import coord_to_chess, coord_from_chess


def update_lobby_list():
    rooms_spectate =[{'room': key,
                      'players': [{'name': key} for key,value in value.players.items() ] } for key, value in rooms.items() if len(value.players) == 2]
    emit('update_lobby_list',
         {'rooms_join': [{'room': key,
                          'creator': value.creator } for key, value in rooms.items() if len(value.players) < 2],
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
    if session['spectator'] == False:
        rooms[room].players.update({session.get('name'): {}})
    else:
        rooms[room].spectators.update({session.get('name'): {}})
    join_room(room)
    send(f'{session.get("name")} connected', room=room)
    update_lobby_list()

@socketio.on('disconnect', namespace='/chess')
def chess_disconnect():
    room = session.get('room')
    leave_room(room)
    send(f'{session.get("name")} disconnected', room=room)
    update_lobby_list()

@socketio.on('move_to', namespace='/chess')
def move_to(move_to):
    figures = rooms[session.get('room')].board.get_figures()
    # figures[move_to.get('id')]['x'] = move_to.get('x') todo
    # figures[move_to.get('id')]['y'] = move_to.get('y')
    set_figures()

@socketio.on('get_pointers', namespace='/chess')
def set_pointers(figure_x, figure_y):
    moves = rooms[session.get('room')].board.get_square(coord_from_chess(figure_x, figure_y)).get_avaibale_moves()
    coords = [coord_to_chess(move) for move in moves]
    pointers = [{'x': coord.x, 'y': coord.y} for coord in coords]
    emit('set_pointers',
         {'pointers': pointers })

@socketio.on('get_figures', namespace='/chess')
def set_figures():
    figures = rooms[session.get('room')].board.get_figures()
    # json_figures = {'figures':[ {'id':key, todo
    #                              'x': value.get('x'),
    #                              'y': value.get('y'),
    #                              'figure_name': value.get('figure_name') } for key,value in figures.items() ]}
    # emit('set_figures', json_figures, room=session.get('room'))