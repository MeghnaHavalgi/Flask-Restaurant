from app import application
from flask import jsonify, Response, session
from app.models import *
from app import *
import uuid
import datetime
from marshmallow import Schema, fields
from flask_restful import Resource, Api
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
import json

class SignUpRestService(Schema):
    username = fields.Str(default="UserName")
    password = fields.Str(Default="PassWord")
    name = fields.Str(default="Name")
    level = fields.Int(default="0")

class LoginAPIRestService(Schema):
    username = fields.Str(default="UserName")
    password = fields.Str(default="PassWord")

class AddVendorRestService(Schema):
    user_id = fields.Str(default="user_id")

class AddItemRestService(Schema):
    item_name = fields.Str(default="item_name")
    restaurant_name = fields.Str(default="restaurant_name")
    available_quantity = fields.Int(default=0)
    unit_price = fields.Float(default=0)
    calories_per_gm = fields.Float(default = 0)

class CreateItemOrderRestService(Schema):
    item_order = fields.List(fields.Dict())


class PlaceOrderRestAPI(Schema):
    order_id = fields.Str(default="order_id")


class APIResponse(Schema):
    message = fields.Str(Default = "Success")

#  Restful way of creating APIs through Flask Restful
class SignUpAPI(MethodResource, Resource):
    @doc(description = 'Sign Up API',tags=['SignUp API'])
    @use_kwargs(SignUpRestService, location=('json'))
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            levelforcheck = kwargs["level"]
            if (levelforcheck==0 or levelforcheck==1 or levelforcheck==2):
                user = User(
                    uuid.uuid4(),
                    kwargs["name"],
                    kwargs["username"],
                    kwargs["password"],
                    kwargs["level"]
                )
                db.session.add(user)
                db.session.commit()
                return APIResponse().dump(dict(message='User is successfully registered')),200
            else:
                return  APIResponse().dump(dict(message="Please choose level between 0 to 2")),404
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f"not able to register user : {str(e)}")) , 400
api.add_resource(SignUpAPI,'/signup')
docs.register(SignUpAPI)




class LoginAPI(MethodResource, Resource):
    @doc(description='Login API' , tags=['Login API'])
    @use_kwargs(LoginAPIRestService,location=('json'))
    @marshal_with(APIResponse)

    def post(self,**kwargs):
        try:
            user = User.query.filter_by(username=kwargs['username'],password=kwargs['password']).first()
            if user:
                print('User')
                session['user_id'] = user.user_id
                return APIResponse().dump(dict(message=f'{user.name} is successfully Logged In. Welcome to flask')),200
        except Exception as err:
            print(str(err))
            return APIResponse().dump(dict(message='Credential is not right please try again for login')),404


api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)

class LogoutAPI(MethodResource, Resource):
    @doc(description='Logout API',tags=['Logout API'])
    @marshal_with(APIResponse)

    def post(self,**kwargs):
        try:
            print('Logout Process Is Activated')
            if session['user_id'] is None:
                return APIResponse().dump(dict(message='Please Login You Are Already Logout')),200
            else:
                session['user_id'] = None
                return APIResponse().dump(dict(message='You Are Successfully Logout')),200

        except Exception as err:
            print('Exception Occures'+err)
            return APIResponse().dump(dict(message='Exception Occured')),404

api.add_resource(LogoutAPI, '/logout')
docs.register(LogoutAPI)


class AddVendorAPI(MethodResource, Resource):
    @doc(description='Add Vendor API', tags=['Add Vendor API'])
    @use_kwargs(AddVendorRestService, location=('json'))
    @marshal_with(APIResponse)

    def post(self,**kwargs):
        try:
            if session['user_id']:
                print("Checking Login")
                user_id = session['user_id']
                user = User.query.filter_by(user_id=user_id).first()
                if user.level == 2:
                    print("I am Admin")
                    updateuser = User.query.filter_by(user_id=kwargs['user_id']).first()
                    updateuser.level =1
                    db.session.add(updateuser)
                    db.session.commit()
                    return APIResponse().dump(dict(message="Vendor added successfully.")), 200
                else:
                    return APIResponse().dump(dict(message="You are not admin so you are not eligible to add the vendor")), 404
            else:
                print("Not Logged In")
                return APIResponse().dump(
                    dict(message="Please login first to add the vendor")), 404

        except Exception as err:
            print(str(err))
            return APIResponse().dump(dict(message="Vendor is not added successfully")),404
            

api.add_resource(AddVendorAPI, '/add_vendor')
docs.register(AddVendorAPI)


