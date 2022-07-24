from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['CAHCE-TYPE'] = 'Simple'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://jxjioubelfaypi:ff76880201fb9c9921d46054c75e292c1cc555b8c60e4ca0ffe30d312f655ecd@ec2-34-207-12-160.compute-1.amazonaws.com:5432/dbqi6ds9f4cq86"
# cache = Cache(app)
db = SQLAlchemy(app)
myapi = Api(app)

from application import controllers, api
