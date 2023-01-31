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
from models import db, User, Planet, People, Vehicle, Favorite
import json
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ----- Endpoint Authentication  -----

# Post - User
@app.route('/signup', methods=['POST'])
def singup():
    body = json.loads(request.data)
    
    user = User.query.filter_by(email=body["email"]).first() 
    
    if user is None:
        userDos = User.query.filter_by(username=body["username"]).first() 
        if userDos is None:
            newUser = User(first_name=body["first_name"], last_name=body["last_name"], email=body["email"], password=body["password"], username=body["username"])
            db.session.add(newUser)
            db.session.commit()

            response_body = {
                "msg": "El usuario fue creado con exito"
            }
            return jsonify(response_body), 200

    response_body = {
            "msg": "User exist in the system"
        }
    return jsonify(response_body), 400

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"msg": "User does not exist"}), 404


    if username != user.username or password != user.password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.id)

    response_body = {
        "access_token": access_token,
        "user": user.serialize()
    }

    return jsonify(response_body), 200

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/private", methods=["GET"])
@jwt_required()
def private():
    # Access the identity of the current user with get_jwt_identity
    current_user_id = get_jwt_identity()

    user = User.query.filter_by(id=current_user_id).first()

    if user is None:
        return jsonify({"msg": "User does not exist"}), 404

    response_body = {
        "status": "true",
        "user": user.serialize()
    }

    return jsonify(response_body), 200

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# ----- Endpoint User -----

# Get - All Users
@app.route('/users', methods=['GET'])
def getUsers():

    users = User.query.all() 
    all_users = list(map(lambda item: item.serialize(), users))

    return jsonify(all_users), 200
# Get - One User for ID
@app.route('/users/<int:id>', methods=['GET'])
def getUser(id):

    user = User.query.filter_by(id=id).first()

    if user is not None:
        return jsonify(user.serialize()), 200
    
    # Afuera del if
    response_body = {
            "msg": "Usuario no existe"
        }
    return jsonify(response_body), 400

# Delete - User
@app.route('/users/<int:id>', methods=['DELETE'])
def deleteUser(id):
    user = User.query.filter_by(id=id).first()
    
    if user is not None:
        db.session.delete(user)
        db.session.commit()

        response_body = {
            "msg": "Eliminación correcta de Usuario"
        }
        return jsonify(response_body), 200

    # Afuera del if
    response_body = {
            "msg": "Usuario no existe"
        }
    return jsonify(response_body), 400
    
# Put - User
@app.route('/users/<int:id>', methods=['PUT'])
def putUser(id):
    body = json.loads(request.data)
    
    user = User.query.filter_by(id=id).first()
    
    if user is not None:
        user.first_name = body["first_name"]
        user.last_name = body["last_name"]
        user.email = body["email"]
        user.password = body["password"]
        user.username = body["username"]

        db.session.add(user)
        db.session.commit()

        response_body = {
            "msg": "El usuario fue modificado con exito"
        }
        return jsonify(response_body), 200

    response_body = {
            "msg": "El usuario no existe en el sistema"
        }
    return jsonify(response_body), 400

# ----- Endpoint People -----

# Get - All People
@app.route('/people', methods=['GET'])
def all_people():

    people = People.query.all() 
    all_people = list(map(lambda item: item.serialize(), people))

    return jsonify(all_people), 200

# Get - One User for ID
@app.route('/people/<int:id>', methods=['GET'])
def getPeople(id):

    people = People.query.filter_by(id=id).first()

    if people is not None:
        return jsonify(people.serialize()), 200

    # Afuera del if
    response_body = {
            "msg": "Personaje no existe"
        }
    return jsonify(response_body), 400

# Delete - People
@app.route('/people/<int:id>', methods=['DELETE'])
def deletePeople(id):
    people = People.query.filter_by(id=id).first()
    
    if people is not None:
        db.session.delete(people)
        db.session.commit()

        response_body = {
            "msg": "Eliminación correcta de Personaje"
        }
        return jsonify(response_body), 200

    # Afuera del if
    response_body = {
            "msg": "Personaje no existe"
        }
    return jsonify(response_body), 400

