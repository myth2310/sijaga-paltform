from flask_mysqldb import MySQL
from datetime import datetime

class CameraModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT id, room, source, create_date FROM camera")
        rows = cur.fetchall()
        cameras = []
        for row in rows:
            cam = {
                "id": row[0],
                "room": row[1],
                "source": row[2],
                "create_date": row[3]
            }
            cameras.append(cam)
        cur.close()
        return cameras

    def save_camera(self, room, source):
        cur = self.mysql.connection.cursor()
        query = "INSERT INTO camera (room, source) VALUES (%s, %s)"
        cur.execute(query, (room, source))
        self.mysql.connection.commit()
        cur.close()

    def get_camera_by_id(self, cam_id):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT id, room, source FROM camera WHERE id = %s", (cam_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return {"id": row[0], "room": row[1], "source": row[2]}
        return None

