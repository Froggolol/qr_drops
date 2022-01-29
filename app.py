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


class Reservation(BaseModel):
    name: str
    phone: str
    url: str
    isClaimed: int
    claimedDatetime: datetime
    size: str
    updated: datetime
    callCount: int


@app.get("/sizes")
async def return_sizes(request: Request):
    if is_not_claimed():
        t = connection.execute(db.select([sizes]).where(sizes.columns.quantity > 0))
        sizes_available = t.fetchall()
        return sizes_available
    else:
        return {'error': True, 'message': 'This code has already been used try to find another code GOOD LUCK!'}


@app.post("/sizes/{size}")
async def confirm_size(size, reservation: Reservation):
    t = connection.execute(db.select([sizes]).where(sizes.columns.size == size))
    sizes_available = t.fetchall()
    print(reservation.name)
    return sizes_available


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