# Put - People
@app.route('/people/<int:id>', methods=['PUT'])
def putPeople(id):
    body = json.loads(request.data)
    
    people = People.query.filter_by(id=id).first()
    
    if people is not None:
        people.name = body["name"]
        people.height = body["height"]
        people.mass = body["mass"]
        people.hair_color = body["hair_color"]
        people.skin_color = body["skin_color"]
        people.eye_color = body["eye_color"]
        people.birth_year = body["birth_year"]
        people.gender = body["gender"]
        people.planet_id = body["planet_id"]

        db.session.add(people)
        db.session.commit()

        response_body = {
            "msg": "El personaje fue modificado con exito"
        }
        return jsonify(response_body), 200

    response_body = {
            "msg": "El personaje no existe en el sistema"
        }
    return jsonify(response_body), 400

# Post - People
@app.route('/people', methods=['POST'])
def postPeople():
    body = json.loads(request.data)
    
    people = People.query.filter_by(name=body["name"]).first() 
    
    if people is None:
        newPeople = People(name=body["name"], height=body["height"], mass=body["mass"], hair_color=body["hair_color"], skin_color=body["skin_color"], eye_color=body["eye_color"], birth_year=body["birth_year"], gender=body["gender"], planet_id=body["planet_id"])
        db.session.add(newPeople)
        db.session.commit()

        response_body = {
            "msg": "El personaje fue creado con exito"
        }
        return jsonify(response_body), 200

    response_body = {
            "msg": "El personaje ya existe en el sistema"
        }
    return jsonify(response_body), 400

# ----- Endpoint Planets -----

# Get - All Planets
@app.route('/planets', methods=['GET'])
def all_planets():

    planets = Planet.query.all() 
    all_planets = list(map(lambda item: item.serialize(), planets))

    return jsonify(all_planets), 200

# Get - One Planet for ID
@app.route('/planets/<int:id>', methods=['GET'])
def getPlanets(id):

    planet = Planet.query.filter_by(id=id).first()

    if planet is not None:
        return jsonify(planet.serialize()), 200

    # Afuera del if
    response_body = {
            "msg": "Planeta no existe"
        }
    return jsonify(response_body), 400

# Delete - Planet
@app.route('/planets/<int:id>', methods=['DELETE'])
def deletePlanet(id):
    planet = Planet.query.filter_by(id=id).first()
    
    if planet is not None:
        db.session.delete(planet)
        db.session.commit()

        response_body = {
            "msg": "Eliminación correcta de Planeta"
        }
        return jsonify(response_body), 200

    # Afuera del if
    response_body = {
            "msg": "Planeta no existe"
        }
    return jsonify(response_body), 400

# Post - Planet
@app.route('/planets', methods=['POST'])
def postPlanet():
    body = json.loads(request.data)
    
    planet = Planet.query.filter_by(name=body["name"]).first() 
    
    if planet is None:
        newPlanet = Planet(name=body["name"], diameter=body["diameter"], rotation_period=body["rotation_period"], orbital_period=body["orbital_period"], gravity=body["gravity"], population=body["population"], climate=body["climate"], terrain=body["terrain"], surface_water=body["surface_water"])
        db.session.add(newPlanet)
        db.session.commit()

        response_body = {
            "msg": "El planeta fue creado con exito"
        }
        return jsonify(response_body), 200

    response_body = {
            "msg": "El planeta ya existe en el sistema"
        }
    return jsonify(response_body), 400

# Put - Planet
@app.route('/planets/<int:id>', methods=['PUT'])
def putPlanet(id):
    body = json.loads(request.data)
    
    planet = Planet.query.filter_by(id=id).first()
    
    if planet is not None:
        planet.name = body["name"]
        planet.diameter = body["diameter"]
        planet.rotation_period = body["rotation_period"]
        planet.orbital_period = body["orbital_period"]
        planet.gravity = body["gravity"]
        planet.population = body["population"]
        planet.climate = body["climate"]
        planet.terrain = body["terrain"]
        planet.surface_water = body["surface_water"]

        db.session.add(planet)
        db.session.commit()

        response_body = {
            "msg": "El planeta fue modificado con exito"
        }
        return jsonify(response_body), 200

    response_body = {
            "msg": "El planeta no existe en el sistema"
        }
    return jsonify(response_body), 400

