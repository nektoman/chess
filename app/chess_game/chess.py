from string import ascii_uppercase
from random import shuffle


class Player:
    def __init__(self, name):
        self.__name = name
        self.__team = None
        self.__status = None

    def get_team(self):
        return self.__team

    def set_team(self, team):
        self.__team = team

    def get_name(self):
        return self.__name

    def get_status(self):
        return self.__status

    def set_status(self, status):
        self.__status = status


class Coordinate:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def __repr__(self):
        return f'X={self.x}, Y={self.y}'


class GameRoom:
    TEAM_BLACK = 'black'
    TEAM_WHITE = 'white'
    STALEMATE = 'stalemate'
    SPECTATOR = 'spectator'
    INITIAL = 'initial'
    IN_PLAY = 'in_play'

    def __init__(self, room_id, creator):
        self.__team_to_move = GameRoom.TEAM_WHITE
        self.id = room_id
        self.creator = creator
        self.__status = GameRoom.INITIAL
        self.__players = {}
        self.__users = {}
        self.__board = Board()
        self.init_figures()
        self.team_generator = GameRoom.__get_rand_team()
        self.__winner = ''

    def in_play(self):
        return self.__status == GameRoom.IN_PLAY

    def get_game_result(self):
        return self.__winner

    def add_player(self, player: Player):
        if self.have_empty_slot():
            player_name = player.get_name()
            if player_name not in self.__players:
                player.set_team(self.team_generator.__next__())
                self.__players.update({player_name: player})
                self.__users.update({player_name: player})
                if self.__status == GameRoom.INITIAL:
                    self.__status = GameRoom.IN_PLAY
                return True

    def get_players(self):
        return self.__players

    def get_user_by_name(self, name):
        return self.__users[name]

    def have_empty_slot(self):
        return len(self.__players) < 2

    def swap_active_team(self):
        if self.__team_to_move == GameRoom.TEAM_WHITE:
            self.__team_to_move = GameRoom.TEAM_BLACK
        else:
            self.__team_to_move = GameRoom.TEAM_WHITE

    def get_active_team(self):
        return self.__team_to_move

    def move(self, x_from, y_from, x_to, y_to):
        figure = self.__board.get_square(coord_from_chess(x_from, y_from))
        if figure is None:
            # todo
            return
        moved = self.__board.move(figure, coord_from_chess(x_to, y_to))
        if moved:
            self.swap_active_team()

        # Может ли продолжаться игра
        for figure in self.get_figures():
            if figure.get_team() == self.get_active_team() and figure.get_available_moves() is not None:
                return moved
        # Если дошли сюда то нет, осталось понять мат или пат, проверить под боем ли король
        king = self.__board.get_king(self.get_active_team())
        if king.under_attack():
            if self.__team_to_move == GameRoom.TEAM_WHITE:
                self.__winner = GameRoom.TEAM_BLACK
            else:
                self.__winner = GameRoom.TEAM_WHITE
        else:
            self.__winner = GameRoom.STALEMATE

    def get_legal_moves(self, coord: Coordinate):
        figure = self.__board.get_square(coord)
        if figure is not None:
            return figure.get_legal_moves()
        else:
            return None

    def get_figures(self):
        return self.__board.get_figures()

    def init_figures(self):
        self.__board.add_figure(Pane(self.__board, GameRoom.TEAM_BLACK, Coordinate(1, 4)))
        self.__board.add_figure(Pane(self.__board, GameRoom.TEAM_WHITE, Coordinate(4, 2)))
        self.__board.add_figure(King(self.__board, GameRoom.TEAM_WHITE, Coordinate(4, 1)))
        self.__board.add_figure(King(self.__board, GameRoom.TEAM_BLACK, Coordinate(1, 5)))
        self.__board.add_figure(Knight(self.__board, GameRoom.TEAM_BLACK, Coordinate(2, 5)))
        self.__board.add_figure(Knight(self.__board, GameRoom.TEAM_WHITE, Coordinate(3, 1)))
        self.__board.add_figure(Bishop(self.__board, GameRoom.TEAM_WHITE, Coordinate(2, 1)))
        self.__board.add_figure(Bishop(self.__board, GameRoom.TEAM_BLACK, Coordinate(3, 5)))
        self.__board.add_figure(Rook(self.__board, GameRoom.TEAM_BLACK, Coordinate(4, 5)))
        self.__board.add_figure(Rook(self.__board, GameRoom.TEAM_WHITE, Coordinate(1, 1)))

    def get_status(self):
        return self.__status

    @staticmethod
    def __get_rand_team():
        teams = [GameRoom.TEAM_WHITE, GameRoom.TEAM_BLACK]
        shuffle(teams)
        for team in teams:
            yield team

    def add_spectator(self, spectator: Player):
        spectator.set_team(GameRoom.SPECTATOR)
        self.__users.update({spectator.get_name(): spectator})


