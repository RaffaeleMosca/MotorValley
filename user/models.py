from flask import Flask, jsonify, request, session, redirect, flash, render_template
from passlib.hash import pbkdf2_sha256
from app import db
import uuid

class User:

  def start_session(self, user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    return jsonify(user), 200

  def signup(self):
    print(request.form)

    # Creazione dell'oggetto utente
    user = {
      "_id": uuid.uuid4().hex,
      "ruolo": request.form.get('ruolo'),
      "nome": request.form.get('nome'),
      "matricola": request.form.get('matricola'),
      "password": request.form.get('password'),
      "active": request.form.get('ruolo') == 'Amministratore'
    }

    # Cripto la passowrd
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

    if user['active'] == False:
        db.users.insert_one(user)
        return jsonify({ "error": "L'utente prima di poter accedere deve essere approvato!" }), 400
    
    

    if db.users.find_one({ "matricola": user['matricola'] }):
      return jsonify({ "error": "La matricola inserita risulta già registrata!" }), 400

    if db.users.insert_one(user):
      return self.start_session(user)

    return jsonify({ "error": "Errore in fase di login!" }), 400
  
  def signout(self):
    session.clear()
    return redirect('/')
  
  def login(self):

    user = db.users.find_one({
      "matricola": request.form.get('matricola')
    })

    if user['active'] == False:
      return jsonify({ "error": "L'utente risulta disattivato!" }), 400

    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      return self.start_session(user)
    
    return jsonify({ "error": "Credenziali non valide!" }), 401