class GetVendorsAPI(MethodResource, Resource):
    @doc(description='GetVendorRestAPI',tags=['Get Vendors'])
    @marshal_with(APIResponse)

    def post(self, **kwargs):
        try:
            if session['user_id'] is None:
                return APIResponse().dump(message="Admin is not logged In Yet")
            else:
                user = User.query.filter_by(user_id=session['user_id']).first()
                if user.level == 2:
                    all_user = User.query.filter_by(level=1)
                    user_list = []
                    for index in all_user:
                        user_dict = {}
                        user_dict['name'] = index.name
                        user_dict['vendor_id'] = index.user_id
                        user_list.append(user_dict)
                    return jsonify({'vendor_data':user_list})
                else:
                    return APIResponse().dump(dict(message="Only Admin Can View Vendors Details")), 404

        except Exception as err:
            return APIResponse().dump(dict(message="Operation Failed. Try To Logged In Again")), 404







api.add_resource(GetVendorsAPI, '/list_vendors')
docs.register(GetVendorsAPI)

class AddItemAPI(MethodResource, Resource):
    @doc(description="Add Item API",tags=['Add Item'])
    @use_kwargs(AddItemRestService,location=('json'))
    @marshal_with(APIResponse)

    def post(self,**kwargs):
        try:
            if session['user_id'] is None:
                return APIResponse().dump(dict(message="Vendor Needs To Be Login First To Add The Item")) , 400
            else:
                user_access_verification = User.query.filter_by(user_id=session['user_id']).first()
                if user_access_verification.level == 1:
                    item = Item(uuid.uuid4(),session['user_id'],kwargs['item_name'],kwargs['calories_per_gm'],kwargs['available_quantity'],kwargs['restaurant_name'],kwargs['unit_price'])
                    db.session.add(item)
                    db.session.commit()
                    return APIResponse().dump(dict(message="Item Added Successfully")) , 200
                else:
                    return APIResponse().dump(dict(message="Only Vendor Can Add The Item")) , 400

        except Exception as err:
            print(str(err))
            return APIResponse().dump(dict(message="Operation Failed Try To Login Again"))



api.add_resource(AddItemAPI, '/add_item')
docs.register(AddItemAPI)


class ListItemsAPI(MethodResource, Resource):
    @doc(description="List All Items",tags=['List All Items'])
    @marshal_with(APIResponse)

    def post(self, **kwargs):
        try :
            if session['user_id']:
                all_items = Item.query.filter_by(is_active=1)
                all_item_list = []
                for index in all_items:
                    item_dict = {}
                    item_dict['item_id']=index.item_id
                    item_dict['vendor_id'] = index.vendor_id
                    item_dict['item_name'] = index.item_name
                    item_dict['calories_per_gm'] = index.calories_per_gm
                    item_dict['available_quantity'] = index.available_quantity
                    item_dict['restaurant_name'] = index.restaurant_name
                    item_dict['unit_price'] = index.unit_price
                    all_item_list.append(item_dict)
                return jsonify({'All_Items':all_item_list})
            else:
                return APIResponse().dump(dict(message="Please Login First To View Items"))
        except Exception as err:
            print(str(err))
            return APIResponse().dump(dict(message="Operation Failed Try To Login Again"))
api.add_resource(ListItemsAPI, '/list_items')
docs.register(ListItemsAPI)


class CreateItemOrderAPI(MethodResource, Resource):
    @doc(description="Create Item Order API", tags=['Create Item Order API'])
    @use_kwargs(CreateItemOrderRestService, location=('json'))
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id'] is None:
                return APIResponse().dump(dict(message="Customer Needs To Be Login First To Add The Order Item")), 400
            else:
                user_access_verification = User.query.filter_by(user_id=session['user_id']).first()
                if user_access_verification.level == 0:
                    order_id = uuid.uuid4()
                    order = Order(order_id,session['user_id'])
                    db.session.add(order)
                    for place in kwargs['item_order']:
                        dict_place = dict(place)
                        check_item = Item.query.filter_by(item_id=dict_place['item_id'], is_active=1).first()
                        if check_item:
                            order_item = OrderItems(uuid.uuid4(), order_id, dict_place['item_id'], dict_place['quantity'])
                            db.session.add(order_item)
                        else:
                            return APIResponse().dump(dict(message="Item Is Not Available")), 200

                    db.session.commit()
                    return APIResponse().dump(dict(message="Order Item Added Successfully")), 200
                else:
                    return APIResponse().dump(dict(message="Only Customer Can Place The Order Item")), 400

        except Exception as err:
            print(str(err))
            return APIResponse().dump(dict(message="Operation Failed Try To Login Again"))


api.add_resource(CreateItemOrderAPI, '/create_items_order')
docs.register(CreateItemOrderAPI)


