from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sijaga'
mysql = MySQL(app)

with app.app_context():
    cur = mysql.connection.cursor()

    # Reset table users
    cur.execute("DELETE FROM users")
    cur.execute("ALTER TABLE users AUTO_INCREMENT = 1")

    # Reset table camera
    cur.execute("DELETE FROM camera")
    cur.execute("ALTER TABLE camera AUTO_INCREMENT = 1")

    # Reset table detections
    cur.execute("DELETE FROM detections")
    cur.execute("ALTER TABLE detections AUTO_INCREMENT = 1")

    # Reset table activity_log
    cur.execute("DELETE FROM activity_log")
    cur.execute("ALTER TABLE activity_log AUTO_INCREMENT = 1")

    mysql.connection.commit()
    print("Tabel berhasil di-reset.")
