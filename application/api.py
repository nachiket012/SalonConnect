from flask_restful import Resource, reqparse
from application import db, myapi
from application.models import Users, employees, shopowners, Service_Queue, Messages, Servicelist
from flask import request


class TableApi(Resource):
    def get(self, name):

        if name == "Users":
            users = db.session.query(Users).order_by(Users.user_id.asc()).all()
            r = {}
            for user in users:
                r[user.user_id] = {
                    "user_id": user.user_id,
                    "name": user.name,
                    "email": user.email,
                    "address": user.address,
                    "password": user.password,
                    "phone": user.phone,
                    "age": user.Age
                }
            return r
        elif name == "messages":
            table = db.session.query(Messages).all()
            r = {}
            for value in table:
                r[value.email] = {
                    "name": value.name,
                    "email": value.email,
                    "message": value.message,
                    "date_time": str(value.date_time)
                }
            return r
        elif name == "employees":
            table = db.session.query(employees).all()
            r = {}
            for value in table:
                r[value.EID] = {
                    "EID": value.EID,
                    "name": value.name,
                    "shop_id": value.shop_id,
                    "Services": value.Services
                }
            return r
        elif name == "Service_Queue":
            table = db.session.query(Service_Queue).all()
            r = {}
            for value in table:
                r[value.Rank] = {
                    "Rank": value.Rank,
                    "Service": value.Service,
                    "Customer": value.Customer,
                    "Shop": value.Shop,
                    "date_time": str(value.date_time),
                    "rating": value.rating,
                    "done": value.done
                }
            return r
        elif name == "shopowners":
            table = db.session.query(shopowners).all()
            r = {}
            for value in table:
                r[value.shop_id] = {
                    "shop_id": value.shop_id,
                    "shop_name": value.shop_name,
                    "owner_name": value.owner_name,
                    "phone": value.phone,
                    "Address": value.Address,
                    "open": str(value.open),
                    "close": str(value.close),
                    "rating": value.rating
                }
            return r
        
        elif name == "Services":
            table = db.session.query(Servicelist).all()
            r = {}
            for value in table:
                r[value.id] = {
                    "service": value.Service,
                    "shop_id": value.shop_id,
                    "price": value.Price,
                    "time": value.time,
                    "id": value.id
                }
            return r
        
        
        else:
            return {"error": "bad request"}
        
    def post(self, name):
        pass
        
        
myapi.add_resource(TableApi, "/api/<string:name>")
