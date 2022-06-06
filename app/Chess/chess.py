from string import ascii_uppercase

class Coordinate():
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

class Player():
    def __init__(self, name):
        self.name = name


class Board():
    def __init__(self, X_FROM=1, X_TO=4, Y_FROM=1, Y_TO=5, march=False):
        self.X_FROM=X_FROM
        self.X_TO=X_TO
        self.Y_FROM=Y_FROM
        self.Y_TO=Y_TO
        self.march = march
        self.figures = []
        self.enpasant = None

    def is_in_board(self, coord: Coordinate):
        if coord.x >= self.X_FROM and coord.x <= self.X_TO and coord.y >= self.Y_FROM and coord.y <= self.Y_TO:
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

class Figure():
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
        #Направление
        if self.team == Figure.WHITE:
            y = 1
        else:
            y = -1

        #Шаг вперед
        move_to = Coordinate(self.coord.x, self.coord.y + y)
        if self.board.is_in_board(move_to) and self.board.get_square(move_to) == None:
            moves.append(move_to)
        #Марш
        if self.board.march == True:
            if self.team == Figure.WHITE and self.coord.y == self.board.Y_FROM + y or self.team == Figure.BLACK and self.coord.y == self.board.Y_TO + y:
                move_to = Coordinate(self.coord.x, self.coord.y + y * 2)
                if self.board.is_in_board(move_to) and self.board.get_square(move_to) == None and self.board.get_square(Coordinate(self.coord.x, self.coord.y + y)) == None:
                    moves.append(move_to)
        #Взятия
        move_to = self.board.get_square(Coordinate(self.coord.x - 1, self.coord.y + y))
        if move_to != None and move_to.team != self.team:
            moves.append(move_to)
        move_to = self.board.get_square(Coordinate(self.coord.x + 1, self.coord.y + y))
        if move_to != None and move_to.team != self.team:
            moves.append(move_to)
        #Взятия на проходе todo
        if self.board.enpasant != None:
            pass
            # if
        return moves


class Game():
    KING = 'king'
    BISHOP = 'bishop'
    KNIGHT = 'knight'
    ROOK = 'rook'
    def __init__(self, player_black, player_white):
        self.player_black = player_black
        self.player_white = player_white
        # self.figures = { '1': {'x':'4', 'y':'5', 'texture_name':'pane_black','name': Game.PANE, 'team': Game.BLACK},
        #                  '2': {'x':'1', 'y':'1', 'texture_name':'pane_white','name': Game.PANE, 'team': Game.WHITE} }
        # self.player_moves = Game.WHITE

    # def get_available_moves(self, figure_id):
    #     # all_moves =
    #     team = self.figures[figure_id]['team']

def coord_from_chess(x: str, y: str):
    return Coordinate(ascii_uppercase.find(str(x)) + 1, y)

def coord_to_chess(coord: Coordinate):
    return ascii_uppercase[coord.x - 1], str(coord.y)

if __name__ == "__main__":
    pane = Pane(Board(),Figure.WHITE, coord_from_chess('B','2'))
    print(pane.get_available_moves())
