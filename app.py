"""
⢀⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆
⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠁⠸⣼⡿
⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀⠀
⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀
⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠿⠿⠿⠛⠉

fucking donkey

"""

import uvicorn
from fastapi import FastAPI
import sqlalchemy as db
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

engine = db.create_engine('sqlite:///qr_code_urls.db')
connection = engine.connect()
metadata = db.MetaData()
sizes = db.Table('sizes', metadata, autoload=True, autoload_with=engine)
claimed = db.Table('the_one_and_only', metadata, autoload=True, autoload_with=engine)


class Reservation(BaseModel):
    name: str
    phone: str
    url_token: str
    size: str
    updated: datetime


@app.get("/sizes")
async def return_sizes(url_token):
    if _is_not_claimed(url_token, count=False):
        return _sizes_left()
    else:
        return {'error': True, 'message': 'This code has already been used try to find another code GOOD LUCK!'}


@app.post("/reserve/")
async def confirm_size(reservation: Reservation):
    try:
        assert len(reservation.phone) == 8
        assert 2 <= len(reservation.size.replace('.','')) <= 3
    except AssertionError:
        return {'error': True, 'message': 'Phone must be 8 characters long example: 12345678 and size must be from the list'}

    if not _is_not_claimed(reservation.url_token):
        return {'error': True, 'message': 'This code has already been used try to find another code GOOD LUCK!'}

    if _size_reservation(reservation.size):
        stmt = claimed.update().where(claimed.columns.url_token == reservation.url_token).values(
            name=reservation.name,
            phone=reservation.phone,
            size=reservation.size,
            updated=reservation.updated,
            claimedDatetime=datetime.now(),
            isClaimed=1
        )
        response = connection.execute(stmt)

        if response.rowcount == 1:
            return {'error':False, 'message': f'CONGRATS {reservation.name} you got a size: {reservation.size} waiting for you to pickup at Enghaven'}
        else:
            return {'error': True, 'message': 'Something went wrong not sure what try again, maybe the url was already used, try again?'}
    else:
        return {'error': True,
                'message': 'Unlucky someone else has claimed that size, try another one. '}


def _is_not_claimed(url_token, count=True):
    t = connection.execute(db.select(claimed.columns.isClaimed).filter(claimed.columns.url_token == url_token))
    is_valid = t.fetchone()
    if is_valid:
        if count:
            _we_counting_here(url_token)
        if is_valid['isClaimed'] == 0:
            return True
    return False


def _size_reservation(req_size):
    size_quant = connection.execute(db.select(sizes.columns.quantity).filter(sizes.columns.size == req_size)).fetchone()
    claimed_sizes = connection.execute(db.select([db.func.count(claimed.columns.size)]).filter(claimed.columns.size == req_size)).fetchone()

    if size_quant['quantity'] - claimed_sizes['count_1']:
        return True
    return False


def _sizes_left():
    sizes_available = connection.execute(db.select([sizes])).fetchall()
    size_dict = {}
    for d in sizes_available:
        size_dict[d['size']] = d['quantity']

    sizes_claimed = connection.execute(db.select(claimed.columns.size).filter(claimed.columns.size != ''))
    for item in sizes_claimed:
        size_dict[item['size']] -= 1
        if size_dict[item['size']] == 0:
            size_dict.pop(item['size'])
    return {'sizes': list(size_dict.keys())}



def _we_counting_here(url_token):
    stmt = claimed.update().where(claimed.columns.url_token == url_token).values(callCount=(claimed.columns.callCount + 1))
    connection.execute(stmt)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
