from flask import Flask
from flask import render_template,request,make_response,jsonify

app=Flask(__name__)
@app.route("/")
def hello_flask():
    resp=make_response(render_template('hello.html'))
    resp.set_cookie('username','johndoe')
    return resp

@app.route("/a")
def test__cookie():
    print(request.cookies.get('username'))
    username=request.cookies.get('username')
    return jsonify({"username":username})


