from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read all Records, choose a random one then retun it through a json format
# Method 1 - manual
# @app.route("/random", methods=["GET"])
# def get_random_cafe():
#     all_cafe = db.session.query(Cafe).all()
#     random_cafe = random.choice(all_cafe)
#     return jsonify(cafe={
#         "can_take_calls": random_cafe.can_take_calls,
#         "coffee_price": random_cafe.coffee_price,
#         "has_sockets": random_cafe.has_sockets,
#         "has_toilet": random_cafe.has_toilet,
#         "has_wifi": random_cafe.has_wifi,
#         "id": random_cafe.id,
#         "img_url": random_cafe.img_url,
#         "location": random_cafe.location,
#         "map_url": random_cafe.map_url,
#         "name": random_cafe.name,
#         "seats": random_cafe.seats
#     })\

# Method 2 - to_dict
@app.route("/random", methods=["GET"])
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())

# Nb: GET is allowed by default on all routes.


# HTTP GET - Read Records
@app.route("/all", methods=["GET"])
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    list_cafes = [cafe.to_dict() for cafe in all_cafes]
    return jsonify(cafes=list_cafes)

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
