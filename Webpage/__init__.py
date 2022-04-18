from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import os

IMG_FOLDER = os.path.join('static', 'images')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datoz.db'
app.config['SECRET_KEY'] = '7780a58a6c2903fbd98c91ea827e92977d87aaeba01fa2b15a8413f403ea9d15'
db = SQLAlchemy(app)
api = Api(app)

            
from Webpage import routes