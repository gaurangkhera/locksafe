from hack import db,login_manager
from uuid import uuid4
from flask_login import UserMixin
import nfc

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def get_uuid():
    return uuid4().hex


# User schema
class User(db.Model,UserMixin):
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String(64),index=True)
    password = db.Column(db.String)
    lockers = db.relationship('Locker', backref='user')


# Locker schema
class Locker(db.Model):
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    locker_name = db.Column(db.String(32))
    price = db.Column(db.Integer, default=10)
    access_key = db.Column(db.String, unique=True, default=lambda: get_uuid()[:6])
    is_available = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    # method to occupy a locker and make it unavailable
    def lock_locker(self, user_id):
        self.user_id = user_id
        self.is_available = False
        db.session.add(self, User.query.filter_by(id=user_id).first())
        db.session.commit()


    # authentication method to unlock locker if it is connected via nfc and access key is correct
    def unlock_locker(self, access_key):
        with nfc.ContactlessFrontend('udp') as clf:
            if access_key == self.access_key:
                self.is_available = True
                user = User.query.filter_by(id=self.user_id).first()
                user.lockers.remove(self)
                self.user_id = None
                self.access_key = get_uuid()[:6]
                db.session.add(self, user)
                db.session.commit()
                return True
            else:
                return False