# ----- Endpoint Vehicle -----

# Get - All Vehicle
@app.route('/vehicles', methods=['GET'])
def all_vehicles():

    vehicles = Vehicle.query.all() 
    all_vehicles = list(map(lambda item: item.serialize(), vehicles))

    return jsonify(all_vehicles), 200

# Get - One Vehicle for ID
@app.route('/vehicles/<int:id>', methods=['GET'])
def getVehicle(id):

    vehicle = Vehicle.query.filter_by(id=id).first()

    if planet is not None:
        return jsonify(planet.serialize()), 200

    # Afuera del if
    response_body = {
            "msg": "Vehiculo no existe"
        }
    return jsonify(response_body), 400

# Delete - Planet
@app.route('/vehicles/<int:id>', methods=['DELETE'])
def deleteVehicle(id):
    vehicle = Vehicle.query.filter_by(id=id).first()
    
    if vehicle is not None:
        db.session.delete(vehicle)
        db.session.commit()

        response_body = {
            "msg": "Eliminación correcta de Vehiculo"
        }
        return jsonify(response_body), 200

    # Afuera del if
    response_body = {
            "msg": "Vehiculo no existe"
        }
    return jsonify(response_body), 400

# Post - Vehicle
@app.route('/vehicles', methods=['POST'])
def postVehicle():
    body = json.loads(request.data)
    
    vehicle = Vehicle.query.filter_by(name=body["name"]).first() 
    
    if vehicle is None:
        newVehicle = Vehicle(name=body["name"], model=body["model"],vehicle_class=body["vehicle_class"], manufacturer=body["manufacturer"], cost_in_credits=body["cost_in_credits"], length=body["length"], crew=body["crew"], passengers=body["passengers"], max_atmospheric_speed=body["max_atmospheric_speed"], cargo_capacity=body["cargo_capacity"], consumables=body["consumables"])
        db.session.add(newVehicle)
        db.session.commit()

        response_body = {
            "msg": "El vehiculo fue creado con exito"
        }
        return jsonify(response_body), 200

    response_body = {
            "msg": "El vehiculo ya existe en el sistema"
        }
    return jsonify(response_body), 400

# Put - Vehicle
@app.route('/vehicles/<int:id>', methods=['PUT'])
def putVehicle(id):
    body = json.loads(request.data)
    
    vehicle = Vehicle.query.filter_by(id=id).first()
    
    if vehicle is not None:
        vehicle.name = body["name"]
        vehicle.model =  body["model"]
        vehicle.vehicle_class = body["vehicle_class"]
        vehicle.manufacturer = body["manufacturer"]
        vehicle.cost_in_credits = body["cost_in_credits"]
        vehicle.length = body["length"]
        vehicle.crew = body["crew"]
        vehicle.passengers = body["passengers"]
        vehicle.max_atmospheric_speed = body["max_atmospheric_speed"]
        vehicle.cargo_capacity = body["cargo_capacity"]
        vehicle.consumables = body["consumables"]

        db.session.add(vehicle)
        db.session.commit()

        response_body = {
            "msg": "El vehiculo fue modificado con exito"
        }
        return jsonify(response_body), 200

    response_body = {
            "msg": "El vehiculo no existe en el sistema"
        }
    return jsonify(response_body), 400

# ----- Endpoint Favorite -----

@app.route('/favorite', methods=['GET'])
def all_Favorite():

    favorites = Favorite.query.all() 
    all_Favorites = list(map(lambda item: item.serialize(), favorites))

    return jsonify(all_Favorites), 200

# Delete - Favorite
@app.route('/favorite/<int:id>', methods=['DELETE'])
def deleteFavorite(id):
    favorite = Favorite.query.filter_by(id=id).first()
    
    if favorite is not None:
        db.session.delete(favorite)
        db.session.commit()

        response_body = {
            "msg": "Eliminación correcta de Favoritos"
        }
        return jsonify(response_body), 200

    # Afuera del if
    response_body = {
            "msg": "Favoritos no existe"
        }
    return jsonify(response_body), 400