class Board:
    def __init__(self, x_from=1, x_to=4, y_from=1, y_to=5, march=False):
        self.x_from = x_from
        self.x_to = x_to
        self.y_from = y_from
        self.y_to = y_to
        self.march = march
        self.figures = []
        self.enpasant = None

    def is_in_board(self, coord: Coordinate):
        if self.x_to >= coord.x >= self.x_from and self.y_to >= coord.y >= self.y_from:
            return True
        else:
            return False

    def add_figure(self, figure):
        self.figures.append(figure)

    def capture_figure(self, figure):
        self.figures.remove(figure)

    def get_figures(self):
        return self.figures

    def get_all_fields(self):
        pass

    def get_square(self, coord):
        for figure in self.figures:
            if figure.coord == coord:
                return figure
        return None

    def move(self, figure, coord):
        if coord not in figure.get_legal_moves():
            return False
        if isinstance(figure, Pane) and abs(figure.coord.y - coord.y) > 1:
            self.enpasant = coord
        else:
            self.enpasant = None

        figure_on_way = self.get_square(coord)
        if figure_on_way is not None:
            self.capture_figure(figure_on_way)

        figure.coord = coord
        return True

    def get_king(self, team):
        for figure in self.figures:
            if figure.get_team() == team and isinstance(figure, King):
                return figure


class Figure:
    def __init__(self, board, team, coord: Coordinate):
        self.__team = team
        self.coord = coord
        self._board = board

    def get_chess_x(self):
        return coord_to_chess(self.coord)[0]

    def get_chess_y(self):
        return coord_to_chess(self.coord)[1]

    def get_available_moves(self):
        return []

    def get_legal_moves(self):
        legal_moves = []
        coord = self.coord
        my_king = self._board.get_king(self.get_team())
        for move in self.get_available_moves():
            self.coord = move
            if not my_king.under_attack():
                legal_moves.append(move)
        self.coord = coord
        return legal_moves

    def get_team(self):
        return self.__team

    def get_name(self):
        return 'Figure'

    def can_attack(self, figure):
        return False

    def _get_moves_on_line(self, x, y, attack=False):
        moves = []
        check_coord = Coordinate(self.coord.x, self.coord.y)
        while True:
            check_coord.x += x
            check_coord.y += y
            if self._board.is_in_board(check_coord):
                figure_on_check_coord = self._board.get_square(check_coord)
                if figure_on_check_coord is None:
                    moves.append(check_coord)
                    continue
                elif figure_on_check_coord.get_team() != self.get_team() or attack:
                    moves.append(check_coord)
                    return moves
                else:
                    return moves


