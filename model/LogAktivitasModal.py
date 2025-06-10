from flask_mysqldb import MySQL
from datetime import datetime

class LogAktivitasModal:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all_today(self, limit=50):
        cur = self.mysql.connection.cursor()
        query = """
            SELECT al.timestamp, al.event_type, al.message, d.location
            FROM activity_log al
            LEFT JOIN detections d ON al.detection_id = d.id
            WHERE DATE(al.timestamp) = CURDATE()
            ORDER BY al.timestamp DESC
            LIMIT %s
        """
        cur.execute(query, (limit,))
        results = cur.fetchall()
        cur.close()
        return results

    def log_activity(self, event_type, message, detection_id=None):
        try:
            cur = self.mysql.connection.cursor()
            if detection_id:
                cur.execute(
                    "INSERT INTO activity_log (event_type, message, detection_id) VALUES (%s, %s, %s)",
                    (event_type, message, detection_id)
                )
            else:
                cur.execute(
                    "INSERT INTO activity_log (event_type, message) VALUES (%s, %s)",
                    (event_type, message)
                )
            self.mysql.connection.commit()
            cur.close()
        except Exception as e:
            print(f"Log activity error: {e}")
