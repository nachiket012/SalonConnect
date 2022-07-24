from flask import render_template, request, redirect, make_response
from sqlalchemy import func

from application import app, db
from application.models import Users, employees, shopowners, Service_Queue, Messages, Servicelist

import datetime
import random
import base64







def cookie():
    return db.session.query(Users.name).filter(Users.email == request.cookies.get("logged")).scalar()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        shops = db.session.query(shopowners).order_by(shopowners.rating.desc()).all()
        return render_template("home.html", shops=shops)

    else:
        searchcity = request.form['city']
        shops = db.session.query(shopowners).filter(shopowners.city == searchcity).order_by(
            shopowners.rating.asc()).limit(5).all()
        return render_template("home.html", shops=shops)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if cookie():
            return redirect("/services")
        return render_template("login.html")

    if request.method == "POST":
        email = request.form['email']
        raw_pass = request.form['password']
        enc_pass = base64.b64encode(raw_pass.encode("ascii")).decode("ascii")
        rem = request.form.get('remember')
        user_emails = []
        user_passwords = []
        # print(list(db.session.query(Users.email, Users.password).all()))
        for i in db.session.query(Users.email, Users.password).all():
            user_emails.append(i.email)
            user_passwords.append(i.password)
        if email in user_emails and enc_pass in user_passwords:
            resp = make_response((redirect("/services")))
            if rem:
                resp.set_cookie(key="logged", value=email, expires=datetime.datetime.now() + datetime.timedelta(days=7))
            else:
                resp.set_cookie(key="logged", value=email)
            return resp
        return "no"


@app.route("/signout")
def signout():
    resp = make_response((redirect("/")))
    resp.delete_cookie('logged')
    return resp


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        raw_pass = request.form['password']
        phone = int(request.form['phone'])
        enc_pass = base64.b64encode(raw_pass.encode("ascii")).decode("ascii")
        uid = "U" + str(random.randint(1000, 9999))
        user = Users(user_id=uid, name=name, address=address, email=email, password=enc_pass, phone=phone)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")


@app.route("/contactus", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")
    else:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        date_time = datetime.datetime.now()
        msg = Messages(name=name, email=email, message=message, date_time=date_time)
        db.session.add(msg)
        db.session.commit()
        return redirect("/")


@app.route("/services", methods=["GET", "POST"])
def services():
    if request.method == "GET":
        shops = db.session.query(shopowners).all()
        return render_template("/services.html", shops=shops)
    else:
        if request.form.get('shop_view'):  # going to booking
            if cookie():
                shopid = request.form.get('shop_view')
                shop = db.session.query(shopowners).filter(shopowners.shop_id == shopid).scalar()
                serviceslist = db.session.query(Servicelist).filter(Servicelist.shop_id == shopid).all()
                mapped = {}
                for i in serviceslist:
                    mapped[i.Service] = {"time": 0, "price": 0}
                for serv in mapped:
                    mapped[serv]["price"] = db.session.query(Servicelist.Price).filter(Servicelist.shop_id == shopid,
                                                                                       Servicelist.Service == serv).scalar()
                    for i in db.session.query(Service_Queue).filter(Service_Queue.Shop == shopid,
                                                                    Service_Queue.Service == serv,
                                                                    Service_Queue.done == False):
                        mapped[serv]["time"] += db.session.query(Servicelist.time).filter(Servicelist.shop_id == shopid,
                                                                                          Servicelist.Service == serv).scalar()

                return render_template('/booking.html', shop=shop, mapped=mapped, services=serviceslist)
            else:
                return redirect("/login")


        else:  # after booking
            booked_shop = request.form.get('shop')
            booked_service = request.form.get('service')
            uid = db.session.query(Users.user_id).filter(Users.name == cookie()).scalar()
            lastrank = db.session.query(func.max(Service_Queue.Rank)).scalar()
            newbooking = Service_Queue(Rank=lastrank + 1, Service=booked_service, Customer=uid, Shop=booked_shop,
                                       date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), done=False)
            db.session.add(newbooking)
            db.session.commit()
            return redirect("/dashboard")


