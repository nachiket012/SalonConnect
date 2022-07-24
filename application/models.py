from application import db


class Users(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(30))
    phone = db.Column(db.Integer)
    Age = db.Column(db.Integer)
    email = db.Column(db.String(30))
    password = db.Column(db.String(30))


class employees(db.Model):
    __tablename__ = 'employees'
    EID = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(30))
    shop_id = db.Column(db.String(30))
    Services = db.Column(db.String(30))


class shopowners(db.Model):
    __tablename__ = 'shopowners'
    shop_id = db.Column(db.String(30), primary_key=True)
    shop_name = db.Column(db.String(30), nullable=False)
    services = db.Column(db.String())
    owner_name = db.Column(db.String(30))
    phone = db.Column(db.Integer)
    Address = db.Column(db.String(30))
    open = db.Column(db.DateTime)
    close = db.Column(db.DateTime)
    rating = db.Column(db.Float)
    city = db.Column(db.String(30))
    img = db.Column(db.String(30), default = "https://mdbcdn.b-cdn.net/img/new/standard/nature/111.webp")
    pwd = db.Column(db.String(30))


class Service_Queue(db.Model):
    __tablename__ = 'Service_Queue'
    Rank = db.Column(db.String(30), primary_key=True)
    Service = db.Column(db.String(30), nullable=False)
    Customer = db.Column(db.String(30))
    Shop = db.Column(db.String(30))
    date_time = db.Column(db.DateTime)
    rating = db.Column(db.Integer())
    done = db.Column(db.Boolean())


class Messages(db.Model):
    __tablename__ = 'messages'
    name = db.Column(db.String(30))
    email = db.Column(db.String(30), primary_key=True)
    message = db.Column(db.String())
    date_time = db.Column(db.DateTime)


class Servicelist(db.Model):
    __tablename__ = 'Available_Services'
    Service = db.Column(db.String(30))
    shop_id = db.Column(db.String(30))
    Price = db.Column(db.Integer())
    time = db.Column(db.Integer())
    id = db.Column(db.Integer(), primary_key=True)

