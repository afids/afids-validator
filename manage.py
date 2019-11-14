import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from controller import app, db

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

class Fiducial_set(db.Model):
    __tablename__ = 'fid_db'

    id = db.Column(db.Integer, primary_key=True)
    AC_x = db.Column(db.Float())
    AC_y = db.Column(db.Float())
    AC_z = db.Column(db.Float())
    PC_x = db.Column(db.Float())
    PC_y = db.Column(db.Float())
    PC_z = db.Column(db.Float())

    def __init__(self, AC_x, AC_y, AC_z, PC_x, PC_y, PC_z):
        self.AC_x = AC_x
        self.AC_y = AC_y
        self.AC_z = AC_z
        self.PC_x = PC_x
        self.PC_y = PC_y
        self.PC_z = PC_z

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id, 
            'AC_x': self.AC_x,
            'AC_y': self.AC_y,
            'AC_z': self.AC_z,
            'PC_x': self.PC_x,
            'PC_y': self.PC_y,
            'PC_z': self.PC_z,

        }

if __name__ == '__main__':
    manager.run()
