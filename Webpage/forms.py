from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, length

class confirmar_pago(FlaskForm):
    address_es = StringField(label="Introduzca dirección de la billetera con la que realizó el pago: ", validators=[DataRequired(message="Insertar dirección de la billetera")])
    link_bscscan_es = StringField(label="Introduzca hash de la transacción de BSCSCAN (acepta hash y link)", validators=[DataRequired(message="Introduce una dirección de BSCSCAN")])
    codigo_referido_es = StringField(label="Introduzca el código de referido: ")
    clave_secreta_es = StringField(label="contraseña temporal: ", validators=[DataRequired(message="Este campo es nesesario para asegurar tu clave"), length(max=20)])

    address_en = StringField(label="Introduce the Wallet address you paid with: ", validators=[DataRequired(message="This Field is mandatory")])
    link_bscscan_en = StringField(label="Introduce The tx. Hash", validators=[DataRequired(message="This Field is mandatory")])
    codigo_referido_en = StringField(label="Referral Code: ")
    clave_secreta_en = StringField(label="Temporary password: ", validators=[DataRequired(message="This field is neccesary to sequre your password"), length(max=20)])

    submit_button = SubmitField(label='Submit')
