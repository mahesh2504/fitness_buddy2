import datetime

from bson import ObjectId
from flask import Flask, render_template, request, redirect, session
import pymongo
conn = pymongo.MongoClient("mongodb://localhost:27017/")
my_database = conn["my_fitness_buddy"]
admin_collection = my_database["admin"]
gym_trainers_collection = my_database["gym_trainers"]
gym_sessions_collection = my_database["sessions"]
members_collection = my_database["members"]
enrollments_collections = my_database['enrollments']
gym_trainees_collection = my_database["gym_trainees"]
payments_collection = my_database['payments']
attendance_collection = my_database['attendance']


app = Flask(__name__)
app.secret_key = "from_spices_to_insights"

query = {}
count = admin_collection.count_documents(query)
if count == 0:
    query = {"username": "admin", "password": "admin"}
    admin_collection.insert_one(query)




@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action",methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = admin_collection.count_documents(query)
    if count > 0:
        admin = admin_collection.find_one(query)
        session['admin_id'] = str(admin['_id'])
        session['role'] = "admin"
        return redirect("/admin_home")
    else:
        return render_template("main_message.html", message="Invalid Login")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/admin_logout")
def admin_logout():
    return redirect("/")


@app.route("/gym_trainer")
def gym_trainer():
    message = request.args.get("message")
    query = {}
    gym_trainers = gym_trainers_collection.find(query)
    gym_trainers = list(gym_trainers)
    return render_template("gym_trainer.html", gym_trainers=gym_trainers, message=message)


@app.route("/gym_trainer_action", methods=['post'])
def gym_trainer_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    ssn = request.form.get("ssn")
    date_of_birth = request.form.get("date_of_birth")
    state = request.form.get("state")
    address = request.form.get("address")
    zip_code = request.form.get("zip_code")
    experience = request.form.get("experience")
    query = {"email": email, "phone": phone}
    count = gym_trainers_collection.count_documents(query)
    if count == 0:
        query = {"first_name": first_name, "last_name": last_name, "email": email, "password": password, "phone": phone, "ssn": ssn, "date_of_birth": date_of_birth, "state": state, "address": address, "zip_code": zip_code, "experience": experience, "is_logged": False}
        gym_trainers_collection.insert_one(query)
        return redirect("gym_trainer?message=Gym trainer is added successfully")
    else:
        return redirect("gym_trainer?message=Gym trainer  email or phone number is already exists")


@app.route("/view_gym_trainee")
def view_gym_trainee():
    query = {}
    gym_trainees = gym_trainees_collection.find(query)
    gym_trainees = list(gym_trainees)
    return render_template("view_gym_trainee.html", gym_trainees=gym_trainees)


@app.route("/gym_trainer_login")
def gym_trainer_login():
    return render_template("gym_trainer_login.html")


@app.route("/gym_trainer_login_action", methods=['post'])
def gym_trainer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = gym_trainers_collection.count_documents(query)
    if count > 0:
        gym_trainer = gym_trainers_collection.find_one(query)
        if gym_trainer['is_logged']:
            session['gym_trainer_id'] = str(gym_trainer['_id'])
            session['role'] = "gym_trainer"
            return redirect("/gym_trainer_home")
        else:
            return render_template("change_password.html", gym_trainer_id=gym_trainer['_id'])
    else:
        return render_template("main_message.html", message="Invalid Login")


@app.route("/change_password_action", methods=['post'])
def change_password_action():
    gym_trainer_id = request.form.get("gym_trainer_id")
    password = request.form.get("password")
    conform_password = request.form.get("conform_password")
    if password != conform_password:
        return render_template("message.html", message="Password is not matched")
    query1 = {"_id": ObjectId(gym_trainer_id)}
    query2 = {"$set": {"password": password, "is_logged": True}}
    gym_trainers_collection.update_one(query1, query2)
    gym_trainers = gym_trainers_collection.find(query)
    gym_trainers = list(gym_trainers)
    session['gym_trainer_id'] = str(gym_trainers['_id'])
    session['role'] = "gym_trainer"
    return redirect("/gym_trainer_home")



