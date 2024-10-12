from flask import Flask,session
from flask import render_template,request,make_response,jsonify
from database.db import create_customer,start_connection,get_user_by_username
from werkzeug.security import generate_password_hash,check_password_hash
import json

app=Flask(__name__)
app.secret_key='jhsdvhfvajhbf231354354'
# @app.route("/")
# def hello_flask():
#     resp=make_response(render_template('hello.html'))
#     resp.set_cookie('username','johndoe')
#     return resp

# @app.route("/a")
# def test__cookie():
#     print(request.cookies.get('username'))
#     username=request.cookies.get('username')
#     return jsonify({"username":username})

"""USER AUTHENTICATION BELOW"""
@app.route("/api/signup", methods=['GET','POST'])
def signup():
    if request.method=='POST':
        data=request.json
        username=data['username']
        password=data['password']
        email=data['email']
        conn=start_connection()

        ##Validate if user exists

        create_customer(username,password,email,conn)
        return("registration Successful")
    else:
        return("Error Creating User")
@app.route("/api/signin",methods=['GET','POST'])    
def login():
    if request.method=='POST':
        data=request.json
        username=data['username']
        password=data['password']
        email=data['email']
        conn=start_connection()

#later include an get_user_by_email or
        user=get_user_by_username(username,conn)
        print(user)
        if user is not None:
            customer_id,customer_name,hashed_password=user
            if check_password_hash(hashed_password,password):
                print(password)
                session['customer_id']=customer_id
                session['customer_name']=customer_name
                conn.close()

                return jsonify({"message":"Login Succeful"})
            else:
                conn.close()
                return jsonify({"Error": "Invalid Credentials"})
        else:
            conn.close()
            return jsonify({"error":"User not Found"}),404
            
@app.route("/api/signout")
def logout():
    session.pop('customer_id',None)
    session.pop('customer_name',None)
    return jsonify({"Message":"Succeful logout"}),200

       



"""END USER AUTHENTICATION"""


"""MOVIES API BELOW"""
 #Fetch Movies





