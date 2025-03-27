import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from datetime import datetime, timedelta
pymysql.install_as_MySQLdb()  # Helps with SQLAlchemy compatibility


app = Flask(__name__) # start project

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:gtil@localhost/user_data' # indien je dit online zet -> verander locatie van @localhost naar locatie database online
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# dit zorgt ervoor dat flask weet wat er in de database is en dan ook kan zoeken in de database
class User(db.Model): # indien je hier datatype verandert ook datatype te veranderen in database manueel
    username = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Boek(db.Model):
    __tablename__ = 'boeken'
    titel = db.Column(db.String(255), primary_key=True)
    auteur = db.Column(db.String(255), nullable=False)
    categorie = db.Column(db.String(255), nullable=False)
    jaar = db.Column(db.Integer, nullable=False)
    ISBN_nummer = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=True)

class leerling(db.Model):
    __tablename__ = 'leerlingen'
    naam = db.Column(db.String(255), nullable=False)
    voornaam = db.Column(db.String(255), nullable=False)
    klas = db.Column(db.String(20), nullable=False)
    ID = db.Column(db.Integer,  primary_key=True)

class BoekVerhuur(db.Model):
    __tablename__ = 'boek_verhuur'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    leerling_id = db.Column(db.Integer, db.ForeignKey('leerlingen.ID'), nullable=False)
    boek_isbn = db.Column(db.String(20), db.ForeignKey('boeken.ISBN_nummer'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

# al de routes om naar verschillende pagina's te gaan -> geen app route -> geen mogelijkheid om te veranderen van pagina

@app.route('/') # mag weg -> staat hier gwn om te weten of het werkt
def home():
    return "Database Verbonden!"

@app.route('/index.html') # startpagina
def index():
    return render_template('index.html')

@app.route('/Boeken.html') # boeken zoeken pagina
def boeken():
    return render_template('Boeken.html')

@app.route('/boeken',methods=['POST','GET']) # zoekt voor de boeken in de database en return ze terug
def boekenlijst():
    if request.method == 'POST':
        zoek_titel = request.form['search1'].strip() # onnodige spaties wegdoen om deftige resultaten weer te geven
        zoek_auteur = request.form['search2'].strip()
        zoek_categorie = request.form['search3'].strip()

        query = Boek.query

        if len(zoek_titel) >= 1: # checken dat er "iets" is ingevuld
            query = query.filter(Boek.titel.like(f"%{zoek_titel}%")) # zoeken in database en geeft terug wat er op lijkt in de velden door de ".like" functie
        if len(zoek_auteur) >= 1:
            query = query.filter(Boek.auteur.like(f"%{zoek_auteur}%"))
        if len(zoek_categorie) >= 1:
            query = query.filter(Boek.categorie.like(f"%{zoek_categorie}%"))

        zoekresultaten = query.all() # geeft resultaten aan de hand van de zoekvelden

        return render_template('Boeken.html', boeken=zoekresultaten)
    else:
        #boeken = Boek.query.all()  # Haal alle boeken uit de database indien er niks ingevuld is in zoekvelden
        return render_template('Boeken.html')

@app.route('/users')
def users():
    all_users = User.query.all()  # get al de users van de database
    return render_template('Boeken.html', users=all_users)

@app.route('/loginpagina.html')
def loginpagina():
    return render_template('loginpagina.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] # neemt de text uit de velden uit en zoekt in database
        password = request.form['password']

        # Zoek gebruiker in database
        user = User.query.filter_by(username=username).first() # geeft alleen maar het eerste resultaat dat het vindt en niet al de resultaten die hetzelfde lijken

        if user and check_password_hash(user.password, password): # wachtwoord encrypten voor privacy
            return redirect(url_for('Boeken.html')) # stuurt terug naar Boeken pagina om te controleren dat het in de database is
        else:
            return "Fout: verkeerde gebruikersnaam of wachtwoord."

    return render_template('loginpagina.html')

@app.route('/registreerpagina.html')
def registreerpagina():
    return render_template('registreerpagina.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'] # neemt text van de velden en zoekt ermee in de database
        lastname = request.form['lastname']
        password = request.form['password']
        email = request.form['e-mail']

        new_user = User(username=username, password=password, lastname=lastname, email=email) # nieuwe user aanmaken
        db.session.add(new_user) # toevoegen aan de database
        db.session.commit()

        return redirect(url_for('login')) # stuurt naar login pagina en kan dan ook onmiddelijk inloggen

    return render_template('registreerpagina.html')

@app.route('/leerkrachtenpagina.html')
def leerkrachtenpagina():
    return render_template('leerkrachtenpagina.html')

@app.route('/toevoegen.html')
def toevoegen():
    return render_template('toevoegen.html')

@app.route('/add_book', methods=['POST'])
def add_book():
    if request.method == 'POST':
        titel = request.form['titel'] # neemt text van de velden en stuurt door naar de database
        auteur = request.form['auteur']
        categorie = request.form['categorie']
        jaar = request.form['jaar']
        isbn = request.form['ISBN_nummer']

        # Maak een nieuw boekobject
        new_book = Boek(
            titel=titel,
            auteur=auteur,
            categorie=categorie,
            jaar=jaar,
            ISBN_nummer=isbn
        )

        # Voeg het boek toe aan de database
        db.session.add(new_book)
        db.session.commit()

        # Redirect naar de boekenlijst pagina
        return redirect(url_for('boekenlijst'))  # Dit zorgt ervoor dat je teruggaat naar de lijst van boeken

    return render_template('toevoegen.html')

@app.route('/uitlenen', methods=['POST'])
def uitlenen():
    if request.method == 'POST':
        # Get data van de form
        leerling_id = request.form.get('ID')
        boek_isbn = request.form.get('ISBN')

        # Check if beide velden zijn ingevuld
        if not leerling_id or not boek_isbn:
            return "Fout: Vul alle velden in!", 400

        # controleer if student in de database is
        leerling_obj = leerling.query.filter_by(ID=leerling_id).first() # eerste resultaat dat de database krijgt tonen
        if not leerling_obj:
            return "Leerling niet gevonden!", 404

        # Controleer of de boek bestaat
        boek_obj = Boek.query.filter_by(ISBN_nummer=boek_isbn).first()
        if not boek_obj:
            return "Boek niet gevonden!", 404

        # zet begin en eind datum (hier puur voor de test 4 weken gedaan)
        start_date = datetime.today().date()
        end_date = start_date + timedelta(weeks=4)

        # Toevoegen aan database
        nieuwe_verhuur = BoekVerhuur(
            leerling_id=leerling_id,
            boek_isbn=boek_isbn,
            start_date=start_date,
            end_date=end_date
        )

        db.session.add(nieuwe_verhuur)
        db.session.commit()

        return "success"

@app.route('/uitleensysteem', methods=['GET', 'POST'])
def leerlingenlijst():
    if request.method == 'POST':
        zoekterm = request.form['ID'] # neemt text van de invulvelden en zoekt ermee dan in de database
        zoekresultaten = leerling.query.filter(leerling.ID.like(f"%{zoekterm}%")).all() # hier return de database al de (soort)gelijke resultaten
        zoekterm_2 = request.form['ISBN']
        zoekresultaten_2 = Boek.query.filter(Boek.ISBN_nummer.like(f"%{zoekterm_2}%")).all()
        return render_template('uitleensysteem.html', leerlingen=zoekresultaten, boeken=zoekresultaten_2) #toont resultaten
    else:
        return render_template('uitleensysteem.html')

@app.route('/beheer.html')
def beheer():
    return render_template('beheer.html')

if __name__ == '__main__':
    app.run(debug=True) # hierdoor kan je aanpassingen maken in deze document Ctrl + s duwen en refreshen op de pagina en het resultaat hebben zonder de server volledig herop te starten
