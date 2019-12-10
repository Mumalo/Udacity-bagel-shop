from models import Base, User, Bagel
from flask import Flask, jsonify, request, abort, g
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_httpauth import HTTPBasicAuth


engine = create_engine('sqlite:///bagelShop.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)
auth = HTTPBasicAuth()

"""
handles token based authentication and basic auth
"""


@auth.verify_password
def verify_password(username_or_token, password):
    user_id = User.verify_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    print(token)
    return jsonify({'token': token.decode('ascii')})


@app.route('/users', methods=['POST'])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    print("Making new user with {}".format(request.json))
    if username is None or password is None:
        print("Wrong arguments")
        abort(400)
    user = session.query(User).filter_by(username=username).first()
    if user is not None:
        return jsonify({'message': 'user exists'}), 200
    user = User(username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'username': user.username}), 201


@app.route('/users/<int:user_id>')
@auth.login_required
def get_user(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/bagels', methods = ['GET','POST'])
@auth.login_required
def show_all_bagels():
    if request.method == 'GET':
        bagels = session.query(Bagel).all()
        return jsonify(bagels = [bagel.serialize for bagel in bagels])
    elif request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        picture = request.json.get('picture')
        price = request.json.get('price')
        newBagel = Bagel(name = name, description = description, picture = picture, price = price)
        session.add(newBagel)
        session.commit()
        return jsonify(newBagel.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