@app.route("/dashboard", methods=['GET', 'POST'])
def dash():
    if request.method == "GET":
        user = db.session.query(Users).filter(Users.name == cookie()).scalar()
        doneservices = {}
        servicelist = db.session.query(Service_Queue).filter(Service_Queue.Customer == user.user_id).all()
        for i in servicelist:
            if i.done and not i.rating:
                doneservices[i.Rank] = {
                    "Service": None,
                    "Shopname": None,
                    "time": None
                }
        for i in servicelist:
            if i.done and not i.rating:
                doneservices[i.Rank]["Service"] = i.Service
                doneservices[i.Rank]["Shopname"] = db.session.query(shopowners.shop_name).filter(
                    shopowners.shop_id == i.Shop).scalar()
                doneservices[i.Rank]['time'] = i.date_time
        return render_template("/user_dashboard.html", user=user, services=doneservices)
    if request.method == "POST":
        # pushing rating into Service_Queue
        rating = int(request.form['rating'])
        rank = int(request.form['rank'])
        print(rating)
        sq = Service_Queue.query.filter_by(Rank=rank).first()
        sq.rating = rating
        db.session.commit()
        # calculating rating avg and pushing into shopowners
        listings = db.session.query(Service_Queue.rating, Service_Queue.Shop).all()
        ratingdict = {}
        for listing in listings:
            ratingdict[listing.Shop] = {
                "sum": 0,
                "count": 0,
                "average": 0
            }
        for listing in listings:
            if listing.rating:
                ratingdict[listing.Shop]["sum"] += listing.rating
                ratingdict[listing.Shop]["count"] += 1
        for shop in ratingdict:
            if ratingdict[shop]["count"]:
                a = ratingdict[shop]["sum"] / ratingdict[shop]["count"]
            print("A IS:")
            print(a)
            print("TYPE OF A IS:")
            print(type(a))
            ratingdict[shop]["average"] = a
        for listing in listings:
            sh = shopowners.query.filter_by(shop_id=listing.Shop).first()
            sh.rating = ratingdict[listing.Shop]["average"]
            db.session.commit()
        return redirect("#")


@app.route("/shopregistration", methods=["GET", "POST"])
def shopsignup():
    if request.method == "GET":
        return render_template("shopsignup.html")
    else:
        if request.form.get('phone'):
            name = request.form['name']
            address = request.form['address']
            ownername = request.form['ownername']
            sservices = request.form['services']
            phone = request.form['phone']
            sopen = request.form['open']
            city = request.form['city']
            sclose = request.form['close']
            img = request.form['img']
            sid = "S" + str(random.randint(1000, 9999))
            shop = shopowners(img=img, city=city, phone=phone, shop_id=sid, shop_name=name, Address=address,
                              services=sservices, owner_name=ownername, open=sopen, close=sclose)
            db.session.add(shop)
            db.session.commit()
            return render_template("/servicereg.html", sid=sid)

        else:
            service = request.form['service']
            time = request.form['time']
            price = request.form['price']
            sid = request.form['sid']
            service = Servicelist(Service=service, time=time, Price=price, shop_id=sid)
            db.session.add(service)
            db.session.commit()
            return redirect("#")



@app.route("/shopdashboard/<string:sid>", methods=['GET', 'POST'])
def shopd(sid):
    if request.method == "GET":
        servque = db.session.query(Service_Queue).filter(Service_Queue.Shop == sid, Service_Queue.done == False).all()
        print(servque)
        curr_shop = db.session.query(shopowners).filter(shopowners.shop_id == sid).scalar()
        print(curr_shop.shop_name)
        for shop in servque:
            print(shop.Service)
        return render_template("/shopdashboard.html", servque=servque, shop=curr_shop, sid=sid)

    if request.method == "POST":
        rank = request.form['rank']
        print(rank)
        sq = Service_Queue.query.filter_by(Rank=rank).first()
        sq.done = True
        db.session.commit()
        return redirect("#")



@app.route("/update/<string:uid>", methods=["GET", "POST"])
def updateuser(uid):
    if request.method == "POST":
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        phone = int(request.form['phone'])
        user = Users.query.filter_by(user_id=uid).first()
        if name:
            user.name = name
        if address:
            user.address = address
        if phone:
            user.phone = phone
        if email:
            user.email = email
        db.session.commit()
        return "ok"

    else:
        user = db.session.query(Users).filter(Users.user_id == uid).first()
        return render_template("/userupdate.html", user=user)



@app.route("/shopupdate/<string:sid>", methods=["GET", "POST"])
def updateshop(sid):
    if request.method == "POST":
        sname = request.form['sname']
        address = request.form['address']
        city = request.form['city']
        sopen = request.form['open']
        sclose = request.form['close']
        ownername = request.form['ownername']
        phone = request.form['phone']
        if phone:
            phone = int(phone)
        shop = shopowners.query.filter_by(shop_id=sid).first()
        if sname:
            shop.shop_name = sname
        if address:
            shop.Address = address
        if sopen:
            shop.open = sopen
        if sclose:
            shop.close = sclose
        if ownername:
            shop.owner_name = ownername
        if city:
            shop.city = city
        if phone:
            shop.phone = phone
        db.session.commit()
        return redirect("#")

    else:
        thisshop = db.session.query(shopowners).filter(shopowners.shop_id == sid).first()
        return render_template("/shopupdate.html", shop=thisshop)


@app.route("/shoplogin", methods = ["GET", "POST"])
def shoplogin():
    if request.method == "GET":
        return render_template("/shoplogin.html")
    else:
        ph = request.form['phone']
        pwd = request.form['pwd']
        sid = db.session.query(shopowners.shop_id).filter(shopowners.phone == ph, shopowners.pwd == pwd).scalar()
        print(sid)
        servque = db.session.query(Service_Queue).filter(Service_Queue.Shop == sid, Service_Queue.done == False).all()
        curr_shop = db.session.query(shopowners).filter(shopowners.shop_id == sid).scalar()
        return render_template("/shopdashboard.html", servque=servque, shop=curr_shop, sid=sid)
    