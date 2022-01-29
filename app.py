import uvicorn
from fastapi import FastAPI, Request
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
async def return_sizes(request: Request, url_token):
    if _is_not_claimed(url_token):
        t = connection.execute(db.select([sizes]).filter(sizes.columns.quantity > 0))
        sizes_available = t.fetchall()
        return sizes_available
    else:
        return {'error': True, 'message': 'This code has already been used try to find another code GOOD LUCK!'}


@app.post("/reserve/")
async def confirm_size(reservation: Reservation):
    if _is_not_claimed(reservation.url_token, count=False) == False:
        return {'error': True, 'message': 'This code has already been used try to find another code GOOD LUCK!'}

    if size_reservation(reservation.size):
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
            stmt = sizes.update().where(sizes.columns.size == reservation.size).values(quantity=(sizes.columns.quantity + 1))
            connection.execute(stmt)
            return {'error': True, 'message': 'Something went wrong not sure what try again, maybe the url was already used'}
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


def size_reservation(size):
    t = connection.execute(db.select([sizes]).filter(sizes.columns.size == size, sizes.columns.quantity > 0))
    is_available = t.fetchone()
    if is_available:
        stmt = sizes.update().where(sizes.columns.size == size).values(quantity=(sizes.columns.quantity - 1))
        connection.execute(stmt)
        return True
    return False


def _we_counting_here(url_token):
    stmt = claimed.update().where(claimed.columns.url_token == url_token).values(callCount=(claimed.columns.callCount + 1))
    test = connection.execute(stmt)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)