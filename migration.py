from flask import Flask
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sijaga'

mysql = MySQL(app)

with app.app_context():
    cur = mysql.connection.cursor()
    password = '#admin'
    hashed_password = generate_password_hash(password)
    
    cur.execute(''' 
        INSERT IGNORE INTO users (username,password, email) VALUES
        (%s, %s,'adminsijaga@gmail.com')
    ''', ('Admin Sijaga', hashed_password))
    
    mysql.connection.commit()
    cur.close()
