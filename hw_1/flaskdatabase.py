import sqlite3


class FlaskDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cursor = db.cursor()

    def get_user(self, email):
        query = f"SELECT * from users WHERE email='{email}'"
        try:
            self.__cursor.execute(query)
            res = self.__cursor.fetchall()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print(f'Unexpected exception {e}')
        return []

    def add_user(self, email, password):
        query = f'INSERT INTO users VALUES (NULL, ?, ?)'
        try:
            self.__cursor.execute(query, (email, password))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f'Error adding user to database: {e}')
            return False
        return True
