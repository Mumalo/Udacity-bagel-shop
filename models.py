from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature
import random
import string

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
Base = declarative_base()


# ADD YOUR USER MODEL HERE
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=60):
        s = TimedJSONWebSignatureSerializer(secret_key=secret_key, expires_in=expiration)
        print({'id': self.id})
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_token(token):
        s = TimedJSONWebSignatureSerializer(secret_key=secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid token but expired
            return None
        except BadSignature:
            # Invalid token
            return None
        user_id = data['id']
        return user_id


class Bagel(Base):
    __tablename__ = 'bagel'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    picture = Column(String)
    description = Column(String)
    price = Column(String)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
            'price': self.price
        }