@app.route("/gym_trainer_home")
def gym_trainer_home():
    gym_trainer_id = session['gym_trainer_id']
    query = {"_id": ObjectId(gym_trainer_id)}
    gym_trainer = gym_trainers_collection.find_one(query)
    return render_template("gym_trainer_home.html", gym_trainer=gym_trainer)


@app.route("/sessions")
def sessions():
    if session['role'] == 'gym_trainer':
        gym_trainer_id = session['gym_trainer_id']
    elif session['role'] == 'gym_trainee':
        gym_trainer_id = request.args.get("gym_trainer_id")
    message = request.args.get("message")
    query = {"gym_trainer_id": ObjectId(gym_trainer_id)}
    gym_sessions = gym_sessions_collection.find(query)
    gym_sessions = list(gym_sessions)
    print(gym_sessions)
    return render_template("sessions.html", gym_sessions=gym_sessions, count=count, is_gym_trainee_enrolled=is_gym_trainee_enrolled, set_enrolled_count_by_session_id=set_enrolled_count_by_session_id, message=message, int=int)
def is_gym_trainee_enrolled():
    gym_trainee_id = session['gym_trainee_id']
    query = {"gym_trainee_id": ObjectId(gym_trainee_id), "status": "enrolled"}
    count = enrollments_collections.count_documents(query)
    if count > 0:
        return True
    else:
        return False


@app.route("/sessions_action", methods=['post'])
def sessions_action():
    session_start_date = request.form.get("session_start_date")
    session_start_date = datetime.datetime.strptime(session_start_date, "%Y-%m-%d")
    session_end_date = request.form.get("session_end_date")
    session_end_date = datetime.datetime.strptime(session_end_date, "%Y-%m-%d")
    start_time_on_day = request.form.get("start_time_on_day")
    start_time_on_day = datetime.datetime.strptime(start_time_on_day, "%H:%M")
    end_time_on_day = request.form.get("end_time_on_day")
    end_time_on_day = datetime.datetime.strptime(end_time_on_day, "%H:%M")
    number_of_seats = request.form.get("number_of_seats")
    price = request.form.get("price")
    about_session = request.form.get("about_session")
    objective = request.form.get("objective")
    gym_trainer_id = session['gym_trainer_id']
    query = {"session_start_date": session_start_date, "session_end_date": session_end_date}
    count = gym_sessions_collection.count_documents(query)
    if count == 0:
        query = {"session_start_date": session_start_date, "session_end_date": session_end_date, "start_time_on_day": start_time_on_day, "end_time_on_day": end_time_on_day, "number_of_seats": number_of_seats, "price": price, "about_session": about_session, "objective": objective, "gym_trainer_id": ObjectId(gym_trainer_id), "status": "Available"}
        gym_sessions_collection.insert_one(query)
        return redirect("sessions?message=Session is added")
    else:
        return redirect("sessions?message=Session of start date and end date is already exists")
def set_enrolled_count_by_session_id(gym_session_id):
    query = {"gym_session_id": gym_session_id, "status": "enrolled"}
    count = enrollments_collections.count_documents(query)
    return count


@app.route("/suspend")
def suspend():
    gym_session_id = request.args.get("gym_session_id")
    query1 = {"_id": ObjectId(gym_session_id)}
    query2 = {"$set": {"status": "suspended"}}
    gym_sessions_collection.update_one(query1, query2)
    query3 = {"gym_session_id": ObjectId(gym_session_id)}
    enrollments = enrollments_collections.find(query3)
    enrollment_ids = []
    for enrollment in enrollments:
        enrollment_ids.append(enrollment['_id'])
    query4 = {"_id": {"$in": enrollment_ids}}
    query5 = {"$set": {"status": "suspended"}}
    enrollments_collections.update_many(query4, query5)
    query6 = {"enrollment_id": {"$in": enrollment_ids}}
    query7 = {"$set": {"status": "refunded"}}
    payments_collection.update_one(query6, query7)
    return redirect("/sessions")


@app.route("/payment")
def payment():
    message = request.args.get("message")
    gym_session_id = request.args.get("gym_session_id")
    gym_trainee_id = session['gym_trainee_id']
    price = request.args.get("price")
    return render_template("enrollment.html", price=price, gym_session_id=gym_session_id, gym_trainee_id=gym_trainee_id, message=message)


