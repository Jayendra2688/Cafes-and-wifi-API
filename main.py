import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

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
        dic = {}
        for column in self.__table__.columns:
            dic[column.name] = getattr(self, column.name)
        return dic


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    with app.app_context():
        result = db.session.execute(db.select(Cafe))
        all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    # object into json --->serialization

    # here cafe is keyword argument and its value
    # return jsonify(cafe={
    #     # Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #
    #     # Put some properties in a sub-category
    #     "amenities": {
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #     }
    # })
    random_cafe_dic = random_cafe.to_dict()
    return jsonify(cafe=random_cafe_dic)


@app.route('/all')
def all():
    result = db.session.execute(db.select(Cafe)).scalars().all()
    cafes_dictionaries = []
    for cafe in result:
        cafes_dictionaries.append(cafe.to_dict())

    return jsonify(cafes=cafes_dictionaries)


@app.route('/search')
def search():
    location = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == location)).scalars().all()
    if len(result)==0:
        dic = {"Not Found":"Sorry no cafe is found for the given location."}
        return jsonify(error=dic),404

    return jsonify(cafes=[cafe.to_dict() for cafe in result])


@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

#dinamic routes
@app.route('/update_price/<int:id>',methods=["PATCH"])
def patch_new_price(id):
    # cafe = db.get_or_404(Cafe,id) // this giving error if cafe not found
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id==id)).scalar()
    if cafe:
        cafe.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify({"success":f"the price of {id} id cafe is updated."}),200
    else:
        return jsonify(error={"Not Found":"no cafe is found with given id."}),404

@app.route('/report_closed/<int:id>',methods=["DELETE"])
def delete_cafe(id):
    api_key = request.args.get('api_key')
    if api_key!="Topsecret":
        return jsonify(error={"error":"Not allowed.Make sure correct api_key"}),403
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id==id)).scalar()
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={"success":"cafe is removed from database sucessfully"}),200
    else:
        return jsonify(error={"Not found":"cafe with given id is not found in database"}),404

# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