# Get- Favorite for User
@app.route('/users/<int:id>/favorite', methods=['GET'])
def getUserFavorite(id):

    # Me fijo si existe el usuario
    user = User.query.filter_by(id=id).first()

    if user is not None:
        favorite = Favorite.query.filter_by(user_id=id).all()
        
        all_Favorite = list(map(lambda item: item.serialize(), favorite))

        return jsonify(all_Favorite), 200

    
    # Afuera del if
    response_body = {
            "msg": "Usuario no existe"
        }
    return jsonify(response_body), 400

    

# Post - Planet Favorite for User
@app.route('/users/<int:id>/favorite/planet', methods=['POST'])
def postFavoritePlanet(id):
    body = json.loads(request.data) 

    # Me fijo si existe el usuario
    user = User.query.filter_by(id=id).first()
    if user is None:
        response_body = {
            "msg": "Usuario no existe"
        }
        return jsonify(response_body), 400
    # Me fijo si existe el planeta
    planet = Planet.query.filter_by(id=body["planet_id"]).first()
    if planet is None:
        response_body = {
                "msg": "Ese planeta no existe"
            }
        return jsonify(response_body), 400
    # Me fijo si el usuario tiene ese planeta en favorito
    favoritePlanet = Favorite.query.filter_by(planet_id=body["planet_id"], user_id=id).first()
    if favoritePlanet is not None:
        response_body = {
                "msg": "Ese usuario ya cuenta con ese planeta en favorito"
            }
        return jsonify(response_body), 400
    # Agrego el planeta a favorito
    newFavorite = Favorite(user_id=id, planet_id=body["planet_id"])
    db.session.add(newFavorite)
    db.session.commit()

    response_body = {
                "msg": "Planeta agregado a favorito con Exito"
            }
    return jsonify(response_body), 200



# Post - People Favorite for User
@app.route('/users/<int:id>/favorite/people', methods=['POST'])
def postFavoritePeople(id):
    body = json.loads(request.data) 

    # Me fijo si existe el usuario
    user = User.query.filter_by(id=id).first()
    if user is None:
        response_body = {
            "msg": "Usuario no existe"
        }
        return jsonify(response_body), 400
    # Me fijo si existe el personaje
    people = People.query.filter_by(id=body["people_id"]).first()
    if people is None:
        response_body = {
                "msg": "Ese personaje no existe"
            }
        return jsonify(response_body), 400
    # Me fijo si el usuario tiene ese personaje en favorito
    favoritePeople = Favorite.query.filter_by(people_id=body["people_id"], user_id=id).first()
    if favoritePeople is not None:
        response_body = {
                "msg": "Ese usuario ya cuenta con ese personaje en favorito"
            }
        return jsonify(response_body), 400
    # Agrego el personaje a favorito
    newFavorite = Favorite(user_id=id, people_id=body["people_id"])
    db.session.add(newFavorite)
    db.session.commit()

    response_body = {
            "msg": "Personaje agregado a favorito con Exito"
            }
    return jsonify(response_body), 200


# Post - Vehicle Favorite for User
@app.route('/users/<int:id>/favorite/vehicle', methods=['POST'])
def postFavoriteVehicle(id):
    body = json.loads(request.data) 
    
    # Me fijo si existe el usuario
    user = User.query.filter_by(id=id).first()
    if user is None:
        response_body = {
            "msg": "Usuario no existe"
        }
        return jsonify(response_body), 400
    # Me fijo si existe el vehiculo
    vehicle = Vehicle.query.filter_by(id=body["vehicle_id"]).first()
    if vehicle is None:
        response_body = {
                "msg": "Ese vehiculo no existe"
            }
        return jsonify(response_body), 400
    # Me fijo si el usuario tiene ese vehiculo en favorito
    favoriteVehicle = Favorite.query.filter_by(vehicle_id=body["vehicle_id"], user_id=id).first()
    if favoriteVehicle is not None:
        response_body = {
                "msg": "Ese usuario ya cuenta con ese vehiculo en favorito"
            }
        return jsonify(response_body), 400
    # Agrego el vehiculo a favorito
    newFavorite = Favorite(user_id=id, vehicle_id=body["vehicle_id"])
    db.session.add(newFavorite)
    db.session.commit()

    response_body = {
                "msg": "Vehiculo agregado a favorito con Exito"
            }
    return jsonify(response_body), 200

