from flask_mysqldb import MySQL

class UserModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_user_by_email(self, email):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        return user

    def get_user_all(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        return users
    
    def insert_user(self, name, email, role, password):
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(
                "INSERT INTO users (username, email, role, password) VALUES (%s, %s, %s, %s)",
                (name, email, role, password)
            )
            self.mysql.connection.commit()
            message = f"User '{name}' dengan peran '{role}' ditambahkan ke sistem."
            cur.execute(
                "INSERT INTO activity_log (event_type, message) VALUES (%s, %s)",
                ("USER_CREATED", message)
            )
            self.mysql.connection.commit()

            cur.close()
            return True
        except Exception as e:
            print(f"Insert error: {e}")
            return False
