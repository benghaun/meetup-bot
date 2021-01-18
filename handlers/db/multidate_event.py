from typing import List
import traceback

from .db import conn


class Date():
    def __init__(self, row):
        self.date = row[0]
        self.going = row[1]


class MultidateEvent():
    def __init__(self, rows: List[List[tuple]]):
        self.info = rows[0][1]
        self.dates = {row[2]: row[3] for row in rows}
    # returns a string representing the attendance for every date

    def attendance(self):
        message = self.info + '\n\n'
        for date, going in self.dates.items():
            message += '{}:\n'.format(date) + '\n'.join(going) + \
                '\n' + ('\n' if len(going) > 0 else '')
        return message

    def save(self):
        cur = conn.cursor()
        for date, going in self.dates.items():
            cur.execute('UPDATE MULTIDATE_EVENTS SET going=%s WHERE date=%s',
                        (going, date))
        conn.commit()


def create_multidate_event(dates: List[str], info: str) -> None:
    cur = conn.cursor()
    for date in dates:
        cur.execute(
            'INSERT INTO MULTIDATE_EVENTS (info, date, going) VALUES(%s, %s, %s)', (info, date, []))
    conn.commit()


def get_multidate_event() -> MultidateEvent:
    cur = conn.cursor()
    cur.execute('SELECT id, info, date, going FROM MULTIDATE_EVENTS')
    rows = cur.fetchall()
    if rows == []:
        return None

    return MultidateEvent(rows)


def delete_multidate_event() -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM MULTIDATE_EVENTS")
    conn.commit()