# Delete - Planet Favorite for User
@app.route('/users/<int:id>/favorite/planet', methods=['DELETE'])
def deleteFavoritePlanet(id):
    body = json.loads(request.data) 
    # Me fijo si existe el usuario
    user = User.query.filter_by(id=id).first()
    if user is None:
        response_body = {
            "msg": "Usuario no existe"
        }
        return jsonify(response_body), 400
    # Me fijo si existe el planeta
    planet = Planet.query.filter_by(id=body["planet_id"]).first()
    if planet is None:
        response_body = {
                "msg": "Ese planeta no existe"
            }
        return jsonify(response_body), 400
    # Me fijo si el usuario tiene ese planeta en favorito
    favoritePlanet = Favorite.query.filter_by(planet_id=body["planet_id"], user_id=id).first()
    if favoritePlanet is None:
        response_body = {
                "msg": "Ese usuario ya no cuenta con ese planeta en favorito"
            }
        return jsonify(response_body), 400
    # Agrego el planeta a favorito
    db.session.delete(favoritePlanet)
    db.session.commit()

    response_body = {
                "msg": "Planeta eliminado de favorito con Exito"
            }
    return jsonify(response_body), 200

    

# Delete - People Favorite for User
@app.route('/users/<int:id>/favorite/people', methods=['DELETE'])
def deleteFavoritePeople(id):
    body = json.loads(request.data) 
    # Me fijo si existe el usuario
    user = User.query.filter_by(id=id).first()
    if user is None:
        response_body = {
            "msg": "Usuario no existe"
        }
        return jsonify(response_body), 400
    # Me fijo si existe el personaje
    people = People.query.filter_by(id=body["people_id"]).first()
    if people is None:
        response_body = {
                "msg": "Ese personaje no existe"
            }
        return jsonify(response_body), 400
    # Me fijo si el usuario tiene ese personaje en favorito
    favoritePeople = Favorite.query.filter_by(people_id=body["people_id"], user_id=id).first()
    if favoritePeople is None:
        response_body = {
                "msg": "Ese usuario ya no cuenta con ese personaje en favorito"
            }
        return jsonify(response_body), 400
    # Agrego el personaje a favorito
    db.session.delete(favoritePeople)
    db.session.commit()

    response_body = {
                "msg": "Personaje eliminado de favorito con Exito"
            }
    return jsonify(response_body), 200
    

# Delete - Vehicle Favorite for User
@app.route('/users/<int:id>/favorite/vehicle', methods=['DELETE'])
def deleteFavoriteVehicle(id):
    body = json.loads(request.data) 
    # Me fijo si existe el usuario
    user = User.query.filter_by(id=id).first()
    if user is None:
        response_body = {
            "msg": "Usuario no existe"
        }
        return jsonify(response_body), 400
    # Me fijo si existe el vehiculo
    vehicle = Vehicle.query.filter_by(id=body["vehicle_id"]).first()
    if vehicle is None:
        response_body = {
                "msg": "Ese vehiculo no existe"
            }
        return jsonify(response_body), 400
    # Me fijo si el usuario tiene ese vehiculo en favorito
    favoriteVehicle = Favorite.query.filter_by(vehicle_id=body["vehicle_id"], user_id=id).first()
    if favoriteVehicle is None:
        response_body = {
                "msg": "Ese usuario ya no cuenta con ese vehiculo en favorito"
            }
        return jsonify(response_body), 400
    # Agrego el vehiculo a favorito
    db.session.delete(favoriteVehicle)
    db.session.commit()

    response_body = {
                "msg": "Vehiculo eliminado de favorito con Exito"
            }
    return jsonify(response_body), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
