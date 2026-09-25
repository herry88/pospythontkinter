import mysql.connector


def koneksi_database():

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pos_db"
    )

    return db
    