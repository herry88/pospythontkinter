from conn import koneksi_database


db = koneksi_database()

if db.is_connected():
    print("Database berhasil terhubung")
else:
    print("Database gagal terhubung")

db.close()