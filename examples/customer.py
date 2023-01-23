from flask import Flask, request, jsonify, make_response
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(45))
    email = db.Column(db.String(45))
    address1 = db.Column(db.String(45))
    address2 = db.Column(db.String(45))
    city = db.Column(db.String(45))
    state = db.Column(db.String(20))
    postal_code = db.Column(db.String(10))

    def __init__(self, username, password, contact_name):
        self.username = username
        self.password = generate_password_hash(password)
        self.contact_name = contact_name

    def __repr__(self):
        ret = ""
        for attribute, value in dict(self).items():
            if not attribute.startswith('__') and not attribute.startswith('_'):
                ret += attribute + " : " + value + " - "
        return ret[:-3]

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield str(attr), str(value)


# For GET request to http://localhost:5000/
class GetUser(Resource):
    def get(self):
        users = User.query.all()
        print(users)
        user_list = []
        for user in users:
            user_data = dict(user)
            del user_data["_sa_instance_state"]
            user_list.append(user_data)
        return {"Users": user_list}, 200


# For Post request to http://localhost:5000/employee
class AddUser(Resource):
    def post(self):
        if request.is_json:
            user = User(username=request.json['username'], password=request.json['password'],
                        contact_name=request.json['contact_name'], )
            db.session.add(user)
            db.session.commit()
            # return a json response
            return make_response(jsonify({'id': user.id, 'username': user.username,
                                          'password': user.password,
                                          'contact_name': user.contact_name, }), 201)
        else:
            return {'error': 'Request must be JSON'}, 400


# For put request to http://localhost:5000/update/?
class UpdateUser(Resource):
    def put(self, user_id):
        if request.is_json:
            user = User.query.get(user_id)
            if user is None:
                return {'error': 'not found'}, 404
            else:
                user.email = request.json['email']
                user.address1 = request.json['address1']
                user.city = request.json['city']
                user.postal_code = request.json['postal_code']
                db.session.commit()
                return 'Updated', 200
        else:
            return {'error': 'Request must be JSON'}, 400


# For delete request to http://localhost:5000/delete/?
class DeleteUser(Resource):
    def delete(self, user_id):
        user = User.query.get(user_id)
        if user is None:
            return {'error': 'not found'}, 404
        db.session.delete(user)
        db.session.commit()
        return f'{user_id} is deleted', 200


api.add_resource(GetUser, '/')
api.add_resource(AddUser, '/add')
api.add_resource(UpdateUser, '/update/<int:user_id>')
api.add_resource(DeleteUser, '/delete/<int:user_id>')
if __name__ == '__main__':
    app.run(debug=True)
