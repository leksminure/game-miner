import numpy as np
import shelve


class Game_Properties():
    def __init__(self):
        self.n = 5
        self.bombs = 3
        self.mines_board = None
        self.user_board = None
        self.bomb_on_the_board = -1
        self.exit_command = 'exit'

    def clean_boards(self):
        self.mines_board = None
        self.user_board = None


class Work_With_User():
    properties = Game_Properties()

    def set(self, properties):
        self.properties = properties

    def ask_int(self, question='Введите N (размеры поля NxN)'):
        response = float('-inf')
        question = '\n' + question + '\n'
        while not response > 1:
            try:
                response = int(input(question))
            except:
                print('Введите положительное число больше 1')
        return response

    def ask_bombs(self, n, question='Введите количество бомб, не превышающее число клеток на доске'):
        response = float('-inf')
        question = '\n' + question + '\n'
        while not 0 < response < n ** 2:
            try:
                response = int(input(question))
            except:
                print('Введите именно число бомб, не превышающее число клеток на доске')
        return response

    def y_or_n(self, question='Хочешь поиграть еще раз? (y/n)'):
        question = '\n' + question + '\n'
        response = None
        while response not in ('y', 'n'):
            response = input(question).lower()
        return response

    def ask_indexes(self, n, question='Введите через пробел индексы строки и столбца и действие, индексы - \
числа в промежутке от 1 до'):
        i, j, action = None, None, None
        question = '\n' + question + ' ' + str(n) + '\n'
        while i not in range(1, n + 1) or j not in range(1, n + 1) or action not in ('flag', 'open'):
            try:
                line = input(question)
                if line == self.properties.exit_command:
                    return None, None, None
                values = line.split()
                if len(values) == 3:
                    i = int(values[0])
                    j = int(values[1])
                    action = values[2].lower()
                else:
                    continue
            except:
                print('Попробуйте еще раз. Введите через пробел индексы строки и столбца и действие, индексы - числа в\
промежутке от 1 до', n)
        return (i-1, j-1, action)


class Board(object):
    def __init__(self, game_properties):
        self.n = game_properties.n
        self.bombs = game_properties.bombs
        self.bomb_on_the_board = game_properties.bomb_on_the_board
        if game_properties.mines_board is not None:
            self.arr = game_properties.mines_board
            self.show_arr = game_properties.user_board
        else:
            self.arr = np.zeros((self.n+2, self.n+2), dtype=np.int32)
            self.arr[0, :], self.arr[-1, :], self.arr[:, 0], self.arr[:, -1] = 8, 8, 8, 8

            k = 0
            while k < self.bombs:
                random_i = np.random.randint(1, self.n+1)
                random_j = np.random.randint(1, self.n+1)
                if self.arr[random_i][random_j] != self.bomb_on_the_board:
                    self.arr[random_i][random_j] = self.bomb_on_the_board
                    k += 1
                else:
                    continue
            self.show_arr = np.array(['-'] * self.n**2).reshape(self.n, self.n)
        self.__gameover = False

    def change_board(self, i, j, action):
        if action == 'open':
            if self.arr[i+1][j+1] != self.bomb_on_the_board and self.show_arr[i][j] != '!':
                count_of_mines = self.get_mines(i, j)
                if count_of_mines:
                    self.show_arr[i][j] = count_of_mines
                else:
                    queue = [(i+1, j+1)]
                    processed = []
                    while queue:
                        indexi, indexj = queue.pop(0)
                        if (indexi, indexj) not in processed:
                            count_of_mines = self.get_mines(indexi-1, indexj-1)
                            self.show_arr[indexi-1][indexj-1] = count_of_mines
                            if not count_of_mines:
                                for i1 in range(indexi-1, indexi+2):
                                    for j1 in range(indexj-1, indexj+2):
                                        if i1 == indexi and j1 == indexj:
                                            continue
                                        if self.arr[i1][j1] != 8 and self.show_arr[i1-1][j1-1] != '!':
                                            queue.append((i1, j1))
                            processed.append((indexi, indexj))
            elif self.arr[i+1][j+1] == self.bomb_on_the_board:
                self.show_all_mines()
                self.__gameover = True
        else:
            if self.show_arr[i][j] == '!':
                self.show_arr[i][j] = '-'
            elif self.show_arr[i][j] == '-':
                self.show_arr[i][j] = '!'

    def show_all_mines(self):
        for i in range(1, self.n+1):
            for j in range(1, self.n+1):
                if self.arr[i][j] == self.bomb_on_the_board:
                    self.show_arr[i - 1][j - 1] = '*'

    def get_mines(self, i, j):
        arr1 = self.arr[i:i+3, j:j+3]
        number = np.sum(arr1 == self.bomb_on_the_board)
        return number

    def show_board(self):
        print(self.show_arr)
        print('.' * round(4.5 * self.n))

    def is_winner(self):
        win = np.sum(self.show_arr == '-') + np.sum(self.show_arr == '!') == self.bombs
        if win:
            self.show_all_mines()
            self.show_board()
        return win

    @property
    def gameover(self):
        return self.__gameover


class Game():
    game_properties = Game_Properties()
    board = None
    __worker = Work_With_User()

    def __init__(self):
        pass

    def load_properties(self, game_properties):
        self.game_properties = game_properties

    def create_game_board(self):
        self.board = Board(self.game_properties)

    def play(self):
        self.board.show_board()
        while True:
            i, j, action = self.__worker.ask_indexes(self.board.n)
            if not action:
                self.save_game(self.board.arr, self.board.show_arr, n=self.board.n, bombs=self.board.bombs)
                break
            self.board.change_board(i, j, action)
            self.board.show_board()
            if self.check_event():
                self.delete_saved_game()
                break

    def check_event(self):
        if self.board.gameover:
            print('Вы проиграли...')
            return True
        if self.board.is_winner():
            print('Поздравляю вы победили!')
            return True
        return False

    def save_game(self, arr, show_arr, n, bombs):
        f = shelve.open('save.dat', 'n')
        f['arr'] = arr
        f['show_arr'] = show_arr
        f['n'] = n
        f['bombs'] = bombs
        f.close()

    @property
    def is_saved_game(self):
        with shelve.open('save.dat', 'c') as f:
            return True if f else False

    def return_saved_game(self):
        with shelve.open('save.dat', 'c') as f:
            return f['arr'], f['show_arr'], f['n'], f['bombs']

    def delete_saved_game(self):
        file_for_clean = shelve.open('save.dat', 'n')
        file_for_clean.close()
        self.game_properties.clean_boards()


def main():
    worker = Work_With_User()
    properties = Game_Properties()
    game = Game()

    while True:
        if game.is_saved_game and worker.y_or_n(question='У вас еcть сохраненная партия, хотите загрузить ее?(y/n)') == 'y':
            properties.mines_board, properties.user_board, properties.n, properties.bombs = game.return_saved_game()
        else:
            properties.n = worker.ask_int()
            properties.bombs = worker.ask_bombs(properties.n)

        game.load_properties(game_properties=properties)
        game.create_game_board()
        game.play()

        response = worker.y_or_n('Хотите сыграть еще одну игру?(y/n)')
        if response == 'y':
            continue
        else:
            break


main()
input('\n\nНажмите Enter, чтобы выйти из игры')