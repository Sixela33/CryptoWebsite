import random
import string
import time
from flask.helpers import flash
from Webpage.models import product_keys, User
from routes import Web3, WALLETS, PRECIOS, TIEMPO, API_KEY
import requests
from werkzeug.security import generate_password_hash
from Webpage import db

# This function processes the payment.
#  - Checks the blockchain for the transaction,
#  - Validates the referall code,
#  - Stores all the needed information in the database

def process_link(request, ref):

    # Verifying Input integrity and security

    try:
        tx_hash = request.form["link_bscscan_es"]
        ADD = request.form["address_es"]
        referido = ref
        clave_temp = request.form["clave_secreta_es"]
    except KeyError:
        tx_hash = request.form["link_bscscan_en"]
        ADD = request.form["address_en"]
        referido = ref
        clave_temp = request.form["clave_secreta_en"]

    if not check_string([tx_hash, ADD, referido, clave_temp]):
        return False

    # checks if the referall is valid
    try:
        tharef, pad, finish = check_referido(referido)
        referido = Web3.toChecksumAddress(referido)
    except ValueError:
        flash("Cartera de referido INVALIDA", category="error")
        finish = False
    
    if not finish:
        return False

    base = "https://bscscan.com/tx/"
    if tx_hash[0: 23] == base:
        tx_hash = tx_hash[23: len(tx_hash)]

    # Asks BSC API for the last transactions the user made and checks if the payment was made

    data = requests.get(f"https://api.bscscan.com/api?module=account&action=txlist&address={ADD}&startblock=0&endblock=99999999&page=1&offset=15&sort=desc&apikey={API_KEY}")
    data = data.json()
    if data["status"] == 0:
        flash("HASH invalido", category="Error")
        return False

    data = data["result"]
    lcl = 0

    try:
        ADD = Web3.toChecksumAddress(ADD)
    except ValueError:
        flash("Cartera Invalida", category="error")
        return False
    
    for item in data:
        lcl+=1
        if tx_hash == item["hash"]:
            try:
                wallet = Web3.toChecksumAddress(item["to"])
            except ValueError:
                flash("Transaccion Invalida", category="error")
                return False

            # Sets the time period
            sent = float(item["value"])/(10**18)
            if wallet == WALLETS[0]: #daily
                tp = 0
            elif wallet == WALLETS[1]: #Mensual
                tp = 1
            elif wallet == WALLETS[2]: # Final
                tp = 2
            else:
                flash("Se envio el dinero a una dirección erronea", category="error")
                return False

            precio = PRECIOS[tp]

            while tp > 0 and sent < precio:
                tp = tp-1
                precio = PRECIOS[tp]
            
            if sent < precio:
                flash(f"Se han Donado exitosamente: {sent} BNB. Si ha cometio un error, envíe un email con su txHash ", category="success")
                return False

            tiempo = TIEMPO[tp]
            mult = sent/precio

            code = gen_code()
            for _ in hash.query.filter_by(hashes = tx_hash):
                flash(f"Este Hash ya fue Claimeado: {sent}", category="error")
                return False
            
            
            pass_hasheada = generate_password_hash(clave_temp, method='sha256')

            # Saving the information to the database

            hx = hash(hashes= tx_hash, referido = tharef, tipo = tp, paid = pad)
            db.session.add(hx)
            def finish_it():
                T = time.time()+(tiempo*mult)
                nk = product_keys(code=code, time_left= T, owner=ADD, passwor=pass_hasheada)
                db.session.add(nk)
                db.session.commit()

            for _ in User.query.filter_by(pubKey = ADD):
                finish_it()
                flash("Codigo activado con exito!! puedes ver tus codigos activos en \"Mis Codigos\" ", category="success")
                return True

            u = User(pubKey= ADD)
            db.session.add(u)
            finish_it()
            flash("Codigo activado con exito!! puedes ver tus codigos activos en \"Mis Codigos\" ", category="success")
            return True

    flash("No se encontró la transacción en el historial de la billetera, Si realizaste la tx aguardá al minado.", category="error")
    return False


def check_referido(referido):
    if referido != "":
        
        ref =  User.query.filter_by(pubKey = referido)
        if len(ref.all()) == 0:
            flash("Este referido no tiene una clave de product PERMANENTE activa", category="error")
            return "", 1, False

        for i in ref:
            for j in i.items:
                if j.time_left > time.time()+2678400000:
                    return referido, 0, True
        
        flash("El referido precisa una clave de producto PERMANENTE", category="error")
        return "", 1, False
    else:
        return None, 1, True

def gen_code():
    code = ""
    for i in range(0,5):
        for _ in range(0, 5):
            code = code + (random.choice(string.ascii_letters)).upper()
            random.choice(string.ascii_letters)
        if i != 4:
            code = code + "-"

    for i in product_keys.query.filter_by(code = code):
        code = gen_code()
        return code
    return code

def check_string(items):
    for i in items:
        if type(i) != str:
            print("[ERROR] Input invalido")
            return False

        if ";" in i:
            flash("No se permiten ';'", category="error")
            return False
    return True