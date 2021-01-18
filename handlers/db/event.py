from .db import conn
from .user import User
from typing import List


class Event():
    def __init__(self, row):
        self.id = row[0]
        self.going = row[1]
        self.not_going = row[2]
        self.maybe = row[3]
        self.unresponded = row[4]
        self.info = row[5]

    # returns a string representing the overall event attendance
    def attendance(self):
        attendance = ("%s\n\n"
                      "Going:\n"
                      "%s\n"
                      "Not going:\n"
                      "%s\n"
                      "Maybe:\n"
                      "%s\n"
                      "Unresponded:\n"
                      "%s" % (self.info, '\n'.join(self.going) + '\n', '\n'.join(self.not_going) + '\n', '\n'.join(self.maybe) + '\n', '\n'.join(self.unresponded)))
        return attendance

    def save(self):
        cur = conn.cursor()
        cur.execute('UPDATE EVENTS SET going=%s, notgoing=%s, maybe=%s, unresponded=%s',
                    (self.going, self.not_going, self.maybe, self.unresponded))
        conn.commit()


def get_event() -> Event:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, going, notgoing, maybe, unresponded, info FROM EVENTS")
    results = cur.fetchall()
    if results == []:
        return None
    return Event(results[0])


def create_event(info: str, organizer_chatid: int, organizer_name: str, users: List[User]) -> Event:
    all_names_except_organizer = [
        user.first_name for user in users if user.chat_id != organizer_chatid]
    cur = conn.cursor()
    cur.execute('INSERT INTO EVENTS (going, notgoing, maybe, unresponded, info) VALUES (%s, %s, %s, %s, %s) RETURNING id,going,notgoing,maybe,unresponded,info',
                ([organizer_name], [], [], all_names_except_organizer, info))
    conn.commit()
    return Event(cur.fetchall()[0])


def delete_event() -> None:
    cur = conn.cursor()
    cur.execute('DELETE FROM EVENTS')
    conn.commit()
