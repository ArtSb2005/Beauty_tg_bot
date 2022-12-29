import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def add_services(self, name: str):
        with self.conn:
            self.cursor.execute("""INSERT INTO services (name) VALUES (?)""",
                                (name,))

    def get_services(self):
        with self.conn:
            result = self.cursor.execute("SELECT * FROM services").fetchall()
            return result

    def get_time(self):
        with self.conn:
            result = self.cursor.execute("SELECT * FROM time").fetchall()
            return result

    def add_user_records(self, user_id, name, time, user_name, phone, date):
        with self.conn:
            self.cursor.execute("""INSERT INTO records (name, user_id, number_phone, services, time, date) 
            VALUES (?, ?, ?, ?, ?, ?)""",
                                (user_name, user_id, phone, name, time, date))

    def get_all_records(self):
        with self.conn:
            result = self.cursor.execute("SELECT * FROM records").fetchall()
            return result

    def get_records(self, user_id):
        with self.conn:
            result = self.cursor.execute("SELECT * FROM records WHERE user_id = ?", (user_id,)).fetchall()
            return result

    def get_time_records(self):
        with self.conn:
            result = self.cursor.execute("SELECT time, date FROM records").fetchall()
            return result

    def delete_records(self, id):
        with self.conn:
            return self.cursor.execute("""DELETE FROM records WHERE id = ?""", (id,))