class King(Figure):
    def __init__(self, board, team, coord: Coordinate):
        super().__init__(board, team, coord)

    def get_name(self):
        return f'king_{self.get_team()}'

    def get_available_moves(self):
        moves = []

        self.__check_and_append(Coordinate(self.coord.x, self.coord.y + 1), moves)
        self.__check_and_append(Coordinate(self.coord.x - 1, self.coord.y + 1), moves)
        self.__check_and_append(Coordinate(self.coord.x + 1, self.coord.y + 1), moves)
        self.__check_and_append(Coordinate(self.coord.x - 1, self.coord.y), moves)
        self.__check_and_append(Coordinate(self.coord.x + 1, self.coord.y), moves)
        self.__check_and_append(Coordinate(self.coord.x, self.coord.y - 1), moves)
        self.__check_and_append(Coordinate(self.coord.x - 1, self.coord.y - 1), moves)
        self.__check_and_append(Coordinate(self.coord.x + 1, self.coord.y - 1), moves)

        return moves

    def under_attack(self):
        for figure in self._board.get_figures():
            if figure.get_team() != self.get_team() and figure.can_attack(self):
                return True
        return False

    def __check_and_append(self, move_to, moves):
        if self._board.is_in_board(move_to):
            if self._board.get_square(move_to) is None:
                moves.append(move_to)
            elif self._board.get_square(move_to).get_team() != self.get_team():
                moves.append(move_to)

    def can_attack(self, figure):
        if abs(figure.coord.x - self.coord.x) < 2 and abs(figure.coord.y - self.coord.y) < 2:
            return True
        else:
            return False


class Bishop(Figure):
    def __init__(self, board, team, coord: Coordinate):
        super().__init__(board, team, coord)

    def get_name(self):
        return f'bishop_{self.get_team()}'

    def get_available_moves(self):
        return [self._get_moves_on_line(1, 1),
                self._get_moves_on_line(1, -1),
                self._get_moves_on_line(-1, 1),
                self._get_moves_on_line(-1, -1)]

    def can_attack(self, figure):
        if abs(self.coord.x - figure.coord.x) == abs(self.coord.y - figure.coord.y):
            if self.coord.x > figure.coord.x:
                x = 1
            else:
                x = -1
            if self.coord.y > figure.coord.y:
                y = 1
            else:
                y = -1
            for move_to in self._get_moves_on_line(x, y, True):
                check_figure = self._board.get_square(move_to)
                if check_figure is None:
                    continue
                elif check_figure is figure:
                    return True
            return False


class Rook(Figure):
    def __init__(self, board, team, coord: Coordinate):
        super().__init__(board, team, coord)

    def get_name(self):
        return f'rook_{self.get_team()}'

    def get_available_moves(self):
        return [self._get_moves_on_line(1, 0),
                self._get_moves_on_line(-1, 0),
                self._get_moves_on_line(0, 1),
                self._get_moves_on_line(0, -1)]

    def can_attack(self, figure):
        if self.coord.x == figure.coord.x:
            x = 0
            if self.coord.y > figure.coord.y:
                y = 1
            else:
                y = 0
        elif self.coord.y == figure.coord.y:
            y = 0
            if self.coord.x > figure.coord.x:
                x = 1
            else:
                x = 0
        else:
            return False
        for move_to in self._get_moves_on_line(x, y, True):
            check_figure = self._board.get_square(move_to)
            if check_figure is None:
                continue
            elif check_figure is figure:
                return True
        return False