@app.route("/payment_action", methods=['post'])
def payment_action():
    gym_session_id = request.form.get("gym_session_id")
    card_number = request.form.get("card_number")
    card_holder_name = request.form.get("card_holder_name")
    price = request.form.get("price")
    expired_date = request.form.get("expired_date")
    cvv = request.form.get("cvv")
    date = datetime.datetime.now()
    gym_trainee_id = session['gym_trainee_id']
    enrollment_date = datetime.datetime.now()
    query = {"enrollment_date": enrollment_date, "status": "enrolled", "gym_session_id": ObjectId(gym_session_id), "gym_trainee_id": ObjectId(gym_trainee_id)}
    result = enrollments_collections.insert_one(query)
    enrollment_id = result.inserted_id
    query = {"enrollment_id": enrollment_id, "gym_trainee_id": ObjectId(gym_trainee_id), "price": price, "card_number": card_number, "card_holder_name": card_holder_name, "expired_date": expired_date, "cvv": cvv, "date": date, "status": "transaction successful"}
    payments_collection.insert_one(query)
    return render_template("message.html", message="Your Are Enrolled Successfully")


@app.route("/membership_payment")
def membership_payment():
    membership_title = request.args.get("membership_title")
    price = request.args.get("price")
    return render_template("membership_payment.html", membership_title=membership_title, price=price)


@app.route("/membership_payment_action", methods=['post'])
def membership_payment_action():
    membership_title = request.form.get("membership_title")
    price = request.form.get("price")
    gym_trainee_id = session['gym_trainee_id']
    query1 = {"_id": ObjectId(gym_trainee_id)}
    query2 = {"$set": {"membership_title": membership_title, "price": price}}
    gym_trainees_collection.update_one(query1, query2)
    query1 = {"gym_trainee_id": ObjectId(gym_trainee_id)}
    query2 = {"$set": {"payment_type": membership_title, "membership_cost": price}}
    payments_collection.update_one(query1, query2)
    return render_template("main_message.html", message="Your membership subscription is added")


@app.route("/view_payments")
def view_payments():
    enrollment_id = request.args.get("enrollment_id")
    print(enrollment_id)
    query = {"enrollment_id": ObjectId(enrollment_id)}
    payment = payments_collection.find_one(query)
    print(payment)
    return render_template("view_payments.html", payment=payment)


@app.route("/view_enrollments")
def view_enrollments():
    query = {}
    if session['role'] == "gym_trainer":
        gym_trainer_id = session['gym_trainer_id']
        gym_session_id = request.args.get("gym_session_id")
        if gym_session_id == None:
            query = {"gym_trainer_id": ObjectId(gym_trainer_id)}
            gym_sessions = gym_sessions_collection.find(query)
            gym_session_ids = []
            for gym_session in gym_sessions:
                gym_session_ids.append(gym_session['_id'])
            query = {"gym_session_id": {"$in": gym_session_ids}}
        else:
            query = {"gym_session_id": ObjectId(gym_session_id)}
    elif session['role'] == "gym_trainee":
        gym_trainee_id = session['gym_trainee_id']
        gym_session_id = request.args.get("gym_session_id")
        if gym_session_id == None:
            query = {"gym_trainee_id": ObjectId(gym_trainee_id)}
        else:
            query = {"gym_trainee_id": ObjectId(gym_trainee_id), "gym_session_id": ObjectId(gym_session_id)}
    print(query)
    enrollments = enrollments_collections.find(query)
    enrollments = list(enrollments)
    print(len(enrollments))
    return render_template("view_enrollments.html", enrollments=enrollments, get_gym_trainees_by_gym_trainee_id=get_gym_trainees_by_gym_trainee_id,get_gym_session_by_gym_session_id=get_gym_session_by_gym_session_id, get_gym_trainer_by_gym_trainer_id=get_gym_trainer_by_gym_trainer_id)
def get_gym_trainees_by_gym_trainee_id(gym_trainee_id):
    query = {"_id": gym_trainee_id}
    gym_trainee = gym_trainees_collection.find_one(query)
    return gym_trainee
def get_gym_session_by_gym_session_id(gym_session_id):
    query = {"_id": gym_session_id}
    gym_session = gym_sessions_collection.find_one(query)
    return gym_session
