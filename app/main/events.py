from flask import session
from flask_socketio import leave_room, send, emit, join_room

from .. import socketio
from . import rooms

def update_lobby_list():
    rooms_spectate =[{'room': key,
                      'players': [{'name': key} for key,value in value['players'].items() ] } for key, value in rooms.items() if len(value['players']) == 2]
    emit('update_lobby_list',
         {'rooms_join': [{'room': key,
                          'creator': value['creator'] } for key, value in rooms.items() if len(value['players']) < 2],
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
        rooms[room]['players'].update({session.get('name'): {}})
    else:
        rooms[room]['spectators'].update({session.get('name'): {}})
    print(rooms)
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
    figures = rooms[session.get('room')]['figures']
    figures[move_to.get('id')]['x'] = move_to.get('x')
    figures[move_to.get('id')]['y'] = move_to.get('y')
    set_figures()

@socketio.on('get_pointers', namespace='/chess')
def set_pointers(figure_id):
    emit('set_pointers',
             {'pointers': [
                 {'x':'A', 'y':'1'},
                 {'x':'A', 'y':'2'},
                 {'x':'A', 'y':'3'},
                 {'x':'A', 'y':'4'},
                 {'x':'A', 'y':'5'},
                 {'x':'B', 'y': '1'},
                 {'x':'B', 'y': '2'},
                 {'x':'B', 'y': '3'},
                 {'x':'B', 'y': '4'},
                 {'x':'B', 'y': '5'},
                 {'x':'C', 'y': '1'},
                 {'x':'C', 'y': '2'},
                 {'x':'C', 'y': '3'},
                 {'x':'C', 'y': '4'},
                 {'x':'C', 'y': '5'},
                 {'x': 'D', 'y': '1'},
                 {'x': 'D', 'y': '2'},
                 {'x': 'D', 'y': '3'},
                 {'x': 'D', 'y': '4'},
                 {'x': 'D', 'y': '5'},
                            ] })

@socketio.on('get_figures', namespace='/chess')
def set_figures():
    figures = rooms[session.get('room')]['figures']
    json_figures = {'figures':[ {'id':key,
                                 'x': value.get('x'),
                                 'y': value.get('y'),
                                 'figure_name': value.get('figure_name') } for key,value in figures.items() ]}
    emit('set_figures', json_figures, room=session.get('room'))