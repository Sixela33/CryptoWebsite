from flask.helpers import flash, send_file
from markupsafe import Markup
from Webpage import app, db
from flask import render_template, request, send_from_directory
from flask import session as secion
from Webpage.models import product_keys, User, hash
from Webpage.forms import confirmar_pago
from web3 import Web3
import requests
import time
from werkzeug.security import generate_password_hash, check_password_hash
from utils import process_link

API_KEY = "JNCYQA8NZFHP9VMWKWZQ87VSTQWUY4FK5Y"
PRECIOS = [0.15, 0.8, 2.8, 0.1]
# 0: Claves Diarias, 1: Claves Mensuales, 2: Claves Finales, 3: Reseteo de máquina
WALLETS = ["0x8b55Fc1698c969Cbb48c4A40E6519486dc104A5A", "0xc064DF10d5c906831c490e4A30D11FF7EC0F106d", "0x1426b9d0Ccc8A1fF6A6838f5dF01fb04fE64158D", "0x394B16c5ff2597a29933F6D13F3556AeBa466C08"] 
TIEMPO = {0: 86500, 1: 2610400, 2: 26784000000}


@app.route('/')
@app.route('/home/', methods=['GET', 'POST'])
def home_page():
    return render_template('home.html', lan= lang())

def lang():
    if "language" in secion:
        a = secion["language"]
    else: a="Español"
    return a
    
@app.route('/', methods=['GET', 'POST'])
def change_language():
    secion["language"] = request.form["lenguajes"]
    print (secion["language"])
    print(request.form["lenguajes"])
    return render_template('home.html', lan=secion["language"])

@app.route("/referidos", methods=['GET', 'POST'])
def referidos_info():
    ref = [0, 0, 0, 0]
    ref_total = [0, 0, 0, 0]
    codigo = 'ESTA CARTERA NO PUEDE REFERIR'

    if 'wallet' in secion and secion['wallet'] != 'null':
        wallet = secion['wallet']
        try:
            add = Web3.toChecksumAddress(wallet)
        except ValueError:
            flash("Cartera Invalida",  category="error")
            return render_template('referido.html', referidos_pendientes = ref, referidos_totales = ref_total, lan=lang(), secion = secion, codigo= codigo)
        queri = product_keys.query.filter_by(owner=add)
        for i in queri:
            if i.time_left > time.time()+2678400000:
                codigo = f'http://CryptoSnyper/checkout/{wallet}'
        itemz = hash.query.filter_by(referido = add)
        for i in itemz:
            if i.paid == 0:
                ref[i.tipo] += 1
                ref[3] += PRECIOS[i.tipo]*0.15
            ref_total[i.tipo] += 1
            ref_total[3] += PRECIOS[i.tipo]*0.15

        if len(itemz.all()) == 0:
            flash("No se encontraron Codigos referidos con esa Wallet", category="error")
    return render_template('referido.html', referidos_pendientes = ref, referidos_totales = ref_total, lan=lang(), secion = secion, codigo = codigo)

