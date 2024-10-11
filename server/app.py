#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods():
    if request.method == 'GET':
        # Retrieve all baked goods
        baked_goods = []
        for baked_good in BakedGood.query.all():
            baked_good_dict = baked_good.to_dict()
            baked_goods.append(baked_good_dict)

        # Return the baked goods as a response
        response = make_response(
            baked_goods,
            200
        )
        return response

    elif request.method == 'POST':
        # Create a new baked good using form data
        new_baked_good = BakedGood(
            name=request.form.get("name"),
            price=request.form.get("price"),
            bakery_id=request.form.get("bakery_id")
        )

        # Add and commit to the database
        db.session.add(new_baked_good)
        db.session.commit()

        # Convert the new baked good to a dictionary and return it as a response
        baked_good_dict = new_baked_good.to_dict()

        response = make_response(
            baked_good_dict,
            201
        )
        return response

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    # Fetch the bakery by id
    bakery = Bakery.query.filter(Bakery.id == id).first()

    if bakery is None:
        response_body = {
            "message": "This bakery does not exist in our database. Please try again."
        }
        response = make_response(response_body, 404)
        return response

    else:
        if request.method == 'GET':
            # Serialize and return the bakery for GET requests
            bakery_dict = bakery.to_dict()
            response = make_response(bakery_dict, 200)
            return response

        elif request.method == 'PATCH':
            # Loop through the form data and set the bakery attributes
            for attr in request.form:
                setattr(bakery, attr, request.form.get(attr))

            # Add the updated bakery and commit the change
            db.session.add(bakery)
            db.session.commit()

            # Serialize the updated bakery data and return it
            bakery_dict = bakery.to_dict()
            response = make_response(bakery_dict, 200)
            return response

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    # Fetch the baked good by id
    baked_good = BakedGood.query.filter(BakedGood.id == id).first()

    if baked_good is None:
        # If the baked good does not exist, return 404 with an error message
        response_body = {
            "message": "Baked good not found. Please check the ID and try again."
        }
        response = make_response(response_body, 404)
        return response

    else:
        # Delete the baked good from the database
        db.session.delete(baked_good)
        db.session.commit()

        # Return a success message as JSON
        response_body = {
            "message": f"Baked good '{baked_good.name}' with ID {id} was successfully deleted."
        }
        response = make_response(response_body, 200)
        return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)