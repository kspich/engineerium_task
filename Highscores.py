from pygame.locals import *
import sqlite3

# тот самый класс для взаимодействия с бд
# если это не то, что вам нужно, напишите
class Highscores():
        def __init__(self) -> None:
            self.db = sqlite3.connect("players.db")
            self.cur = self.db.cursor()
            self.cur.execute("CREATE TABLE IF NOT EXISTS players(name, score)")
            print(f'Database was initialized')

        def pasteNew(self, name, score):
            self.cur.execute(f"INSERT INTO players VALUES ('{name}', {score})")
            print(f'New score ({name}, {score}) pasted into db')
            self.db.commit()

        def getScores(self):
            res = ''
            i = 1
            for row in self.cur.execute("SELECT name, score FROM players ORDER BY score DESC LIMIT 5"):
                res += str(i) + '. ' + row[0] + ' ' + str(row[1]) + '\n'
                i +=1
            while (i < 6):
                res += str(i) + '. ' + '- - -' + '\n'
                i +=1
                 
            print(f'Results for select statement:\n{res}')
            return res