class Knight(Figure):
    def __init__(self, board, team, coord: Coordinate):
        super().__init__(board, team, coord)

    def get_name(self):
        return f'knight_{self.get_team()}'

    def get_available_moves(self):
        moves = []
        self._fill_move(moves, Coordinate(self.coord.x + 2, self.coord.y + 1))
        self._fill_move(moves, Coordinate(self.coord.x + 2, self.coord.y - 1))
        self._fill_move(moves, Coordinate(self.coord.x - 2, self.coord.y + 1))
        self._fill_move(moves, Coordinate(self.coord.x - 2, self.coord.y - 1))
        self._fill_move(moves, Coordinate(self.coord.x + 1, self.coord.y + 2))
        self._fill_move(moves, Coordinate(self.coord.x + 1, self.coord.y - 2))
        self._fill_move(moves, Coordinate(self.coord.x - 1, self.coord.y + 2))
        self._fill_move(moves, Coordinate(self.coord.x - 1, self.coord.y - 2))
        return moves

    def _check_move(self, move_to):
        if not self._board.is_in_board(move_to):
            return False
        figure = self._board.get_square(move_to)
        if figure is None:
            return True
        elif figure.get_team() != self.get_team():
            return True
        else:
            return False

    def _fill_move(self, moves, move_to):
        if self._check_move(move_to):
            moves.append(move_to)

    def can_attack(self, figure):
        if (abs(self.coord.x - figure.coord.x) == 1 and abs(self.coord.y - figure.coord.y) == 2) \
                or (abs(self.coord.x - figure.coord.x) == 2 and abs(self.coord.y - figure.coord.y) == 1):
            return True
        else:
            return False


class Pane(Figure):
    def __init__(self, board, team, coord: Coordinate):
        super().__init__(board, team, coord)
        self.march = False

    def get_name(self):
        return f'pane_{self.get_team()}'

    def get_available_moves(self):
        moves = []
        # Направление
        direction = self._get_direction()

        # Шаг вперед
        move_to = Coordinate(self.coord.x, self.coord.y + direction)
        if self._board.is_in_board(move_to) and self._board.get_square(move_to) is None:
            moves.append(move_to)
        # Марш
        if self._board.march:
            if self.get_team() == GameRoom.TEAM_WHITE and self.coord.y == self._board.y_from + direction \
                    or self.get_team() == GameRoom.TEAM_BLACK and self.coord.y == self._board.y_to + direction:
                move_to = Coordinate(self.coord.x, self.coord.y + direction * 2)
                if self._board.is_in_board(move_to) and self._board.get_square(
                        move_to) is None and self._board.get_square(
                        Coordinate(self.coord.x, self.coord.y + direction)) is None:
                    moves.append(move_to)
        # Взятия
        figure_to_capture = self._board.get_square(Coordinate(self.coord.x - 1, self.coord.y + direction))
        if figure_to_capture is not None and figure_to_capture.get_team() != self.get_team():
            moves.append(figure_to_capture.coord)
        figure_to_capture = self._board.get_square(Coordinate(self.coord.x + 1, self.coord.y + direction))
        if figure_to_capture is not None and figure_to_capture.get_team() != self.get_team():
            moves.append(figure_to_capture.coord)
        # Взятия на проходе
        if self._board.enpasant is not None and self._board.enpasant.y == self.coord.y:
            if self._board.enpasant.x == self.coord.x + 1:
                moves.append(Coordinate(x=self.coord.x + 1, y=self.coord.y + direction))
            elif self._board.enpasant.x == self.coord.x - 1:
                moves.append(Coordinate(x=self.coord.x - 1, y=self.coord.y + direction))

        return moves

    def can_attack(self, figure):
        direction = self._get_direction()
        # Взятия
        if abs(figure.coord.x - self.coord.x) == 1 and figure.coord.y == self.coord.y + direction:
            return True
        # Взятия на проходе
        elif isinstance(figure,
                        Pane) and self._board.enpasant is not None and self._board.enpasant.y == self.coord.y and abs(
                self.coord.x - self._board.enpasant.x) == 1:
            return True
        else:
            return False

    def _get_direction(self):
        if self.get_team() == GameRoom.TEAM_WHITE:
            return 1
        else:
            return -1


def coord_from_chess(x: str, y: str):
    return Coordinate(ascii_uppercase.find(str(x)) + 1, y)


def coord_to_chess(coord: Coordinate):
    return ascii_uppercase[coord.x - 1], str(coord.y)


def create_game_room_if_init(rooms, room_name, creator_name):
    if room_name not in rooms:
        rooms.update({room_name: GameRoom(room_id=room_name, creator=creator_name)})


if __name__ == "__main__":
    pass
