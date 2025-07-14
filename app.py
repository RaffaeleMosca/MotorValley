from bson import ObjectId
from flask import Flask, render_template, session, redirect, url_for, request, jsonify, flash
from functools import wraps
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_pymongo import PyMongo
from passlib.handlers.pbkdf2 import pbkdf2_sha256
import uuid

app = Flask(__name__)
#genero la secret key
app.secret_key = uuid.uuid4().hex

from datetime import timedelta
app.permanent_session_lifetime = timedelta(minutes=30)

# Database locale
#client = pymongo.MongoClient('localhost', 27017)
#db = client.login


#Database su cloud
#app.config['MONGO_URI'] = 'mongodb+srv://RafMosca:RafMoscaDB@cluster0.rzvmm.mongodb.net/'
#mongo = PyMongo(app)
#db = mongo.db

uri = "mongodb+srv://RafMosca:RafMoscaDB@cluster0.rzvmm.mongodb.net/"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#Database su cloud
app.config['MONGO_URI'] = uri
mongo = PyMongo(app)
db = client.motorValley

# FUNZIONE CHE CONTROLLA SE SI E' LOGGATI
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/log/')

  return wrap

# Routes
from user import routes

@app.route('/')
def home():
  return render_template('homepage.html')

@app.route('/homepage/')
def homepage():
  return render_template('homepage.html')

@app.route('/log/')
def log():
  return render_template('log.html')

@app.route('/utente/')
@login_required
def utente():
    return render_template('page_account.html')


@app.route('/modificapass/<utente>', methods=['GET', 'POST'])
def modificapass(utente):
    utente = db.users.find_one({'matricola': utente})
    if not utente:
        flash('Utente non trovato.', 'error')
        return render_template('page_account.html')

    # Richiesta POST: elaboro il cambio password
    current_password = request.form.get('password')
    new_password = request.form.get('newpassword')

    # Validazione dei campi
    if not current_password or not new_password:
        flash('Tutti i campi sono obbligatori.', 'error')
        return render_template('page_account.html')

    # Verifica password corrente
    if not pbkdf2_sha256.verify(current_password, utente['password']):
        flash('La password attuale non è corretta.', 'error')
        return render_template('page_account.html')

    # Hash della nuova password
    hashed_new_password = pbkdf2_sha256.hash(new_password)

    # Aggiornamento su DB
    db.users.update_one(
        {"matricola": utente},
        {"$set": {"password": hashed_new_password}}
    )

    flash('Password cambiata correttamente.', 'success')
    return render_template('page_account.html')

    

#funzione per la creazione di un componente
#nello specefico la parte front end scatena una chiamata post al backend
#recupero tutti i dati inseriti dall'utente
#vado ad inserire il componente a DB nella tabella componenti
#alla fine sfruttando il tempoto render_template di Flask reindizzo alla pagina stessa passandogli tutti i componenti a DB

@app.route('/componente/')
@login_required
def componente():
    allComponenti = db.componenti.find()    
    return render_template('componente.html', componenti = allComponenti) # reindirizzo alla pagina visualizza e modifica componenti

@app.route("/creaComponente/<utente>", methods=('GET', 'POST'))
@login_required
def creaComponente(utente):
    if request.method == "POST":
        matricola = request.form.get('matricola')
        nome = request.form.get('nome')
        tipologia = request.form.get('tipologia')
        tempoLavorazione = request.form.get('tempoLavorazione')
        db.componenti.insert_one({'utente': utente, 'nome': nome, 'matricola': matricola, 'tipologia': tipologia, 'tempoLavorazione': int(tempoLavorazione)})
        return redirect(url_for('componente'))
    return render_template('componente.html')

#funzione che mi recupera tutti i componenti disponibili a DB e li passa al front-end
#il front-end poi li gestirà sotto forma tabellare
@app.route("/visualizzaComponenti/", methods=('GET', 'POST'))
@login_required
def visualizzaComponenti():
    allComponenti = db.componenti.find()    
    return render_template('visualizzaComponenti.html', componenti = allComponenti) # reindirizzo alla pagina visualizza e modifica componenti

@app.route('/eliminaComponente/<oid>', methods=('POST',))
def eliminaComponente(oid):
    db.componenti.delete_one({"_id": ObjectId(oid)})
    return redirect('/componente/')

