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


# HTTP GET - Search records that match the area wanted by the client
@app.route("/search", methods=["GET"])
def search_cafe():
    area = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == area))
    all_cafes = result.scalars().all()
    if all_cafes:
        list_cafes = [cafe.to_dict() for cafe in all_cafes]
        return jsonify(cafes=list_cafes)
    else:
        return jsonify(error={"Not found": "Sorry, there is no cafe at that location."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    if request.method == "POST":
        cafe = Cafe(
            name=request.form["name"],
            map_url=request.form["map_url"],
            img_url=request.form["img_url"],
            location=request.form["location"],
            seats=request.form["seats"],
            has_toilet=bool(request.form["has_toilet"]),
            has_wifi=bool(request.form["has_wifi"]),
            has_sockets=bool(request.form["has_sockets"]),
            can_take_calls=bool(request.form["can_take_calls"]),
            coffee_price=request.form["coffee_price"]
        )
        db.session.add(cafe)
        db.session.commit()

        return jsonify(response={"success": "Successfully added the new cafe."}), 201


# HTTP PUT/PATCH - Update Record

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    if request.method == "PATCH":
        cafe_to_update = db.session.get(Cafe, cafe_id)
        if cafe_to_update:
            # Method n°1
            # cafe_to_update.__setattr__('coffee_price', request.args.get('new_price'))
            # Method n°2
            cafe_to_update.coffee_price = request.args.get('new_price')
            db.session.commit()
            return jsonify(response={"success": "Successfully updated the price"}), 201
        else:
            return jsonify(error={"Not found": "Sorry, a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete Record
@app.route("/reported-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    if request.args.get('api_key') == "TopSecretAPIKey":
        cafe_to_rm = db.session.get(Cafe, cafe_id)
        if cafe_to_rm:
            db.session.delete(cafe_to_rm)
            db.session.commit()
            return jsonify(response={"success": "Successfully removed the cafe from the database"}), 201
        else:
            return jsonify(error={"Not found": "Sorry, a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Unauthorized": "You are not authorized to access this resource. Please make sur you "
                                              "have the correct api_key"}), 401


if __name__ == '__main__':
    app.run(debug=True)
