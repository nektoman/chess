from string import ascii_uppercase

class Player:
    def __init__(self, name):
        self.name = name


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


class Game_room:
    def __init__(self, room_id, creator):
        self.id = room_id
        self.creator = creator
        self.status = 'initial'
        self.__players = {}
        self.spectators = {}

        self.__board = Board()
        self.__board.add_figure(Pane(self.__board, Pane.BLACK, Coordinate(3, 4)))
        self.__board.add_figure(Pane(self.__board, Pane.WHITE, Coordinate(2, 2)))

    def add_player(self, player: Player):
        if player.name not in self.__players:
            self.__players.update({player.name:player})
            if not self.have_empty_slot():
                self.status = 'ready_to_start'
            return True

    def get_players(self):
        return self.__players

    def have_empty_slot(self):
        return len(self.__players) < 2

    def move(self, x_from, y_from, x_to, y_to):
        figure = self.__board.get_square(coord_from_chess(x_from, y_from))
        return self.__board.move(figure, coord_from_chess(x_to, y_to))

    def get_available_moves(self, coord : Coordinate):
        figure = self.__board.get_square(coord)
        if figure is not None:
            return figure.get_available_moves()
        else:
            return None

    def get_figures(self):
        return self.__board.get_figures()

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
        if coord not in figure.get_available_moves():
            return False
        if figure is Pane and abs(figure.coord.y - coord.y) > 1:
            self.enpasant = coord
        else:
            self.enpasant = None

        figure_on_way = self.get_square(coord)
        if figure_on_way is not None:
            self.capture_figure(figure_on_way)

        figure.coord = coord
        return True


class Figure:
    BLACK = 'black'
    WHITE = 'white'

    def __init__(self, board, team, coord: Coordinate):
        self.team = team
        self.coord = coord
        self.board = board

    def get_chess_x(self):
        return coord_to_chess(self.coord)[0]

    def get_chess_y(self):
        return coord_to_chess(self.coord)[1]

    def get_available_moves(self):
        return None


class Pane(Figure):
    def __init__(self, board, team, coord: Coordinate):
        super().__init__(board, team, coord)
        self.march = False
        self.name = f'pane_{team}'

    def get_available_moves(self):
        moves = []
        # Направление
        if self.team == Figure.WHITE:
            y = 1
        else:
            y = -1

        # Шаг вперед
        move_to = Coordinate(self.coord.x, self.coord.y + y)
        if self.board.is_in_board(move_to) and self.board.get_square(move_to) is None:
            moves.append(move_to)
        # Марш
        if self.board.march:
            if self.team == Figure.WHITE and self.coord.y == self.board.y_from + y or self.team == Figure.BLACK and self.coord.y == self.board.y_to + y:
                move_to = Coordinate(self.coord.x, self.coord.y + y * 2)
                if self.board.is_in_board(move_to) and self.board.get_square(move_to) is None and self.board.get_square(
                        Coordinate(self.coord.x, self.coord.y + y)) is None:
                    moves.append(move_to)
        # Взятия
        figure_to_capture = self.board.get_square(Coordinate(self.coord.x - 1, self.coord.y + y))
        if figure_to_capture is not None and figure_to_capture.team != self.team:
            moves.append(figure_to_capture.coord)
        figure_to_capture = self.board.get_square(Coordinate(self.coord.x + 1, self.coord.y + y))
        if figure_to_capture is not None and figure_to_capture.team != self.team:
            moves.append(figure_to_capture.coord)
        # Взятия на проходе
        if self.board.enpasant is not None and self.board.enpasant.y == self.coord.y:
            if self.board.enpasant.x == self.coord.x + 1:
                moves.append(Coordinate(x=self.coord.x + 1, y=self.coord.y + y))
            elif self.board.enpasant.x == self.coord.x - 1:
                moves.append(Coordinate(x=self.coord.x - 1, y=self.coord.y + y))

        return moves


def coord_from_chess(x: str, y: str):
    return Coordinate(ascii_uppercase.find(str(x)) + 1, y)


def coord_to_chess(coord: Coordinate):
    return ascii_uppercase[coord.x - 1], str(coord.y)


def create_game_room_if_init(rooms, room_name, creator_name):
    if room_name not in rooms:
        rooms.update({room_name: Game_room(room_id=room_name, creator=creator_name)})


if __name__ == "__main__":
    pass
