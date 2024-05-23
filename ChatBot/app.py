from flask import Flask, render_template, request, redirect, url_for, flash
import speech_recognition as sr
from flask_mysqldb import MySQL
import MySQLdb.cursors
import secrets
import string

def generate_secret_key(length=24):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key

app = Flask(__name__)
app.config['SECRET_KEY'] = generate_secret_key()

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'chatbot'

mysql = MySQL(app)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    Error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE u_email = %s AND u_pass = %s', (email, password))
        account = cursor.fetchone()
        if account:
            #flash('Login successful!', 'success')
            return redirect(url_for('main'))
        else:
            Error = 'Invalid email or password!'
    return render_template('login.html', error=Error)

@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO user (u_name, u_email, u_pass) VALUES (%s, %s, %s)', (name, email, password))
        mysql.connection.commit()
        #flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('sign.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if request.method == 'POST':
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            flash("Listening for command...")
            audio_data = r.listen(source)
        try:
            text = r.recognize_google(audio_data)
            flash("Speech recognized: " + text)
        except sr.UnknownValueError:
            flash("Sorry, could not understand audio.")
        except sr.RequestError as e:
            flash("Could not request results; {0}".format(e))
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