def get_gym_trainer_by_gym_trainer_id(gym_trainer_id):
    query = {"_id": gym_trainer_id}
    gym_trainer = gym_trainers_collection.find_one(query)
    return gym_trainer


@app.route("/attendance")
def attendance():
    message = request.args.get("message")
    enrollment_id = request.args.get("enrollment_id")
    attendances = attendance_collection.find({"enrollment_id": ObjectId(enrollment_id)})
    return render_template("attendance.html", attendances=attendances,enrollment_id=enrollment_id, message=message, get_enrollments_by_enrollment_id=get_enrollments_by_enrollment_id, get_gym_trainees_by_gym_trainee_id=get_gym_trainees_by_gym_trainee_id)


@app.route("/attendance_action", methods=['post'])
def attendance_action():
    enrollment_id = request.form.get("enrollment_id")
    attendance = request.form.get("attendance")
    date = request.form.get("date")
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    query = {"date": date, "enrollment_id": ObjectId(enrollment_id)}
    count = attendance_collection.count_documents(query)
    if count > 0:
        return redirect("attendance?message=Attendance of the trainee is already added&enrollment_id="+str(enrollment_id))
    else:
        query = {"enrollment_id": ObjectId(enrollment_id), "attendance": attendance, "date": date}
        attendance_collection.insert_one(query)
        return redirect("attendance?message=Attendance Added Successfully&enrollment_id="+str(enrollment_id))
def get_enrollments_by_enrollment_id(enrollment_id):
    query = {"_id": enrollment_id}
    enrollment = enrollments_collections.find_one(query)
    return enrollment
def get_gym_trainees_by_gym_trainee_id(gym_trainee_id):
    query = {"_id": gym_trainee_id}
    gym_trainee = gym_trainees_collection.find_one(query)
    return gym_trainee


@app.route("/gym_trainer_logout")
def gym_trainer_logout():
    return redirect("/")


@app.route("/gym_trainee_registration")
def gym_trainee_registration():
    return render_template("/gym_trainee_registration.html")


@app.route("/gym_trainee_registration_action", methods=['post'])
def gym_trainee_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")
    conform_password = request.form.get("conform_password")
    phone = request.form.get("phone")
    date_of_birth = request.form.get("date_of_birth")
    gender = request.form.get("gender")
    state = request.form.get("state")
    address = request.form.get("address")
    zip_code = request.form.get("zip_code")
    if password != conform_password:
        return render_template("main_message.html", message="Password and Conform Password is not Matched")
    query = {"email": email, "phone": phone}
    count = gym_trainees_collection.count_documents(query)
    if count == 0:
        query = {"first_name": first_name, "last_name": last_name, "email": email, "password": password, "phone": phone, "date_of_birth": date_of_birth, "gender": gender, "state": state, "address": address, "zip_code": zip_code}
        gym_trainees_collection.insert_one(query)
        return render_template("main_message.html", message=" Your Registered Successfully")
    else:
        return render_template("main_message.html", message="Duplicate email or phone number")


@app.route("/gym_trainee_login")
def gym_trainee_login():
    return render_template("gym_trainee_login.html")


@app.route("/gym_trainee_login_action", methods=['post'])
def gym_trainee_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = gym_trainees_collection.count_documents(query)
    if count > 0:
        gym_trainee = gym_trainees_collection.find_one(query)
        session['gym_trainee_id'] = str(gym_trainee['_id'])
        session['role'] = "gym_trainee"
        print(gym_trainee)
        if 'membership_title' not in gym_trainee:
            return render_template("view_member_ship.html")
        return redirect("/gym_trainee_home")
    else:
        return render_template("main_message.html", message="Invalid Login")


@app.route("/gym_trainee_home")
def gym_trainee_home():
    gym_trainee_id = session['gym_trainee_id']
    query = {"_id": ObjectId(gym_trainee_id)}
    gym_trainee = gym_trainees_collection.find_one(query)
    return render_template("gym_trainee_home.html", gym_trainee=gym_trainee)


@app.route("/gym_trainee_logout")
def gym_trainee_logout():
    return redirect("/")


app.run(debug=True)