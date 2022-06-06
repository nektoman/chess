from string import ascii_uppercase

class Room:
    def __init__(self, id, game, creator):
        self.game = game
        self.id = id
        self.creator = creator
        self.status = 'initial'
        self.players = {}
        self.spectators = {}

    def get_figures(self):
        return self.game.board.get_figures()

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


class Player:
    def __init__(self, name):
        self.name = name


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
        if figure is Pane and abs(figure.y - coord.y) > 1:
            self.enpasant = coord
        else:
            self.enpasant = None


class Figure:
    BLACK = 'team_black'
    WHITE = 'team_white'

    def __init__(self, board, team, coord: Coordinate):
        self.team = team
        self.coord = coord
        self.board = board


class Pane(Figure):
    def __init__(self, board, team, coord: Coordinate):
        super().__init__(board, team, coord)
        self.march = False

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
        move_to = self.board.get_square(Coordinate(self.coord.x - 1, self.coord.y + y))
        if move_to is not None and move_to.team != self.team:
            moves.append(move_to)
        move_to = self.board.get_square(Coordinate(self.coord.x + 1, self.coord.y + y))
        if move_to is not None and move_to.team != self.team:
            moves.append(move_to)
        # Взятия на проходе
        if self.board.enpasant is not None and self.board.enpasant.y == self.coord.y:
            if self.board.enpasant.x == self.coord.x + 1:
                moves.append(Coordinate(x=self.coord.x + 1, y=self.coord.y + y))
            elif self.board.enpasant.x == self.coord.x - 1:
                moves.append(Coordinate(x=self.coord.x - 1, y=self.coord.y + y))

        return moves


class Game:
    def __init__(self):
        self.board = Board()
        self.board.add_figure(Pane(self.board, Pane.BLACK, Coordinate(4,4)))
        self.board.add_figure(Pane(self.board, Pane.WHITE, Coordinate(2,2)))

def coord_from_chess(x: str, y: str):
    return Coordinate(ascii_uppercase.find(str(x)) + 1, y)


def coord_to_chess(coord: Coordinate):
    return ascii_uppercase[coord.x - 1], str(coord.y)


if __name__ == "__main__":
    game = Game()
    print(game.board.get_square(Coordinate(2,2)).get_available_moves())