class PlaceOrderAPI(MethodResource, Resource):
    @doc(description="Create Item Order API", tags=['Create Item Order API'])
    @use_kwargs(PlaceOrderRestAPI, location=('json'))
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id'] is None:
                return APIResponse().dump(dict(message="Customer Needs To Be Login First To Add The Order Item")), 400
            else:
                user_access_verification = User.query.filter_by(user_id=session['user_id']).first()
                if user_access_verification.level == 0:
                    order_item_data = OrderItems.query.filter_by(order_id=kwargs['order_id'],is_active=1)
                    order_data = Order.query.filter_by(order_id=kwargs['order_id'],user_id=session['user_id'],is_active=1).first()
                    if order_data:
                        if order_data.is_placed == 1:
                            return APIResponse().dump(dict(message="Your Order Was Already Placed Successfully")), 400
                        else:
                            total_amount = 0
                            for order_item_val in order_item_data:
                                item_data = Item.query.filter_by(item_id=order_item_val.item_id,is_active=1).first()
                                total_amount += order_item_val.quantity * item_data.unit_price
                                if item_data.available_quantity >= order_item_val.quantity:
                                    item_data.available_quantity =  item_data.available_quantity - order_item_val.quantity
                                else:
                                    return APIResponse().dump(dict(message="Insufficient Item")), 400


                            order_data.total_amount = total_amount
                            order_data.is_placed = 1
                            db.session.add(item_data)
                            db.session.add(order_data)
                            db.session.commit()
                            return APIResponse().dump(dict(message="Your Order Placed Successfully")), 200
                    else:
                        return APIResponse().dump(dict(message="Selected Order Is Not Belongs To The Logged In Customer Please Login With Correct User")), 400

                else:
                    return APIResponse().dump(dict(message="Only Customer Can Place The Order Item")), 400
        except Exception as err:
            print(str(err))
            return APIResponse().dump(dict(message="Operation Failed Try To Login Again"))


api.add_resource(PlaceOrderAPI, '/place_order')
docs.register(PlaceOrderAPI)

class ListOrdersByCustomerAPI(MethodResource, Resource):
    @doc(description="List Logged In Customer Order API", tags=['List Customer Order'])
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id'] is None:
                return APIResponse().dump(dict(message="Customer Needs To Be Login First To View The Order")), 400
            else:
                user_access_verification = User.query.filter_by(user_id=session['user_id']).first()
                if user_access_verification.level == 0:
                    all_cust_orders = Order.query.filter_by(user_id = session['user_id'],is_placed=1,is_active=1)

                    order_list = []
                    for single_order in all_cust_orders:
                        individaul_order = {}
                        order_item_dict = {}
                        order_item = []
                        individaul_order['order_id']=single_order.order_id
                        individaul_order['total_amount']=single_order.total_amount
                        order_item_data = OrderItems.query.filter_by(order_id = single_order.order_id)
                        for index in order_item_data:
                            order_item_dict['item_id'] = index.item_id
                            order_item_dict['quantity'] = index.quantity
                            order_item.append(order_item_dict)
                        individaul_order['items'] = order_item
                        order_list.append(individaul_order)
                    return jsonify({"my_orders":order_list})
                else:
                    return APIResponse().dump(dict(message="Only Customer Have The Orders")), 400

        except Exception as err:
            print(str(err))
            return APIResponse().dump(dict(message="Operation Failed Try To Login Again"))
            

api.add_resource(ListOrdersByCustomerAPI, '/list_orders')
docs.register(ListOrdersByCustomerAPI)


class ListAllOrdersAPI(MethodResource, Resource):
    @doc(description="List All Customer Order API", tags=['List All Customer Order'])
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id'] is None:
                return APIResponse().dump(dict(message="Admin Needs To Be Login First ")), 400
            else:
                user_access_verification = User.query.filter_by(user_id=session['user_id']).first()
                if user_access_verification.level == 2:
                    all_cust_orders = Order.query.filter_by(is_active=1)


                    order_list = []
                    for single_order in all_cust_orders:
                        order_item_dict = {}
                        individaul_order = {}
                        order_item = []
                        individaul_order['user_id']=single_order.user_id
                        customer_data = User.query.filter_by(user_id=single_order.user_id).first()
                        individaul_order['username']=customer_data.username
                        individaul_order['name']=customer_data.name
                        individaul_order['order_id'] = single_order.order_id
                        individaul_order['total_amount'] = single_order.total_amount
                        order_item_data = OrderItems.query.filter_by(order_id=single_order.order_id)
                        for index in order_item_data:
                            order_item_dict['item_id'] = index.item_id
                            order_item_dict['quantity'] = index.quantity
                            order_item.append(order_item_dict)
                        individaul_order['items'] = order_item
                        order_list.append(individaul_order)
                    return jsonify({"my_orders": order_list})
                else:
                    return APIResponse().dump(dict(message="Only Admin Can View All The Orders")), 400

        except Exception as err:
            print(str(err))
            return APIResponse().dump(dict(message="Operation Failed Try To Login Again"))
            
api.add_resource(ListAllOrdersAPI, '/list_all_orders')
docs.register(ListAllOrdersAPI)