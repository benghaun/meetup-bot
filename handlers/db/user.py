from .db import conn
from typing import List


class User():
    def __init__(self, row):
        self.first_name = row[0]
        self.chat_id = row[1]
        self.username = row[2]


def add_user(first_name: str, chat_id: str, username: str) -> None:
    cur = conn.cursor()
    cur.execute('INSERT INTO USERS (firstname, chatid, username) VALUES (%s, %s, %s)',
                (first_name, chat_id, username))
    conn.commit()


def remove_user_by_chat_id(chat_id: str) -> None:
    cur = conn.cursor()
    cur.execute('DELETE FROM USERS WHERE chatid=%s', (chat_id,))
    conn.commit()


def get_users() -> List[User]:
    cur = conn.cursor()
    cur.execute(
        'SELECT firstname, chatid, username FROM USERS')
    rows = cur.fetchall()
    return [User(row) for row in rows]


def get_user_by_chat_id(chat_id: int) -> User:
    cur = conn.cursor()
    cur.execute(
        'SELECT firstname, chatid, username FROM USERS WHERE chatid=%s', (chat_id,))
    rows = cur.fetchall()
    if rows == []:
        return None
    return User(rows[0])
