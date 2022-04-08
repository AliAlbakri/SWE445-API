import flask
import os
from flask import request, send_from_directory, render_template
from bson import json_util, ObjectId
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient
import json
import datetime
from hashlib import sha256

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


api = Api(app)
db_username = 'adveneerice'
db_password = 'adveneerice123'
db_name = 'adveneericeDB'
cluster = MongoClient(
    'mongodb+srv://adveneerice:adveneerice123@cluster0.blq7j.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')


db = cluster['SWE445']
user_collection = db['ecommerce-khobar']




class test(Resource):

    def post(self):

        obj = {'name':'ali'}

        id = user_collection.insert_one(obj).inserted_id

        print(id)
        return str(id),200






api.add_resource(test,'/post')

if __name__ == "__main__":
    app.run(debug=True)

