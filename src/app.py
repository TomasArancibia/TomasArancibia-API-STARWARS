"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Person, Planet, Favorite


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ModelesDB.db"

db.init_app(app)
CORS(app)
MIGRATE = Migrate(app, db)

setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User()
    new_user.username = data['username']
    new_user.password = data['password']
    new_user.first_name = data['first_name']
    new_user.last_name = data['last_name']
    new_user.email = data['email']
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    serialized_people = [person.serialize() for person in people]
    return jsonify(serialized_people), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Person.query.get_or_404(people_id)
    serialized_person = person.serialize()
    return jsonify(serialized_person), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    serialized_planets = [planet.serialize() for planet in planets]
    return jsonify(serialized_planets), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    serialized_planet = planet.serialize()
    return jsonify(serialized_planet), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized_users = [user.serialize() for user in users]
    return jsonify(serialized_users), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    serialized_favorites = [favorite.serialize() for favorite in favorites]
    return jsonify(serialized_favorites), 200



@app.route('/favorite/planet/<int:planet_id>', methods=['POST', 'PUT'])
def add_or_update_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, favorite_planets=planet_id).first()
    if favorite is None:
        favorite = Favorite(user_id=user_id, favorite_planets=planet_id)
        db.session.add(favorite)
    else:
        favorite.favorite_planets = planet_id

    db.session.commit()
    return jsonify({'message': 'Favorite planet added/updated successfully'}), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST', 'PUT'])
def add_or_update_favorite_people(people_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, favorite_people=people_id).first()

    if favorite is None:
        favorite = Favorite(user_id=user_id, favorite_people=people_id)
        db.session.add(favorite)
    else:
        favorite.favorite_people = people_id

    db.session.commit()

    return jsonify({'message': 'Favorite people added/updated successfully'}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, favorite_planets=planet_id).first()

    if favorite is None:
        raise APIException('Favorite planet not found', status_code=404)
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': 'Favorite planet deleted successfully'}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, favorite_people=people_id).first()

    if favorite is None:
        raise APIException('Favorite people not found', status_code=404)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': 'Favorite people deleted successfully'}), 200

@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    new_person = Person()
    new_person.name = data['name']
    new_person.height = data['height']
    new_person.mass = data['mass']
    new_person.hair_color = data['hair_color']
    new_person.skin_color = data['skin_color']
    new_person.eye_color = data['eye_color']
    new_person.birth_year = data['birth_year']
    new_person.gender = data['gender']
    new_person.homeworld_id = data['homeworld_id']
    db.session.add(new_person)
    db.session.commit()
    
    return jsonify({'message': 'Person created successfully'}), 201


@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    new_planet = Planet()
    new_planet.name = data['name']
    new_planet.diameter = data['diameter']
    new_planet.rotation_period = data['rotation_period']
    new_planet.orbital_period = data['orbital_period']
    new_planet.gravity = data['gravity']
    new_planet.population = data['population']
    new_planet.climate = data['climate']
    new_planet.terrain = data['terrain']
    new_planet.surface_water = data['surface_water']
    db.session.add(new_planet)
    db.session.commit()
    
    return jsonify({'message': 'Planet created successfully'}), 201

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
