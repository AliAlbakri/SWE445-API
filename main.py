

db = cluster['SWE445']
user_collection = db['Users']
shopping_cart_collection = db['Shopping_cart']
items_collection = db['items']







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
        # needs to capture ccvvv
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

                if 'cvv' in new_user:
                    del new_user['cvv']
                del new_user['confirmed_password']
                new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()  # encrpt password
                new_user["card_number"] = hashlib.sha256(new_user["card_number"].encode("utf-8")).hexdigest()  # encrpt card number
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
        user_cart = request.get_json()  #   store the json body request ddddd

        items_arr = user_cart['items']
        total_bill_amount = 0

        for item in items_arr :
            item['total_price'] = int(item['item_price'] )* int(item['quantity'])

        for item in items_arr :
            total_bill_amount += int(item['total_price'])

        user_cart['total_bill'] = total_bill_amount

        # assuming cvv has been sent to the gateway
        del user_cart['cvv']

        shopping_cart_collection.insert_one(user_cart)

        return {"msg":'items have been purchased successfully'},200







class Search(Resource):

    def get(self):
        search_query = request.args.get('search_query')
        items_pointer =  items_collection.find({'name':{'$regex':search_query,'$options' : 'i'}})
        item_arr = []
        for item in items_pointer:
            item_arr.append(getJsonProfile(item))

        print(item_arr)


        return item_arr,200






class Items(Resource):
    def post(self):
        item_added = request.get_json()

        items_collection.insert_one(item_added)

        return {"msg":"adding completed"},200








api.add_resource(Search,'/search_items')

api.add_resource(Items,'/add_item')


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



def getJsonProfile(mongo_user):
    return json.loads(json_util.dumps(mongo_user))

if __name__ == "__main__":
    app.run(debug=True)

