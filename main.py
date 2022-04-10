import flask
import os
from flask import request, send_from_directory, render_template
from bson import json_util, ObjectId
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
import json
import datetime
import hashlib
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity

# these are necessary decorations , do not tech them please
app = flask.Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')


@app.route('/')
@app.route('/home')
def home():
    return render_template('endpoints.html')



# the fun starts here .....

jwt = JWTManager(app) # initialize JWTManager
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1) # define the life span of the token


api = Api(app)
db_username = 'adveneerice'
db_password = 'adveneerice123'
db_name = 'adveneericeDB'
cluster = MongoClient(
    'mongodb+srv://adveneerice:adveneerice123@cluster0.blq7j.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')


db = cluster['SWE445']
user_collection = db['Users']
shopping_cart_collection = db['Shopping_cart']





class Profile(Resource):

    @jwt_required()
    def get(self):
        ## needs to sent authorization body with the request

        current_user = get_jwt_identity()  # Get the identity of the current user
        user_from_db = user_collection.find_one({'email': current_user})

        if user_from_db:
            del user_from_db['_id'], user_from_db['password']  # delete data we don't want to return
            return user_from_db, 200
        else:
            return {'msg': 'Profile not found'}, 404



    def post(self):
        # needs to capture ccv
        # {'email':'',
        #  "password":"",
        #  "confirmed_password":"",
        #  "fname":"",
        #  "lname":"",
        #  "country": "",
        #  "city": "",
        #  "address": "",
        #  "card_number": "encrypt it",
        #  "expiry_date": ""
        #  }

        new_user = request.get_json()  # store the json body request
        doc = user_collection.find_one({"email": new_user["email"]})  # check if user exist

        if not doc:

            if new_user['password'] != new_user['confirmed_password']:
                return {'msg': 'passwords are inconsistent'}, 409
            else:

                del new_user['confirmed_password'],new_user['ccv']
                new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()  # encrpt password
                new_user["card_number"] = hashlib.sha256(new_user["card_number"].encode("utf-8")).hexdigest()  # encrpt card
                user_collection.insert_one(new_user)
                return {'msg': 'User created successfully'}, 201
        else:
            return {'msg': 'user is already exists'}, 409




class Login(Resource):


    def post(self):
        login_details = request.get_json()  # store the json body request
        user_from_db = user_collection.find_one({'email': login_details['email']})  # search for user in database

        if user_from_db:
            encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
            if encrpted_password == user_from_db['password']:
                access_token = create_access_token(identity=user_from_db['email'])  # create jwt token
                return {"access_token": access_token}, 200

            return {'msg': 'The email or password is incorrect'}, 401




class ShoopingCart(Resource):


    def post(self):
        user_cart = request.get_json()  # store the json body request

        items_arr = user_cart['items']
        total_bill_amount = 0

        for item in items_arr :
            item['total_price'] = int(item['item_price'] )* int(item['quantity'])

        for item in items_arr :
            total_bill_amount += int(item['total_price'])

        user_cart['total_bill'] = total_bill_amount

        shopping_cart_collection.insert_one(user_cart)

        return {"msg":'items have been purchased successfully '},200

















api.add_resource(ShoopingCart,'/checkout')


api.add_resource(Login,'/login')
api.add_resource(Profile,'/sign_up','/get_profile')





#utilities

def getProfile(current_user):
    #needs to sent authorization body with the request
        user_from_db = user_collection.find_one({'email': current_user})

        if user_from_db:
            del user_from_db['password']  # delete data we don't want to return
            return user_from_db
        else:
            return None

if __name__ == "__main__":
    app.run(debug=True)

