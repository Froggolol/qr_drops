import uvicorn
from fastapi import FastAPI
import sqlalchemy as db

app = FastAPI()

engine = db.create_engine('sqlite:///qr_code_urls.db')
connection = engine.connect()
metadata = db.MetaData()

@app.get("/sizes")
async def return_sizes():
    sizes = db.Table('sizes', metadata, autoload=True, autoload_with=engine)
    t = connection.execute(db.select([sizes]).where(sizes.columns.quantity > 0))
    for row in t.fetchall():
        print(row._asdict())
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5049)
