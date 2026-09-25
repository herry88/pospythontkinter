import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.conn import koneksi_database


class KategoriView:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        # Clear existing widgets in parent_frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.selected_item_id = None
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # 1. Header Section
        header_frame = tk.Frame(self.parent_frame, bg="#F8FAFC")
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="🏷️ Kelola Data Kategori",
            font=("Helvetica", 16, "bold"),
            bg="#F8FAFC",
            fg="#1E293B"
        )
        title_label.pack(side="left")

        subtitle_label = tk.Label(
            header_frame,
            text="Manajemen kategori barang toko Anda",
            font=("Helvetica", 9),
            bg="#F8FAFC",
            fg="#64748B"
        )
        subtitle_label.pack(side="left", padx=(10, 0), pady=(4, 0))

        # 2. Top Action Bar (Search & Buttons)
        action_bar = tk.Frame(self.parent_frame, bg="#F8FAFC")
        action_bar.pack(fill="x", pady=(0, 15))

        # Search Box
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
            text="➕ Tambah Kategori",
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
            text="✏️ Edit",
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
            command=self.hapus_kategori
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
            rowheight=30,
            background="#FFFFFF",
            fieldbackground="#FFFFFF"
        )
        style.map("Treeview", background=[("selected", "#3B82F6")], foreground=[("selected", "#FFFFFF")])

        # Treeview Table
        columns = ("id", "nama_kategori")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID", anchor="center")
        self.tree.heading("nama_kategori", text="NAMA KATEGORI", anchor="w")

        self.tree.column("id", width=80, minwidth=60, anchor="center")
        self.tree.column("nama_kategori", width=400, minwidth=200, anchor="w")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scrollbar.pack(side="right", fill="y", pady=1)

        # Double click action to edit
        self.tree.bind("<Double-1>", lambda event: self.show_edit_dialog())

        # Footer / Info Bar
        footer_frame = tk.Frame(self.parent_frame, bg="#F8FAFC")
        footer_frame.pack(fill="x", pady=(10, 0))

        self.lbl_count = tk.Label(
            footer_frame,
            text="Total: 0 Kategori",
            font=("Helvetica", 9, "bold"),
            bg="#F8FAFC",
            fg="#64748B"
        )
        self.lbl_count.pack(side="left")

    def load_data(self):
        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id, nama_kategori FROM categories ORDER BY id ASC")
            rows = cursor.fetchall()

            self.all_data = rows
            count = 0
            for row in rows:
                self.tree.insert("", "end", values=(row["id"], row["nama_kategori"]))
                count += 1

            self.lbl_count.config(text=f"Total: {count} Kategori")
            cursor.close()
            db.close()
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data kategori:\n{e}")

    def filter_data(self):
        query = self.search_entry.get().strip().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for row in getattr(self, "all_data", []):
            if query in str(row["id"]).lower() or query in row["nama_kategori"].lower():
                self.tree.insert("", "end", values=(row["id"], row["nama_kategori"]))
                count += 1

        self.lbl_count.config(text=f"Total: {count} Kategori (filtered)")

    def get_selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih data kategori terlebih dahulu dari tabel!")
            return None
        values = self.tree.item(selected[0], "values")
        return {"id": values[0], "nama_kategori": values[1]}

    def show_tambah_dialog(self):
        dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
        dialog.title("Tambah Kategori")
        dialog.geometry("380x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg="#FFFFFF")
        self.center_dialog(dialog, 380, 200)

        # Header
        lbl_header = tk.Label(dialog, text="Tambah Kategori Baru", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#1E293B")
        lbl_header.pack(pady=(15, 10))

        # Input
        lbl_nama = tk.Label(dialog, text="Nama Kategori", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151")
        lbl_nama.pack(anchor="w", padx=30, pady=(5, 2))

        entry_nama = tk.Entry(dialog, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_nama.pack(fill="x", padx=30, ipady=5)
        entry_nama.focus()

        # Submit Action
        def simpan():
            nama = entry_nama.get().strip()
            if not nama:
                messagebox.showwarning("Peringatan", "Nama kategori tidak boleh kosong!", parent=dialog)
                return

            try:
                db = koneksi_database()
                cursor = db.cursor()
                cursor.execute("INSERT INTO categories (nama_kategori) VALUES (%s)", (nama,))
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", "Kategori berhasil ditambahkan!", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan data:\n{e}", parent=dialog)

        entry_nama.bind("<Return>", lambda event: simpan())

        # Buttons
        btn_frame = tk.Frame(dialog, bg="#FFFFFF")
        btn_frame.pack(fill="x", padx=30, pady=(20, 0))

        btn_simpan = tk.Button(
            btn_frame, text="Simpan", font=("Helvetica", 9, "bold"),
            bg="#2563EB", fg="#FFFFFF", relief="flat", cursor="hand2", padx=15, pady=5, command=simpan
        )
        btn_simpan.pack(side="right", padx=(5, 0))

        btn_batal = tk.Button(
            btn_frame, text="Batal", font=("Helvetica", 9),
            bg="#E2E8F0", fg="#475569", relief="flat", cursor="hand2", padx=15, pady=5, command=dialog.destroy
        )
        btn_batal.pack(side="right")

    def show_edit_dialog(self):
        selected = self.get_selected_item()
        if not selected:
            return

        dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
        dialog.title("Edit Kategori")
        dialog.geometry("380x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg="#FFFFFF")
        self.center_dialog(dialog, 380, 200)

        # Header
        lbl_header = tk.Label(dialog, text=f"Edit Kategori (ID: {selected['id']})", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#1E293B")
        lbl_header.pack(pady=(15, 10))

        # Input
        lbl_nama = tk.Label(dialog, text="Nama Kategori", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151")
        lbl_nama.pack(anchor="w", padx=30, pady=(5, 2))

        entry_nama = tk.Entry(dialog, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_nama.pack(fill="x", padx=30, ipady=5)
        entry_nama.insert(0, selected["nama_kategori"])
        entry_nama.focus()

        # Update Action
        def update():
            nama = entry_nama.get().strip()
            if not nama:
                messagebox.showwarning("Peringatan", "Nama kategori tidak boleh kosong!", parent=dialog)
                return

            try:
                db = koneksi_database()
                cursor = db.cursor()
                cursor.execute("UPDATE categories SET nama_kategori = %s WHERE id = %s", (nama, selected["id"]))
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", "Kategori berhasil diperbarui!", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal mengoperasikan data:\n{e}", parent=dialog)

        entry_nama.bind("<Return>", lambda event: update())

        # Buttons
        btn_frame = tk.Frame(dialog, bg="#FFFFFF")
        btn_frame.pack(fill="x", padx=30, pady=(20, 0))

        btn_simpan = tk.Button(
            btn_frame, text="Update", font=("Helvetica", 9, "bold"),
            bg="#F59E0B", fg="#FFFFFF", relief="flat", cursor="hand2", padx=15, pady=5, command=update
        )
        btn_simpan.pack(side="right", padx=(5, 0))

        btn_batal = tk.Button(
            btn_frame, text="Batal", font=("Helvetica", 9),
            bg="#E2E8F0", fg="#475569", relief="flat", cursor="hand2", padx=15, pady=5, command=dialog.destroy
        )
        btn_batal.pack(side="right")

    def hapus_kategori(self):
        selected = self.get_selected_item()
        if not selected:
            return

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus kategori '{selected['nama_kategori']}'?"
        )
        if konfirmasi:
            try:
                db = koneksi_database()
                cursor = db.cursor()
                cursor.execute("DELETE FROM categories WHERE id = %s", (selected["id"],))
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", "Kategori berhasil dihapus!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data kategori:\n{e}")

    def center_dialog(self, dialog, width, height):
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Kategori View")
    root.geometry("800x500")
    frame = tk.Frame(root, bg="#F8FAFC", padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    app = KategoriView(frame)
    root.mainloop()
