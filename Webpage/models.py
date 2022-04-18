from Webpage import db, api
from flask_restful import Resource

VERSION = 0.85

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    pubKey = db.Column(db.String(), nullable=False, unique=True)
    items = db.relationship('product_keys', backref='owned_user', lazy=True)
    pagos_recibidos = db.relationship('recibos', backref='pagado_a', lazy=True)

class product_keys(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(), nullable=False, unique=True)
    referido = db.Column(db.String())
    time_left = db.Column(db.Integer())
    passwor = db.Column(db.String())
    owner = db.Column(db.String(), db.ForeignKey('user.pubKey'), nullable=False)

class recibos(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    txhash = db.Column(db.String(), nullable=False, unique=True)
    pago = db.relationship("hash", backref='pago_deuda', lazy=True)
    a_quien = db.Column(db.String(), db.ForeignKey('user.pubKey'), nullable=False)

class hash(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    hashes = db.Column(db.String(), nullable=False, unique=True)
    referido = db.Column(db.String()) #quien refirió ese hash
    tipo = db.Column(db.Integer()) # 0 = Daily, 1 = Mensual, 2 = Final
    paid = db.Column(db.Integer()) # 0 = False, 1 = True
    pago_recibo = db.Column(db.String(), db.ForeignKey('recibos.txhash'))

class TimeLeft(Resource):
    def get(self, key, ip):
        for i in product_keys.query.filter_by(code = key):
            tlef = i.time_left
            if ip != i.referido:
                if i.referido == None:
                    i.referido = ip
                    db.session.commit()
                else:
                    return {"data": None, "version": VERSION, "message": "Esta clave pertenece a otro ordenador"}
            return {"data": tlef, "version": VERSION, "message": "Bienvenido"}
        return {"data": None, "version": VERSION, "message": "Clave invalida"}

api.add_resource(TimeLeft, "/TimeLeft/<string:key>/<string:ip>")
