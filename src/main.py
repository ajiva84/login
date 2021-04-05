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
from models import db, User
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route("/login", methods=["POST"])
def login():

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

        
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    

    if not email:
        return jsonify({"msg": "Missing email paramter"}), 400
    if not password:
        return jsonify({"msg": "Missing password paramter"}), 400

    try:
        user = User.query.filter_by(email=email).first()
        if user.validate(password):
            db.session.commit()
            expires = datetime.timedelta(days=7)
            response_msg = {
                "user":user.serialize(),
            }
            status_code = 200
        else:
            raise Exception("Failed to login. Check your email and password.")

    except Exception as e:
        response_msg = {
            "msg": str(e),
            "status": 401
        }
        status_code = 401


    return jsonify(response_msg), status_code

@app.route("/protected", methods=["GET"])
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify( {
        
        "logged_in_as": current_user,
        "msg": "Access Granted to protected route"
        }), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