#funzione che dato l'id del Componente dal front-end effettua le modifiche del componente
@app.route('/modificaComponente/<oid>', methods=('POST',))
def modificaComponente(oid):
    if request.method == "POST":
        nome = request.form.get('nome')
        tipologia = request.form.get('tipologia')
        tempoLavorazione = request.form.get('tempoLavorazione')
        db.componenti.update_one({"_id" : ObjectId(oid)}, {"$set": {"nome": nome, "tipologia": tipologia, "tempoLavorazione": tempoLavorazione}})
    return redirect('/componente/')


@app.route("/gestioneUtenze/", methods=('GET', 'POST'))
@login_required
def gestioneUtenze():
    allUsers = db.users.find()    
    return render_template('gestioneUtenze.html', utenti = allUsers) # reindirizzo alla pagina visualizza e modifica componenti

@app.route('/eliminaUtente/<oid>', methods=('POST',))
def eliminaUtente(oid):
    db.users.delete_one({"_id": oid})
    return redirect('/gestioneUtenze/')

@app.route('/modificaUtente/<oid>', methods=('POST',))
def modificaUtente(oid):
    if request.method == "POST":
        nome = request.form.get('nome')
        matricola = request.form.get('matricola')
        ruolo = request.form.get('ruolo')
        active = request.form.get('active') == 'on'
        db.users.update_one({"_id" : oid}, {"$set": {"nome": nome, "matricola": matricola, "ruolo": ruolo, "active": active}})
    return redirect('/gestioneUtenze/')

@app.route('/parametriProduzione/')
@login_required
def parametriProduzione():
    allParametriProduzione = db.parametriProduzione.find()    
    return render_template('parametriProduzione.html', parametriProduzione = allParametriProduzione) # reindirizzo alla pagina visualizza e modifica componenti

@app.route("/creaParametreProduzione/<utente>", methods=('GET', 'POST'))
def creaParametreProduzione(utente):
    if request.method == "POST":
        tipologia = request.form.get('tipologia')
        tempoLavorazione = request.form.get('tempoLavorazione')
        db.parametriProduzione.insert_one({'tipologia': tipologia, 'tempoLavorazione': int(tempoLavorazione)})
        return redirect(url_for('parametriProduzione'))
    all_parametriProduzione = db.parametriProduzione.find()  
    return render_template('parametriProduzione.html', parametriProduzione = all_parametriProduzione) # reindirizzo alla pagina crea parametri di produzione

@app.route('/eliminaParametriProduzione/<oid>', methods=('POST',))
def eliminaParametriProduzione(oid):
    db.parametriProduzione.delete_one({"_id": ObjectId(oid)})
    return redirect('/parametriProduzione/')

@app.route('/modificaParametriProduzione/<oid>', methods=('POST',))
def modificaParametriProduzione(oid):
    if request.method == "POST":
        tipologia = request.form.get('tipologia')
        tempoLavorazione = request.form.get('tempoLavorazione')
        db.parametriProduzione.update_one({"_id" : ObjectId(oid)}, {"$set": {"tipologia": tipologia, "tempoLavorazione": int(tempoLavorazione)}})
    return redirect('/parametriProduzione/')


@app.route('/lotto/')
@login_required
def lotto():
    allLotti = db.lotti.find()    
    allComponenti = db.componenti.find()   
    listComponenti = list(allComponenti)
    for componente in listComponenti:
        componente['quantita'] = 0
    return render_template('lotto.html', lotti = allLotti, componenti = listComponenti) # reindirizzo alla pagina visualizza e modifica componenti

@app.route('/eliminaLotto/<oid>', methods=('POST',))
def eliminaLotto(oid):
    db.lotti.delete_one({"_id": ObjectId(oid)})
    return redirect('/lotto/')

@app.route('/completaLottoInProduzione/<oid>,<numeroLotto>', methods=('POST',))
def completaLottoInProduzione(oid, numeroLotto):
    if request.method == "POST":
        all_lottiView = db.lotti.find()
        lotti = list(all_lottiView)
        for lotto in lotti:
            if int(lotto['numeroLotto']) == int(numeroLotto):
                db.lotti.update_one({"_id" : ObjectId(lotto['_id'])}, {"$set": {"statoLotto": "Completato"}})
    return redirect('/lotto/')

@app.route('/scartaLottoInProduzione/<oid>,<numeroLotto>', methods=('POST',))
def scartaLottoInProduzione(oid, numeroLotto):
    if request.method == "POST":
        db.lotti.update_one({"_id" : ObjectId(oid)}, {"$set": {"statoLotto": "Scartato"}})
    return redirect('/lotto/')


