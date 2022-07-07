import flask
from flask import request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import json

app = flask.Flask(__name__)
cors = CORS(app)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:problemplays@database-1.cqzway4arj7b.us-east-1.rds.amazonaws.com/site'
app.config['CORS_HEADERS'] = 'Content-Type'
database = SQLAlchemy(app)

class Content(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    content = database.Column(database.String(10000), default='')

class IGUrl(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    igurl = database.Column(database.String(100), default='')

class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_name = database.Column(database.String(100), default='')
    user_email = database.Column(database.String(100), default='')

database.create_all()
database.session.commit()

@app.route('/api/v1/resources/content', methods=['GET'])
@cross_origin()
def api_content():
    recent_content = Content.query.order_by(Content.id.desc()).first().content
    return jsonify(recent_content)

@app.route('/api/v1/resources/get-users', methods=['POST'])
def create_entry():
    req = request.get_json()
    print(req)
    data = json.dumps(req)
    data = json.loads(data)
    name = data['name']
    email = data['email']
    new_user = Users(user_name = name, user_email = email)
    database.session.add(new_user)
    database.session.commit()
    res = make_response(jsonify({"message": "OK"}), 200)
    return res


if __name__ == '__main__':
    app.run()