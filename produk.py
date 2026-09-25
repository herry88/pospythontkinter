import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.conn import koneksi_database


class ProdukView:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        # Clear existing widgets in parent_frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.kategori_map = {}  # {nama_kategori: id}
        self.kategori_list = []
        self.build_ui()
        self.load_kategori_data()
        self.load_data()

    def build_ui(self):
        # 1. Header Section
        header_frame = tk.Frame(self.parent_frame, bg="#F8FAFC")
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text="📦 Kelola Data Produk",
            font=("Helvetica", 16, "bold"),
            bg="#F8FAFC",
            fg="#1E293B"
        )
        title_label.pack(side="left")

        subtitle_label = tk.Label(
            header_frame,
            text="Manajemen stok, harga, dan data barang toko Anda",
            font=("Helvetica", 9),
            bg="#F8FAFC",
            fg="#64748B"
        )
        subtitle_label.pack(side="left", padx=(10, 0), pady=(4, 0))

        # 2. Action Bar (Search, Category Filter & Buttons)
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
            width=22
        )
        self.search_entry.pack(side="left", padx=5, ipady=3)
        self.search_entry.bind("<KeyRelease>", lambda event: self.filter_data())

        # Category Filter Dropdown
        filter_lbl = tk.Label(action_bar, text="Kategori:", font=("Helvetica", 9, "bold"), bg="#F8FAFC", fg="#475569")
        filter_lbl.pack(side="left", padx=(15, 5))

        self.filter_kategori_cb = ttk.Combobox(action_bar, state="readonly", width=15, font=("Helvetica", 9))
        self.filter_kategori_cb.pack(side="left", ipady=3, padx=(0, 25))
        self.filter_kategori_cb.bind("<<ComboboxSelected>>", lambda event: self.filter_data())

        # Buttons Right
        btn_container = tk.Frame(action_bar, bg="#F8FAFC")
        btn_container.pack(side="right")

        btn_tambah = tk.Button(
            btn_container,
            text="➕ Tambah Produk",
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
            command=self.hapus_produk
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

        # Treeview Table Columns
        columns = ("id", "kode_barang", "nama_barang", "kategori", "harga", "stok", "satuan")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID", anchor="center")
        self.tree.heading("kode_barang", text="Kode Barang", anchor="center")
        self.tree.heading("nama_barang", text="Nama Barang", anchor="w")
        self.tree.heading("kategori", text="Kategori", anchor="w")
        self.tree.heading("harga", text="Harga (Rp)", anchor="e")
        self.tree.heading("stok", text="Stok", anchor="center")
        self.tree.heading("satuan", text="Satuan", anchor="center")

        self.tree.column("id", width=50, minwidth=40, anchor="center")
        self.tree.column("kode_barang", width=110, minwidth=90, anchor="center")
        self.tree.column("nama_barang", width=220, minwidth=150, anchor="w")
        self.tree.column("kategori", width=140, minwidth=100, anchor="w")
        self.tree.column("harga", width=120, minwidth=90, anchor="e")
        self.tree.column("stok", width=70, minwidth=50, anchor="center")
        self.tree.column("satuan", width=80, minwidth=60, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scrollbar.pack(side="right", fill="y", pady=1)

        # Double click to edit
        self.tree.bind("<Double-1>", lambda event: self.show_edit_dialog())

        # 4. Footer Info Bar
        footer_frame = tk.Frame(self.parent_frame, bg="#F8FAFC")
        footer_frame.pack(fill="x", pady=(10, 0))

        self.lbl_count = tk.Label(
            footer_frame,
            text="Total: 0 Produk",
            font=("Helvetica", 9, "bold"),
            bg="#F8FAFC",
            fg="#64748B"
        )
        self.lbl_count.pack(side="left")

    def load_kategori_data(self):
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id, nama_kategori FROM categories ORDER BY nama_kategori ASC")
            rows = cursor.fetchall()
            cursor.close()
            db.close()

            self.kategori_map = {row["nama_kategori"]: row["id"] for row in rows}
            self.kategori_list = list(self.kategori_map.keys())

            self.filter_kategori_cb["values"] = ["Semua Kategori"] + self.kategori_list
            self.filter_kategori_cb.current(0)
        except Exception as e:
            print("Error loading kategori dropdown:", e)

    def load_data(self):
        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT p.id, p.kode_barang, p.nama_barang, p.kategori_id, c.nama_kategori,
                       p.harga, p.stok, p.satuan, p.created_at
                FROM products p
                LEFT JOIN categories c ON p.kategori_id = c.id
                ORDER BY p.id ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            db.close()

            self.all_data = rows
            count = 0
            for row in rows:
                harga_formatted = f"Rp {float(row['harga']):,.0f}".replace(",", ".")
                kategori_name = row["nama_kategori"] if row["nama_kategori"] else "-"
                
                self.tree.insert(
                    "", 
                    "end", 
                    values=(
                        row["id"],
                        row["kode_barang"],
                        row["nama_barang"],
                        kategori_name,
                        harga_formatted,
                        row["stok"],
                        row["satuan"] or "pcs"
                    )
                )
                count += 1

            self.lbl_count.config(text=f"Total: {count} Produk")
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data produk:\n{e}")

    def filter_data(self):
        query = self.search_entry.get().strip().lower()
        selected_kat = self.filter_kategori_cb.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for row in getattr(self, "all_data", []):
            kat_nama = row["nama_kategori"] if row["nama_kategori"] else "-"
            
            # Check Category Filter
            match_kat = (selected_kat == "Semua Kategori") or (kat_nama == selected_kat)
            
            # Check Text Search Filter
            match_text = (
                query in str(row["id"]).lower()
                or query in str(row["kode_barang"]).lower()
                or query in str(row["nama_barang"]).lower()
                or query in kat_nama.lower()
            )

            if match_kat and match_text:
                harga_formatted = f"Rp {float(row['harga']):,.0f}".replace(",", ".")
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["id"],
                        row["kode_barang"],
                        row["nama_barang"],
                        kat_nama,
                        harga_formatted,
                        row["stok"],
                        row["satuan"] or "pcs"
                    )
                )
                count += 1

        self.lbl_count.config(text=f"Total: {count} Produk (filtered)")

    def get_selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih produk terlebih dahulu dari tabel!")
            return None
        
        values = self.tree.item(selected[0], "values")
        
        # Find raw row data
        selected_id = int(values[0])
        for row in getattr(self, "all_data", []):
            if row["id"] == selected_id:
                return row
        return None

    def generate_next_kode(self):
        try:
            db = koneksi_database()
            cursor = db.cursor()
            cursor.execute("SELECT MAX(id) FROM products")
            max_id = cursor.fetchone()[0] or 0
            cursor.close()
            db.close()
            return f"BRG{max_id + 1:03d}"
        except Exception:
            return "BRG001"

    def show_tambah_dialog(self):
        self.load_kategori_data()  # Refresh dropdown data

        dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
        dialog.title("Tambah Produk Baru")
        dialog.geometry("450x480")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg="#FFFFFF")
        self.center_dialog(dialog, 450, 480)

        # Header
        lbl_header = tk.Label(dialog, text="Tambah Produk Baru", font=("Helvetica", 14, "bold"), bg="#FFFFFF", fg="#1E293B")
        lbl_header.pack(pady=(15, 15))

        form_frame = tk.Frame(dialog, bg="#FFFFFF")
        form_frame.pack(fill="both", expand=True, padx=30)

        # 1. Kode Barang
        tk.Label(form_frame, text="Kode Barang*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        entry_kode = tk.Entry(form_frame, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_kode.pack(fill="x", ipady=4, pady=(2, 10))
        entry_kode.insert(0, self.generate_next_kode())

        # 2. Nama Barang
        tk.Label(form_frame, text="Nama Barang*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        entry_nama = tk.Entry(form_frame, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_nama.pack(fill="x", ipady=4, pady=(2, 10))
        entry_nama.focus()

        # 3. Kategori
        tk.Label(form_frame, text="Kategori*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        cb_kategori = ttk.Combobox(form_frame, state="readonly", values=self.kategori_list, font=("Helvetica", 10))
        cb_kategori.pack(fill="x", ipady=4, pady=(2, 10))
        if self.kategori_list:
            cb_kategori.current(0)

        # 4. Harga & Stok (Side-by-Side)
        hs_frame = tk.Frame(form_frame, bg="#FFFFFF")
        hs_frame.pack(fill="x", pady=(0, 10))

        # Harga
        h_frame = tk.Frame(hs_frame, bg="#FFFFFF")
        h_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(h_frame, text="Harga (Rp)*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        entry_harga = tk.Entry(h_frame, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_harga.pack(fill="x", ipady=4, pady=(2, 0))
        entry_harga.insert(0, "0")

        # Stok
        s_frame = tk.Frame(hs_frame, bg="#FFFFFF")
        s_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(s_frame, text="Stok*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        entry_stok = tk.Entry(s_frame, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_stok.pack(fill="x", ipady=4, pady=(2, 0))
        entry_stok.insert(0, "0")

        # 5. Satuan
        tk.Label(form_frame, text="Satuan*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        cb_satuan = ttk.Combobox(
            form_frame, 
            values=["pcs", "pack", "box", "kg", "liter", "unit", "botol", "mangkuk"], 
            font=("Helvetica", 10)
        )
        cb_satuan.pack(fill="x", ipady=4, pady=(2, 10))
        cb_satuan.set("pcs")

        # Simpan Action
        def simpan():
            kode = entry_kode.get().strip()
            nama = entry_nama.get().strip()
            kat_nama = cb_kategori.get()
            harga_str = entry_harga.get().strip()
            stok_str = entry_stok.get().strip()
            satuan = cb_satuan.get().strip() or "pcs"

            if not kode or not nama:
                messagebox.showwarning("Peringatan", "Kode barang dan Nama barang wajib diisi!", parent=dialog)
                return

            if kat_nama not in self.kategori_map:
                messagebox.showwarning("Peringatan", "Pilih kategori yang valid!", parent=dialog)
                return

            try:
                harga = float(harga_str)
                stok = int(stok_str)
            except ValueError:
                messagebox.showwarning("Peringatan", "Harga harus berupa angka dan Stok harus berupa bilangan bulat!", parent=dialog)
                return

            kategori_id = self.kategori_map[kat_nama]

            try:
                db = koneksi_database()
                cursor = db.cursor()
                query = """
                    INSERT INTO products (kode_barang, nama_barang, kategori_id, harga, stok, satuan)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (kode, nama, kategori_id, harga, stok, satuan))
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", "Produk baru berhasil ditambahkan!", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error Database", f"Gagal menyimpan data produk:\n{e}", parent=dialog)

        # Buttons
        btn_frame = tk.Frame(dialog, bg="#FFFFFF")
        btn_frame.pack(fill="x", padx=30, pady=(10, 20))

        btn_simpan = tk.Button(
            btn_frame, text="Simpan Produk", font=("Helvetica", 9, "bold"),
            bg="#2563EB", fg="#FFFFFF", relief="flat", cursor="hand2", padx=15, pady=6, command=simpan
        )
        btn_simpan.pack(side="right", padx=(5, 0))

        btn_batal = tk.Button(
            btn_frame, text="Batal", font=("Helvetica", 9),
            bg="#E2E8F0", fg="#475569", relief="flat", cursor="hand2", padx=15, pady=6, command=dialog.destroy
        )
        btn_batal.pack(side="right")

    def show_edit_dialog(self):
        selected = self.get_selected_item()
        if not selected:
            return

        self.load_kategori_data()

        dialog = tk.Toplevel(self.parent_frame.winfo_toplevel())
        dialog.title(f"Edit Produk - {selected['kode_barang']}")
        dialog.geometry("450x480")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg="#FFFFFF")
        self.center_dialog(dialog, 450, 480)

        # Header
        lbl_header = tk.Label(
            dialog, 
            text=f"Edit Produk (ID: {selected['id']})", 
            font=("Helvetica", 14, "bold"), 
            bg="#FFFFFF", 
            fg="#1E293B"
        )
        lbl_header.pack(pady=(15, 15))

        form_frame = tk.Frame(dialog, bg="#FFFFFF")
        form_frame.pack(fill="both", expand=True, padx=30)

        # 1. Kode Barang
        tk.Label(form_frame, text="Kode Barang*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        entry_kode = tk.Entry(form_frame, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_kode.pack(fill="x", ipady=4, pady=(2, 10))
        entry_kode.insert(0, selected["kode_barang"])

        # 2. Nama Barang
        tk.Label(form_frame, text="Nama Barang*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        entry_nama = tk.Entry(form_frame, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_nama.pack(fill="x", ipady=4, pady=(2, 10))
        entry_nama.insert(0, selected["nama_barang"])
        entry_nama.focus()

        # 3. Kategori
        tk.Label(form_frame, text="Kategori*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        cb_kategori = ttk.Combobox(form_frame, state="readonly", values=self.kategori_list, font=("Helvetica", 10))
        cb_kategori.pack(fill="x", ipady=4, pady=(2, 10))
        
        # Set current category
        current_kat = selected.get("nama_kategori", "")
        if current_kat in self.kategori_list:
            cb_kategori.set(current_kat)
        elif self.kategori_list:
            cb_kategori.current(0)

        # 4. Harga & Stok (Side-by-Side)
        hs_frame = tk.Frame(form_frame, bg="#FFFFFF")
        hs_frame.pack(fill="x", pady=(0, 10))

        # Harga
        h_frame = tk.Frame(hs_frame, bg="#FFFFFF")
        h_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(h_frame, text="Harga (Rp)*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        entry_harga = tk.Entry(h_frame, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_harga.pack(fill="x", ipady=4, pady=(2, 0))
        entry_harga.insert(0, str(int(selected["harga"])))

        # Stok
        s_frame = tk.Frame(hs_frame, bg="#FFFFFF")
        s_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(s_frame, text="Stok*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        entry_stok = tk.Entry(s_frame, font=("Helvetica", 10), bg="#F9FAFB", relief="solid", bd=1)
        entry_stok.pack(fill="x", ipady=4, pady=(2, 0))
        entry_stok.insert(0, str(selected["stok"]))

        # 5. Satuan
        tk.Label(form_frame, text="Satuan*", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#374151").pack(anchor="w")
        cb_satuan = ttk.Combobox(
            form_frame, 
            values=["pcs", "pack", "box", "kg", "liter", "unit", "botol", "mangkuk"], 
            font=("Helvetica", 10)
        )
        cb_satuan.pack(fill="x", ipady=4, pady=(2, 10))
        cb_satuan.set(selected["satuan"] or "pcs")

        # Update Action
        def update():
            kode = entry_kode.get().strip()
            nama = entry_nama.get().strip()
            kat_nama = cb_kategori.get()
            harga_str = entry_harga.get().strip()
            stok_str = entry_stok.get().strip()
            satuan = cb_satuan.get().strip() or "pcs"

            if not kode or not nama:
                messagebox.showwarning("Peringatan", "Kode barang dan Nama barang wajib diisi!", parent=dialog)
                return

            if kat_nama not in self.kategori_map:
                messagebox.showwarning("Peringatan", "Pilih kategori yang valid!", parent=dialog)
                return

            try:
                harga = float(harga_str)
                stok = int(stok_str)
            except ValueError:
                messagebox.showwarning("Peringatan", "Harga harus berupa angka dan Stok harus berupa bilangan bulat!", parent=dialog)
                return

            kategori_id = self.kategori_map[kat_nama]

            try:
                db = koneksi_database()
                cursor = db.cursor()
                query = """
                    UPDATE products 
                    SET kode_barang = %s, nama_barang = %s, kategori_id = %s, harga = %s, stok = %s, satuan = %s
                    WHERE id = %s
                """
                cursor.execute(query, (kode, nama, kategori_id, harga, stok, satuan, selected["id"]))
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", "Data produk berhasil diperbarui!", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error Database", f"Gagal mengoperasikan data produk:\n{e}", parent=dialog)

        # Buttons
        btn_frame = tk.Frame(dialog, bg="#FFFFFF")
        btn_frame.pack(fill="x", padx=30, pady=(10, 20))

        btn_simpan = tk.Button(
            btn_frame, text="Update Produk", font=("Helvetica", 9, "bold"),
            bg="#F59E0B", fg="#FFFFFF", relief="flat", cursor="hand2", padx=15, pady=6, command=update
        )
        btn_simpan.pack(side="right", padx=(5, 0))

        btn_batal = tk.Button(
            btn_frame, text="Batal", font=("Helvetica", 9),
            bg="#E2E8F0", fg="#475569", relief="flat", cursor="hand2", padx=15, pady=6, command=dialog.destroy
        )
        btn_batal.pack(side="right")

    def hapus_produk(self):
        selected = self.get_selected_item()
        if not selected:
            return

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus produk '{selected['nama_barang']}' ({selected['kode_barang']})?"
        )
        if konfirmasi:
            try:
                db = koneksi_database()
                cursor = db.cursor()
                cursor.execute("DELETE FROM products WHERE id = %s", (selected["id"],))
                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo("Berhasil", "Data produk berhasil dihapus!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error Database", f"Gagal menghapus data produk:\n{e}")

    def center_dialog(self, dialog, width, height):
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Produk View")
    root.geometry("950x550")
    frame = tk.Frame(root, bg="#F8FAFC", padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    app = ProdukView(frame)
    root.mainloop()