@app.route('/controlli_creazione_lotto', methods=['POST'])
def controlli_creazione_lotto():
    # Inizializzo le variabili di aggregazione
    totale_tempo_lotto_nuovo = 0
    totale_tempo_lotti_in_produzione = 0
    totale_tempo_generale = 0
    flag_error = False

    # Recupero dati da DB
    componenti = list(db.componenti.find())
    parametri_produzione = list(db.parametriProduzione.find())
    lotti = list(db.lotti.find())

    # Mappa: tipologia -> limite massimo di tempo lavorazione
    mappa_limiti_produzione = {el['tipologia']: el['tempoLavorazione'] for el in parametri_produzione}

    # Inizializzo mappe di aggregazione
    mappa_tempi_lotto_nuovo = {}           # tipologia -> totale tempo lavorazione lotto che sto creando
    mappa_quantita_lotto_nuovo = {}        # tipologia -> totale quantità lotto che sto creando
    mappa_tempi_lotti_in_produzione = {}   # tipologia -> totale tempo lavorazione dei lotti in corso

    # Elaboro input utente
    for componente in componenti:
        input_name = f"quantita_{componente['_id']}"
        quantita_input = request.form.get(input_name)

        if quantita_input:
            componente['quantita'] = int(quantita_input)
        else:
            componente['quantita'] = 0  # Se non specificato, considero 0

        tipologia = componente['tipologia']
        tempo_unitario = int(componente['tempoLavorazione'])
        quantita = int(componente['quantita'])

        # Aggiorno mappe
        mappa_tempi_lotto_nuovo.setdefault(tipologia, 0)
        mappa_quantita_lotto_nuovo.setdefault(tipologia, 0)

        mappa_tempi_lotto_nuovo[tipologia] += tempo_unitario * quantita
        mappa_quantita_lotto_nuovo[tipologia] += quantita

    # Calcolo tempi dei lotti in corso
    for lotto in lotti:
        if lotto['statoLotto'] != 'In corso':
            continue
        tipologia = lotto['tipologia']
        tempo_lotto = int(lotto['tempoLavorazione'])

        mappa_tempi_lotti_in_produzione.setdefault(tipologia, 0)
        mappa_tempi_lotti_in_produzione[tipologia] += tempo_lotto

    # Controllo vincoli per ciascuna tipologia
    for tipologia in mappa_tempi_lotto_nuovo:
        tempo_nuovo = mappa_tempi_lotto_nuovo[tipologia]
        tempo_in_corso = mappa_tempi_lotti_in_produzione.get(tipologia, 0)
        limite = mappa_limiti_produzione.get(tipologia, 0)

        totale_tempo_lotto_nuovo += tempo_nuovo
        totale_tempo_lotti_in_produzione += tempo_in_corso
        totale_tempo_generale += tempo_nuovo + tempo_in_corso

        if (tempo_nuovo + tempo_in_corso) > limite:
            error_message = (
                f"Limite superato per categoria '{tipologia}'. "
                f"Il lotto che si intende creare occupa { tempo_nuovo} minuti. "
                f"Attualmente c'è una coda in produzione pari a {tempo_in_corso} minuti. "
                f"Limite massimo {limite} minuti."
            )
            flash(error_message, 'error')
            flag_error = True

    # Controllo limite generale
    limite_generale = mappa_limiti_produzione.get('Generale', 0)
    if totale_tempo_generale > limite_generale:
        error_message = (
            f"Limite generale superato: il lotto che si intende creare occupa {totale_tempo_lotto_nuovo} minuti. "
            f"Attualmente c'è una coda in produzione pari a {totale_tempo_lotti_in_produzione} minuti. "
            f"Limite massimo consentito {limite_generale} minuti."
        )
        flash(error_message, 'error')
        flag_error = True

    # Se non ci sono errori, creo il nuovo lotto
    if not flag_error:
        # Recupero il numeroLotto più alto
        numero_lotto_max = max((int(l['numeroLotto']) for l in lotti), default=0)

        for tipologia in mappa_tempi_lotto_nuovo:
            db.lotti.insert_one({
                'numeroLotto': numero_lotto_max + 1,
                'tipologia': tipologia,
                'quantita': mappa_quantita_lotto_nuovo[tipologia],
                'tempoLavorazione': mappa_tempi_lotto_nuovo[tipologia],
                'statoLotto': 'In corso'
            })

        flash('Lotto creato con successo.', 'success')

    return redirect('/lotto/')
