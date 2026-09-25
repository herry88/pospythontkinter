import tkinter as tk
from tkinter import messagebox
import sys
import os

# Import koneksi database dari folder database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.conn import koneksi_database


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Aplikasi POS")
        self.root.geometry("400x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#F3F4F6")

        # Posisikan window di tengah layar
        self.center_window(400, 480)

        # Container / Card Utama
        card = tk.Frame(self.root, bg="#FFFFFF", padx=30, pady=30, highlightthickness=1, highlightbackground="#E5E7EB")
        card.place(relx=0.5, rely=0.5, anchor="center", width=340, height=420)

        # Header Title
        title_label = tk.Label(
            card, 
            text="APLIKASI POS", 
            font=("Helvetica", 18, "bold"), 
            bg="#FFFFFF", 
            fg="#1F2937"
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = tk.Label(
            card, 
            text="Silakan login untuk melanjutkan", 
            font=("Helvetica", 9), 
            bg="#FFFFFF", 
            fg="#6B7280"
        )
        subtitle_label.pack(pady=(0, 25))

        # Username Field
        username_lbl = tk.Label(card, text="Username", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#374151")
        username_lbl.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(
            card, 
            font=("Helvetica", 11), 
            bg="#F9FAFB", 
            relief="solid", 
            bd=1, 
            highlightthickness=1,
            highlightcolor="#2563EB"
        )
        self.username_entry.pack(fill="x", ipady=6, pady=(0, 15))
        self.username_entry.focus()

        # Password Field
        password_lbl = tk.Label(card, text="Password", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#374151")
        password_lbl.pack(anchor="w", pady=(0, 5))

        self.password_entry = tk.Entry(
            card, 
            font=("Helvetica", 11), 
            show="*", 
            bg="#F9FAFB", 
            relief="solid", 
            bd=1, 
            highlightthickness=1,
            highlightcolor="#2563EB"
        )
        self.password_entry.pack(fill="x", ipady=6, pady=(0, 20))

        # Bind Enter key ke proses login
        self.password_entry.bind("<Return>", lambda event: self.proses_login())
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus())

        # Tombol Login
        login_btn = tk.Button(
            card,
            text="LOGIN",
            font=("Helvetica", 11, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            command=self.proses_login
        )
        login_btn.pack(fill="x", ipady=8, pady=(10, 0))

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def proses_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validasi input kosong
        if not username or not password:
            messagebox.showwarning("Peringatan", "Username dan Password tidak boleh kosong!")
            return

        try:
            # Koneksi ke database MySQL
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)

            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            cursor.close()
            db.close()

            if user:
                messagebox.showinfo(
                    "Login Berhasil", 
                    f"Selamat Datang, {user['nama']}!\nRole: {user['role'].upper()}"
                )
                self.buka_dashboard(user)
            else:
                messagebox.showerror("Login Gagal", "Username atau Password salah!")

        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal terhubung ke database:\n{e}")

    def buka_dashboard(self, user):
        from dashboard import DashboardApp
        self.root.destroy()
        dash_root = tk.Tk()
        app = DashboardApp(dash_root, user)
        app.show_dashboard_view()
        dash_root.mainloop()



if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
