import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.conn import koneksi_database


class UserView:
    def __init__(self, parent_frame, user_data=None):
        self.parent_frame = parent_frame
        self.user_data = user_data or {"id": 1, "nama": "User", "username": "user", "role": "admin"}

        # Bersihkan widget yang ada sebelumnya di parent_frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.all_users = []
        self.selected_user_id = None
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # 1. Header Section
        header_frame = tk.Frame(self.parent_frame, bg="#F8FAFC")
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="👥 Kelola Data User & Role",
            font=("Helvetica", 16, "bold"),
            bg="#F8FAFC",
            fg="#1E293B"
        )
        title_label.pack(side="left")

        subtitle_label = tk.Label(
            header_frame,
            text="Manajemen akun pengguna, kata sandi, dan hak akses (Role: Admin / Kasir)",
            font=("Helvetica", 9),
            bg="#F8FAFC",
            fg="#64748B"
        )
        subtitle_label.pack(side="left", padx=(10, 0), pady=(4, 0))

        # 2. Action Bar (Search & Action Buttons)
        action_bar = tk.Frame(self.parent_frame, bg="#F8FAFC")
        action_bar.pack(fill="x", pady=(0, 15))

        # Search Box Left
        search_frame = tk.Frame(action_bar, bg="#FFFFFF", highlightthickness=1, highlightbackground="#CBD5E1")
        search_frame.pack(side="left", ipady=2, ipadx=5)

        search_icon = tk.Label(search_frame, text="🔍", bg="#FFFFFF", fg="#64748B", font=("Helvetica", 10))
        search_icon.pack(side="left", padx=(5, 2))

        self.search_entry = tk.Entry(
            search_frame,
            font=("Helvetica", 10),
            bd=0,
            bg="#FFFFFF",
            relief="flat",
            width=25
        )
        self.search_entry.pack(side="left", padx=5, ipady=3)
        self.search_entry.bind("<KeyRelease>", lambda event: self.filter_data())

        # Buttons Right
        btn_container = tk.Frame(action_bar, bg="#F8FAFC")
        btn_container.pack(side="right")

        btn_tambah = tk.Button(
            btn_container,
            text="➕ Tambah User",
            font=("Helvetica", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.show_tambah_dialog
        )
        btn_tambah.pack(side="left", padx=(0, 8))

        btn_edit = tk.Button(
            btn_container,
            text="✏️ Edit User & Role",
            font=("Helvetica", 9, "bold"),
            bg="#F59E0B",
            fg="#FFFFFF",
            activebackground="#D97706",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.show_edit_dialog
        )
        btn_edit.pack(side="left", padx=(0, 8))

        btn_pass = tk.Button(
            btn_container,
            text="🔑 Ganti Password",
            font=("Helvetica", 9, "bold"),
            bg="#8B5CF6",
            fg="#FFFFFF",
            activebackground="#7C3AED",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.show_ganti_password_dialog
        )
        btn_pass.pack(side="left", padx=(0, 8))

        btn_hapus = tk.Button(
            btn_container,
            text="🗑️ Hapus",
            font=("Helvetica", 9, "bold"),
            bg="#EF4444",
            fg="#FFFFFF",
            activebackground="#DC2626",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.hapus_user
        )
        btn_hapus.pack(side="left", padx=(0, 8))

        btn_refresh = tk.Button(
            btn_container,
            text="🔄 Refresh",
            font=("Helvetica", 9),
            bg="#64748B",
            fg="#FFFFFF",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=6,
            command=self.load_data
        )
        btn_refresh.pack(side="left")

        # 3. Table Container Frame
        table_container = tk.Frame(self.parent_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0")
        table_container.pack(fill="both", expand=True)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 10, "bold"),
            background="#F1F5F9",
            foreground="#1E293B",
            relief="flat"
        )
        style.configure(
            "Treeview",
            font=("Helvetica", 10),
            rowheight=32,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#0F172A"
        )
        style.map("Treeview", background=[("selected", "#E0F2FE")], foreground=[("selected", "#0369A1")])

        columns = ("id", "nama", "username", "role")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=12)

        self.tree.heading("id", text="ID User")
        self.tree.heading("nama", text="Nama Lengkap")
        self.tree.heading("username", text="Username")
        self.tree.heading("role", text="Role / Hak Akses")

        self.tree.column("id", width=80, anchor="center")
        self.tree.column("nama", width=250, anchor="w")
        self.tree.column("username", width=200, anchor="w")
        self.tree.column("role", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda event: self.show_edit_dialog())

    def load_data(self):
        """Memuat daftar user dari database"""
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id, username, nama, role FROM users ORDER BY id ASC")
            self.all_users = cursor.fetchall()
            cursor.close()
            db.close()

            self.render_tree(self.all_users)
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data user:\n{e}")

    def render_tree(self, data):
        """Menampilkan data ke Treeview"""
        for r in self.tree.get_children():
            self.tree.delete(r)

        for u in data:
            role_display = u['role'].upper() if u['role'] else "KASIR"
            if role_display == "ADMIN":
                role_display = "⭐ ADMIN"
            else:
                role_display = "👤 KASIR"

            self.tree.insert("", "end", values=(
                u['id'],
                u['nama'],
                u['username'],
                role_display
            ))

    def filter_data(self):
        """Filter data berdasarkan pencarian Nama / Username"""
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            self.render_tree(self.all_users)
            return

        filtered = [
            u for u in self.all_users
            if keyword in u['nama'].lower() or keyword in u['username'].lower()
        ]
        self.render_tree(filtered)

    def show_tambah_dialog(self):
        """Modal dialog Tambah User Baru"""
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("➕ Tambah User Baru")
        dialog.geometry("450x420")
        dialog.resizable(False, False)
        dialog.configure(bg="#F8FAFC")
        dialog.transient(self.parent_frame.winfo_toplevel())
        dialog.grab_set()

        # Posisikan dialog di tengah
        screen_w = dialog.winfo_screenwidth()
        screen_h = dialog.winfo_screenheight()
        x = (screen_w // 2) - 225
        y = (screen_h // 2) - 210
        dialog.geometry(f"450x420+{x}+{y}")

        # Header Dialog
        header = tk.Frame(dialog, bg="#2563EB", padx=20, pady=15)
        header.pack(fill="x")

        lbl_title = tk.Label(header, text="Tambah User Baru", font=("Helvetica", 12, "bold"), bg="#2563EB", fg="#FFFFFF")
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(header, text="Isi formulir di bawah ini untuk membuat akun pengguna baru", font=("Helvetica", 8), bg="#2563EB", fg="#DBEAFE")
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Form Container
        form_frame = tk.Frame(dialog, bg="#F8FAFC", padx=25, pady=15)
        form_frame.pack(fill="both", expand=True)

        # Nama Lengkap
        tk.Label(form_frame, text="Nama Lengkap:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        entry_nama = tk.Entry(form_frame, font=("Helvetica", 10), bg="#FFFFFF", relief="solid", bd=1)
        entry_nama.pack(fill="x", ipady=4, pady=(0, 10))

        # Username
        tk.Label(form_frame, text="Username:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        entry_username = tk.Entry(form_frame, font=("Helvetica", 10), bg="#FFFFFF", relief="solid", bd=1)
        entry_username.pack(fill="x", ipady=4, pady=(0, 10))

        # Password
        tk.Label(form_frame, text="Password:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        entry_pass = tk.Entry(form_frame, font=("Helvetica", 10), show="*", bg="#FFFFFF", relief="solid", bd=1)
        entry_pass.pack(fill="x", ipady=4, pady=(0, 10))

        # Role Combobox
        tk.Label(form_frame, text="Role / Hak Akses:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        cb_role = ttk.Combobox(form_frame, values=["kasir", "admin"], state="readonly", font=("Helvetica", 10))
        cb_role.current(0)  # Default kasir
        cb_role.pack(fill="x", ipady=2, pady=(0, 15))

        def simpan():
            nama = entry_nama.get().strip()
            username = entry_username.get().strip()
            password = entry_pass.get().strip()
            role = cb_role.get().strip().lower()

            if not nama or not username or not password:
                messagebox.showwarning("Input Kosong", "Semua bidang (Nama, Username, Password) wajib diisi!")
                return

            try:
                db = koneksi_database()
                cursor = db.cursor()

                # Cek apakah username sudah dipakai
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    messagebox.showwarning("Username Sudah Ada", f"Username '{username}' sudah digunakan. Silakan pilih username lain.")
                    cursor.close()
                    db.close()
                    return

                # Simpan user baru
                cursor.execute(
                    "INSERT INTO users (nama, username, password, role) VALUES (%s, %s, %s, %s)",
                    (nama, username, password, role)
                )
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", f"User '{nama}' berhasil ditambahkan dengan role '{role.upper()}'!")
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menambahkan user:\n{e}")

        # Buttons Footer
        btn_frame = tk.Frame(dialog, bg="#F1F5F9", padx=20, pady=10)
        btn_frame.pack(fill="x", side="bottom")

        btn_simpan = tk.Button(
            btn_frame,
            text="💾 Simpan User",
            font=("Helvetica", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=simpan
        )
        btn_simpan.pack(side="right", padx=(5, 0))

        btn_batal = tk.Button(
            btn_frame,
            text="Batal",
            font=("Helvetica", 9),
            bg="#64748B",
            fg="#FFFFFF",
            activebackground="#475569",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=dialog.destroy
        )
        btn_batal.pack(side="right")

    def show_edit_dialog(self):
        """Modal dialog Edit Data User & Role"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Pilih User", "Silakan pilih salah satu user dari tabel untuk diedit.")
            return

        values = self.tree.item(selected_item[0], "values")
        user_id = values[0]
        curr_nama = values[1]
        curr_username = values[2]
        raw_role = values[3].replace("⭐ ", "").replace("👤 ", "").strip().lower()

        dialog = tk.Toplevel(self.parent_frame)
        dialog.title(f"✏️ Edit User - {curr_username}")
        dialog.geometry("450x380")
        dialog.resizable(False, False)
        dialog.configure(bg="#F8FAFC")
        dialog.transient(self.parent_frame.winfo_toplevel())
        dialog.grab_set()

        # Posisikan dialog di tengah
        screen_w = dialog.winfo_screenwidth()
        screen_h = dialog.winfo_screenheight()
        x = (screen_w // 2) - 225
        y = (screen_h // 2) - 190
        dialog.geometry(f"450x380+{x}+{y}")

        # Header Dialog
        header = tk.Frame(dialog, bg="#F59E0B", padx=20, pady=15)
        header.pack(fill="x")

        lbl_title = tk.Label(header, text=f"Edit User & Role: {curr_username}", font=("Helvetica", 12, "bold"), bg="#F59E0B", fg="#FFFFFF")
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(header, text="Ubah nama, username, atau hak akses (role) dari akun pengguna ini", font=("Helvetica", 8), bg="#F59E0B", fg="#FEF3C7")
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Form Container
        form_frame = tk.Frame(dialog, bg="#F8FAFC", padx=25, pady=15)
        form_frame.pack(fill="both", expand=True)

        # Nama Lengkap
        tk.Label(form_frame, text="Nama Lengkap:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        entry_nama = tk.Entry(form_frame, font=("Helvetica", 10), bg="#FFFFFF", relief="solid", bd=1)
        entry_nama.insert(0, curr_nama)
        entry_nama.pack(fill="x", ipady=4, pady=(0, 12))

        # Username
        tk.Label(form_frame, text="Username:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        entry_username = tk.Entry(form_frame, font=("Helvetica", 10), bg="#FFFFFF", relief="solid", bd=1)
        entry_username.insert(0, curr_username)
        entry_username.pack(fill="x", ipady=4, pady=(0, 12))

        # Role Combobox
        tk.Label(form_frame, text="Role / Hak Akses:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        cb_role = ttk.Combobox(form_frame, values=["kasir", "admin"], state="readonly", font=("Helvetica", 10))
        if raw_role in ["admin", "kasir"]:
            cb_role.set(raw_role)
        else:
            cb_role.set("kasir")
        cb_role.pack(fill="x", ipady=2, pady=(0, 15))

        def update_user():
            nama = entry_nama.get().strip()
            username = entry_username.get().strip()
            new_role = cb_role.get().strip().lower()

            if not nama or not username:
                messagebox.showwarning("Input Kosong", "Nama Lengkap dan Username tidak boleh kosong!")
                return

            try:
                db = koneksi_database()
                cursor = db.cursor()

                # Cek duplikasi username (kecuali username milik user ini sendiri)
                cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (username, user_id))
                if cursor.fetchone():
                    messagebox.showwarning("Username Sudah Ada", f"Username '{username}' sudah digunakan oleh user lain!")
                    cursor.close()
                    db.close()
                    return

                # Update data user & role
                cursor.execute(
                    "UPDATE users SET nama = %s, username = %s, role = %s WHERE id = %s",
                    (nama, username, new_role, user_id)
                )
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", f"Data user '{username}' berhasil diperbarui!")
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memperbarui data user:\n{e}")

        # Buttons Footer
        btn_frame = tk.Frame(dialog, bg="#F1F5F9", padx=20, pady=10)
        btn_frame.pack(fill="x", side="bottom")

        btn_simpan = tk.Button(
            btn_frame,
            text="💾 Simpan Perubahan",
            font=("Helvetica", 9, "bold"),
            bg="#F59E0B",
            fg="#FFFFFF",
            activebackground="#D97706",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=update_user
        )
        btn_simpan.pack(side="right", padx=(5, 0))

        btn_batal = tk.Button(
            btn_frame,
            text="Batal",
            font=("Helvetica", 9),
            bg="#64748B",
            fg="#FFFFFF",
            activebackground="#475569",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=dialog.destroy
        )
        btn_batal.pack(side="right")

    def show_ganti_password_dialog(self):
        """Modal dialog khusus Ganti Password User"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Pilih User", "Silakan pilih salah satu user dari tabel untuk mengganti password.")
            return

        values = self.tree.item(selected_item[0], "values")
        user_id = values[0]
        curr_username = values[2]

        dialog = tk.Toplevel(self.parent_frame)
        dialog.title(f"🔑 Ganti Password - {curr_username}")
        dialog.geometry("420x320")
        dialog.resizable(False, False)
        dialog.configure(bg="#F8FAFC")
        dialog.transient(self.parent_frame.winfo_toplevel())
        dialog.grab_set()

        # Posisikan dialog di tengah
        screen_w = dialog.winfo_screenwidth()
        screen_h = dialog.winfo_screenheight()
        x = (screen_w // 2) - 210
        y = (screen_h // 2) - 160
        dialog.geometry(f"420x320+{x}+{y}")

        # Header Dialog
        header = tk.Frame(dialog, bg="#8B5CF6", padx=20, pady=15)
        header.pack(fill="x")

        lbl_title = tk.Label(header, text=f"Ganti Password: {curr_username}", font=("Helvetica", 12, "bold"), bg="#8B5CF6", fg="#FFFFFF")
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(header, text="Masukkan kata sandi baru untuk akun ini", font=("Helvetica", 8), bg="#8B5CF6", fg="#F3E8FF")
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Form Container
        form_frame = tk.Frame(dialog, bg="#F8FAFC", padx=25, pady=15)
        form_frame.pack(fill="both", expand=True)

        # Password Baru
        tk.Label(form_frame, text="Password Baru:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        entry_pass1 = tk.Entry(form_frame, font=("Helvetica", 10), show="*", bg="#FFFFFF", relief="solid", bd=1)
        entry_pass1.pack(fill="x", ipady=4, pady=(0, 12))

        # Konfirmasi Password
        tk.Label(form_frame, text="Konfirmasi Password Baru:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#334155").pack(anchor="w", pady=(0, 2))
        entry_pass2 = tk.Entry(form_frame, font=("Helvetica", 10), show="*", bg="#FFFFFF", relief="solid", bd=1)
        entry_pass2.pack(fill="x", ipady=4, pady=(0, 15))

        def update_password():
            pass1 = entry_pass1.get().strip()
            pass2 = entry_pass2.get().strip()

            if not pass1:
                messagebox.showwarning("Input Kosong", "Password baru tidak boleh kosong!")
                return

            if pass1 != pass2:
                messagebox.showwarning("Password Tidak Cocok", "Password baru dan Konfirmasi Password tidak sama!")
                return

            try:
                db = koneksi_database()
                cursor = db.cursor()

                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (pass1, user_id))
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", f"Password untuk user '{curr_username}' berhasil diperbarui!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memperbarui password:\n{e}")

        # Buttons Footer
        btn_frame = tk.Frame(dialog, bg="#F1F5F9", padx=20, pady=10)
        btn_frame.pack(fill="x", side="bottom")

        btn_simpan = tk.Button(
            btn_frame,
            text="🔑 Update Password",
            font=("Helvetica", 9, "bold"),
            bg="#8B5CF6",
            fg="#FFFFFF",
            activebackground="#7C3AED",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=update_password
        )
        btn_simpan.pack(side="right", padx=(5, 0))

        btn_batal = tk.Button(
            btn_frame,
            text="Batal",
            font=("Helvetica", 9),
            bg="#64748B",
            fg="#FFFFFF",
            activebackground="#475569",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=dialog.destroy
        )
        btn_batal.pack(side="right")

    def hapus_user(self):
        """Menghapus user terpilih"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Pilih User", "Silakan pilih salah satu user dari tabel yang ingin dihapus.")
            return

        values = self.tree.item(selected_item[0], "values")
        user_id = int(values[0])
        nama_user = values[1]
        username = values[2]

        # Mencegah user menghapus akun yang sedang dipakai sendiri saat ini
        logged_in_id = self.user_data.get("id")
        if logged_in_id and int(logged_in_id) == user_id:
            messagebox.showerror("Aksi Ditolak", "Anda tidak dapat menghapus akun Anda sendiri yang sedang aktif digunakan saat ini!")
            return

        confirm = messagebox.askyesno(
            "Konfirmasi Hapus User",
            f"Apakah Anda yakin ingin menghapus akun user '{nama_user}' ({username})?\n\nTindakan ini tidak dapat dibatalkan."
        )

        if confirm:
            try:
                db = koneksi_database()
                cursor = db.cursor()

                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", f"User '{nama_user}' telah berhasil dihapus!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error Database", f"Gagal menghapus user:\n\nSebab error: {e}")