@app.route("/static<path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.route("/codigos", methods=['GET', 'POST'])
def code_management():
    itemz = ""
    e = 0
    items =[]

    if request.method == 'POST':
        
        if request.form["submit_button"] == "valdidar_pass":
            objs = product_keys.query.filter_by(owner=secion["wallet"])
            with db.session.no_autoflush:
                for i in objs:
                    obj = {"id": "", "code": "", "time_left": 0}
                    if i.referido == None:
                        passw = str(request.form["contraseña"])

                        if not check_password_hash(i.passwor, passw):
                            obj["code"] = Markup('<form method="POST"><input type="text" id="password" placeholder="Password" name="contraseña"><input type="submit" name="submit_button" value="valdidar_pass" class="btn btn-primary"></form>')
                        else:
                            obj["code"] = i.code
                    
                    if i.time_left < time.time():
                        db.session.delete(i)
                        db.session.commit()
                        continue
                    
                    tf = i.time_left-time.time()
                    if (tf/86400) < 1:
                        obj["time_left"] = f"{(i.time_left-time.time())/3600} Hours"
                    elif (tf/86400) < 30:
                        obj["time_left"] = f"{(i.time_left-time.time())/86400} Days"
                    elif (tf/2592000) < 12:
                        obj["time_left"] = f"{(i.time_left-time.time())/2592000} Months"
                    else:
                        obj["time_left"] = "FINAL"

                    obj["id"] = i.id
                    items.append(obj)

                return render_template('codigos.html', items=items, mostrar=True, hora = time.time(), lan=lang(), secion = secion)

        else:
            try:
                wallet = Web3.toChecksumAddress(request.form["wallet"])
                secion["wallet"] = wallet
            except ValueError:
                flash("Cartera Invalida", category="error")
                return render_template('codigos.html', items=itemz, mostrar=False, hora = time.time(), lan=lang(), secion = secion)

    if "wallet" in secion:
        wallet = secion["wallet"]
    else:
        wallet = ""

    if wallet != "":
        itemz = product_keys.query.filter_by(owner=wallet)

        with db.session.no_autoflush:
            for j in itemz:

                obj = {"id": "", "code": "", "time_left": 0}
                if float(j.time_left) < time.time():
                    db.session.delete(j)
                    db.session.commit()
                    continue
                else:
                    secion["wallet"] = wallet
                    e+=1
                
                tf = j.time_left-time.time()
                if (tf/86400) < 1:
                    obj["time_left"] = f"{(j.time_left-time.time())/3600} Hours"
                elif (tf/86400) < 30:
                    obj["time_left"] = f"{(j.time_left-time.time())/86400} Days"
                elif (tf/2592000) < 12:
                    obj["time_left"] = f"{(j.time_left-time.time())/2592000} Months"
                else:
                    obj["time_left"] = "FINAL"

                
                if j.referido == None:
                        obj["code"] = Markup('<form method="POST"><input type="text" id="password" placeholder="Password" name="contraseña"><input type="submit" name="submit_button" value="valdidar_pass" class="btn btn-primary"></form>')
                else: obj["code"] = j.code
                
                obj["id"] = j.id
                items.append(obj)

                if e == 0:
                    flash("No se encontraron Codigos linkeados con esa Wallet", category="error")
            return render_template('codigos.html', items=items, mostrar=True, hora = time.time(), lan=lang(), secion = secion)
            
    return render_template('codigos.html', items=itemz, mostrar=False, hora = time.time(), lan=lang(), secion = secion)

@app.route('/descargas')
def descargar_archivo():
    p = "File.txt"
    return send_file(f"./static/descargas/{p}", as_attachment=True)

@app.route('/reiniciar_ordenador/<id>', methods=['GET', 'POST'])
def Reiniciar_ordenador(id):
    confirm = confirmar_pago(request.form)
    query = product_keys.query.filter_by(id = id)
    for i in query:
        dueño = i.owner

    if request.method == "POST":

        def check_string(items):
            for i in items:
                if type(i) != str:
                    print("[ERROR] Hash invalido")
                    return False

                if ";" in i:
                    print("[ERROR] Input invalido")
                    return False
            return True
            
        clave = confirm.clave_secreta_es.data
        tx_hash = confirm.link_bscscan_es.data

        if not check_string([tx_hash]):

            return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)

        base = "https://bscscan.com/tx/"

        if tx_hash[0: 23] == base:
            tx_hash = tx_hash[23: len(tx_hash)]

        try:
            ADD = Web3.toChecksumAddress(secion["wallet"])
        except:
            flash("No hay cartera en la sesion, porfavor accede a esta pagina desde 'Mis Coidigos'")
            return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)

        data = requests.get(f"https://api.bscscan.com/api?module=account&action=txlist&address={ADD}&startblock=0&endblock=99999999&page=1&offset=15&sort=desc&apikey={API_KEY}")
        data = data.json()
        if data["status"] == 0:
            flash("HASH invalido", category="Error")
            return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)

        data = data["result"]

        lcl = 0
        for item in data:
            lcl+=1
            if tx_hash == item["hash"]:
                try:
                    wallet = Web3.toChecksumAddress(item["to"])
                except ValueError:
                    flash("Transaccion Invalida", category="error")
                    return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)

                sent = float(item["value"])/(10**18)
                if wallet == WALLETS[3]: #daily
                    tp = 3
                else:
                    flash("Se envio el dinero a una dirección erronea", category="error")
                    return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)
                
                if sent < PRECIOS[tp]:
                    flash(f"Se han Donado exitosamente: {sent} BNB.", category="success")
                    return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)

                for _ in hash.query.filter_by(hashes = tx_hash):
                    flash(f"Este Hash ya fue Claimeado: {sent}", category="error")
                    return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)

                pass_hasheada = generate_password_hash(clave, method='sha256')

                hx = hash(hashes= tx_hash, tipo = tp, paid = 1)
                db.session.add(hx)
                for i in query:
                    i.referido = None
                    i.passwor = pass_hasheada

                    db.session.commit()
                    flash("Se han reiniciado los valores de forma exitosa!", category="success")

            else:
                flash("No se encontró la transacción en el historial de la billetera, (recuerda que debe ser la billetera con la que compraste el codigo) Si realizaste la tx aguardá al minado.", category="error")
                return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)

    return render_template('pc_reset.html', precio_reset = PRECIOS[3], owner_address = dueño, direccion_reseteo = WALLETS[3], confirm = confirm, lan=lang(), secion = secion)

@app.route('/checkout/', defaults ={"referido": ''}, methods=['GET', 'POST'])
@app.route('/checkout/<referido>', methods=['GET', 'POST'])
def pagina_compra(referido):
    confirm = confirmar_pago(request.form)
    show = True
    if referido != '':
        try: referido = Web3.toChecksumAddress(referido)
        except: flash("link de referido Invalido", category='error'); referido = ''
        
    if request.method == 'POST':

        th = request.form["submit_button"]

        if th == "Submit":
            if process_link(request, referido):
                render_template("codigos.html", items="")

        if th == f"Diaria [{PRECIOS[0]} BNB]" or th == f"1 Day [{PRECIOS[0]} BNB]":
            precio = f"{PRECIOS[0]} BNB"
            add = WALLETS[0]

        elif th == f"Mensual [{PRECIOS[1]} BNB]" or th == f"1 Month [{PRECIOS[1]} BNB]":
            precio = f"{PRECIOS[1]} BNB"
            add = WALLETS[1]

        elif th == f"Vez única [{PRECIOS[2]} BNB]" or th == f"Lifetime [{PRECIOS[2]} BNB]":
            precio = f"{PRECIOS[2]} BNB"
            add = WALLETS[2]
        else:
            show = False
            precio = ""
            add = ""

        return render_template('checkout.html', precio = precio, add= add , confirm=confirm, show = show, lan=lang(), secion = secion, price = PRECIOS, ref = referido)
    else:
        show = False
        precio = ""
        add = ""
        return render_template('checkout.html', precio = precio, add= add , confirm=confirm, show = False, lan=lang(), secion = secion, price = PRECIOS, ref = referido)
