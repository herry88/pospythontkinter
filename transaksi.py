import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.conn import koneksi_database


class TransaksiView:
    def __init__(self, parent_frame, user_data=None):
        self.parent_frame = parent_frame
        self.user_data = user_data or {"id": 1, "nama": "Kasir", "username": "kasir", "role": "kasir"}

        # Clear existing widgets in parent_frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.cart = []  # List of dicts: {'product_id', 'kode_barang', 'nama_barang', 'harga', 'jumlah', 'subtotal', 'stok_max'}
        self.products_list = []  # All products from database
        self.filtered_products = []
        self.total_bayar = 0.0

        # Generate Nomor Transaksi
        self.nomor_transaksi = self.generate_nomor_transaksi()

        self.build_ui()
        self.load_products()

    def generate_nomor_transaksi(self):
        """Menghasilkan Nomor Transaksi otomatis unik TRX-YYYYMMDD-XXXX"""
        date_str = datetime.now().strftime("%Y%m%d")
        prefix = f"TRX-{date_str}-"
        
        try:
            db = koneksi_database()
            cursor = db.cursor()
            query = "SELECT nomor_transaksi FROM transactions WHERE nomor_transaksi LIKE %s ORDER BY id DESC LIMIT 1"
            cursor.execute(query, (f"{prefix}%",))
            row = cursor.fetchone()
            cursor.close()
            db.close()

            if row and row[0]:
                last_no = row[0]
                last_seq = int(last_no.split("-")[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1

            return f"{prefix}{new_seq:04d}"
        except Exception:
            # Fallback jika terjadi error koneksi saat penomoran
            return f"{prefix}{datetime.now().strftime('%H%M%S')}"

    def build_ui(self):
        # Header Section
        header_frame = tk.Frame(self.parent_frame, bg="#F8FAFC")
        header_frame.pack(fill="x", pady=(0, 15))

        title_label = tk.Label(
            header_frame,
            text="🛒 Kasir / Transaksi Penjualan",
            font=("Helvetica", 16, "bold"),
            bg="#F8FAFC",
            fg="#1E293B"
        )
        title_label.pack(side="left")

        subtitle_label = tk.Label(
            header_frame,
            text=f"No. Trx: {self.nomor_transaksi} | Kasir: {self.user_data.get('nama', 'User')}",
            font=("Helvetica", 10, "bold"),
            bg="#F8FAFC",
            fg="#2563EB"
        )
        subtitle_label.pack(side="right", padx=(10, 0), pady=(4, 0))

        # Main Layout: Left (Cart & Products) + Right (Payment Summary)
        main_container = tk.Frame(self.parent_frame, bg="#F8FAFC")
        main_container.pack(fill="both", expand=True)

        left_frame = tk.Frame(main_container, bg="#F8FAFC")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_frame = tk.Frame(main_container, bg="#FFFFFF", width=360, highlightthickness=1, highlightbackground="#CBD5E1")
        right_frame.pack(side="right", fill="both", expand=False)

        # ------------------ LEFT SIDE ------------------
        # 1. Product Search & Add Section
        search_card = tk.Frame(left_frame, bg="#FFFFFF", padx=12, pady=10, highlightthickness=1, highlightbackground="#E2E8F0")
        search_card.pack(fill="x", pady=(0, 10))

        search_lbl = tk.Label(search_card, text="Pilih / Cari Produk:", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#334155")
        search_lbl.grid(row=0, column=0, sticky="w", pady=(0, 4))

        # Search Entry & Combobox
        self.search_var = tk.StringVar()
        self.product_cb = ttk.Combobox(search_card, textvariable=self.search_var, font=("Helvetica", 9), state="normal")
        self.product_cb.grid(row=1, column=0, sticky="ew", padx=(0, 8), ipady=3)
        self.product_cb.bind("<KeyRelease>", self.on_search_keyrelease)
        self.product_cb.bind("<<ComboboxSelected>>", self.on_product_selected)

        qty_lbl = tk.Label(search_card, text="Qty:", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#334155")
        qty_lbl.grid(row=0, column=1, sticky="w", pady=(0, 4))

        self.qty_spin = tk.Spinbox(search_card, from_=1, to=999, font=("Helvetica", 9), width=5, justify="center")
        self.qty_spin.grid(row=1, column=1, sticky="w", padx=(0, 8), ipady=3)
        self.qty_spin.bind("<Return>", lambda e: self.tambah_ke_keranjang())

        btn_tambah = tk.Button(
            search_card,
            text="Tambah Item",
            font=("Helvetica", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.tambah_ke_keranjang
        )
        btn_tambah.grid(row=1, column=2, sticky="e")

        search_card.columnconfigure(0, weight=1)

        # Info Stok & Harga terpilih
        self.selected_info_lbl = tk.Label(search_card, text="Pilih produk untuk melihat detail harga & stok", font=("Helvetica", 8, "italic"), bg="#FFFFFF", fg="#64748B")
        self.selected_info_lbl.grid(row=2, column=0, columnspan=3, sticky="w", pady=(5, 0))

        # 2. Cart Table (Treeview)
        cart_card = tk.Frame(left_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0")
        cart_card.pack(fill="both", expand=True)

        cart_header = tk.Frame(cart_card, bg="#F1F5F9", padx=10, pady=6)
        cart_header.pack(fill="x")

        cart_title = tk.Label(cart_header, text="🛒 Keranjang Belanja", font=("Helvetica", 9, "bold"), bg="#F1F5F9", fg="#1E293B")
        cart_title.pack(side="left")

        btn_kosongkan = tk.Button(
            cart_header,
            text="🗑️ Kosongkan Cart",
            font=("Helvetica", 8, "bold"),
            bg="#EF4444",
            fg="#FFFFFF",
            activebackground="#DC2626",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.kosongkan_keranjang
        )
        btn_kosongkan.pack(side="right")

        # Treeview
        columns = ("no", "kode", "nama", "harga", "jumlah", "subtotal")
        self.cart_tree = ttk.Treeview(cart_card, columns=columns, show="headings", height=8)

        self.cart_tree.heading("no", text="No")
        self.cart_tree.heading("kode", text="Kode")
        self.cart_tree.heading("nama", text="Nama Produk")
        self.cart_tree.heading("harga", text="Harga (Rp)")
        self.cart_tree.heading("jumlah", text="Qty")
        self.cart_tree.heading("subtotal", text="Subtotal (Rp)")

        self.cart_tree.column("no", width=35, anchor="center")
        self.cart_tree.column("kode", width=80, anchor="center")
        self.cart_tree.column("nama", width=180, anchor="w")
        self.cart_tree.column("harga", width=95, anchor="e")
        self.cart_tree.column("jumlah", width=50, anchor="center")
        self.cart_tree.column("subtotal", width=105, anchor="e")

        scrollbar = ttk.Scrollbar(cart_card, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscroll=scrollbar.set)

        self.cart_tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scrollbar.pack(side="right", fill="y")

        # Cart Action Buttons (+ / - / Hapus Item)
        cart_action_frame = tk.Frame(left_frame, bg="#F8FAFC", pady=6)
        cart_action_frame.pack(fill="x")

        btn_plus = tk.Button(cart_action_frame, text="➕ Tambah Qty", font=("Helvetica", 8, "bold"), bg="#10B981", fg="#FFFFFF", relief="flat", cursor="hand2", padx=8, pady=3, command=self.tambah_qty)
        btn_plus.pack(side="left", padx=(0, 5))

        btn_minus = tk.Button(cart_action_frame, text="➖ Kurangi Qty", font=("Helvetica", 8, "bold"), bg="#F59E0B", fg="#FFFFFF", relief="flat", cursor="hand2", padx=8, pady=3, command=self.kurangi_qty)
        btn_minus.pack(side="left", padx=(0, 5))

        btn_hapus = tk.Button(cart_action_frame, text="❌ Hapus Item", font=("Helvetica", 8, "bold"), bg="#64748B", fg="#FFFFFF", relief="flat", cursor="hand2", padx=8, pady=3, command=self.hapus_item_keranjang)
        btn_hapus.pack(side="left")

        # ------------------ RIGHT SIDE (PAYMENT) ------------------
        pay_padding = tk.Frame(right_frame, bg="#FFFFFF", padx=14, pady=14)
        pay_padding.pack(fill="both", expand=True)

        pay_title = tk.Label(pay_padding, text="Ringkasan Pembayaran", font=("Helvetica", 11, "bold"), bg="#FFFFFF", fg="#0F172A")
        pay_title.pack(anchor="w", pady=(0, 10))

        # Total Big Display Box
        total_box = tk.Frame(pay_padding, bg="#1E293B", padx=12, pady=12)
        total_box.pack(fill="x", pady=(0, 12))

        total_lbl_title = tk.Label(total_box, text="TOTAL BAYAR", font=("Helvetica", 8, "bold"), bg="#1E293B", fg="#94A3B8")
        total_lbl_title.pack(anchor="w")

        self.total_display_lbl = tk.Label(total_box, text="Rp 0", font=("Helvetica", 18, "bold"), bg="#1E293B", fg="#38BDF8")
        self.total_display_lbl.pack(anchor="w", pady=(4, 0))

        # Input Nominal Bayar
        bayar_lbl = tk.Label(pay_padding, text="Nominal Bayar (Rp):", font=("Helvetica", 9, "bold"), bg="#FFFFFF", fg="#334155")
        bayar_lbl.pack(anchor="w", pady=(0, 4))

        self.bayar_entry = tk.Entry(
            pay_padding,
            font=("Helvetica", 12, "bold"),
            bg="#F9FAFB",
            relief="solid",
            bd=1,
            justify="right",
            highlightthickness=1,
            highlightcolor="#2563EB"
        )
        self.bayar_entry.pack(fill="x", ipady=5, pady=(0, 8))
        self.bayar_entry.bind("<KeyRelease>", self.hitung_kembalian)

        # Quick Nominal Buttons Grid
        quick_frame = tk.Frame(pay_padding, bg="#FFFFFF")
        quick_frame.pack(fill="x", pady=(0, 12))
        quick_frame.columnconfigure((0, 1, 2), weight=1)

        quick_nominals = [
            ("Uang Pas", "pas"), ("10.000", 10000), ("20.000", 20000),
            ("50.000", 50000), ("100.000", 100000), ("200.000", 200000)
        ]

        for idx, (label, val) in enumerate(quick_nominals):
            r, c = divmod(idx, 3)
            btn_q = tk.Button(
                quick_frame,
                text=label,
                font=("Helvetica", 8, "bold"),
                bg="#F1F5F9",
                fg="#334155",
                activebackground="#E2E8F0",
                relief="flat",
                cursor="hand2",
                pady=4,
                command=lambda v=val: self.set_quick_bayar(v)
            )
            btn_q.grid(row=r, column=c, sticky="ew", padx=2, pady=2)

        # Kembalian Box
        kembalian_box = tk.Frame(pay_padding, bg="#F8FAFC", padx=10, pady=10, highlightthickness=1, highlightbackground="#E2E8F0")
        kembalian_box.pack(fill="x", pady=(0, 15))

        kembalian_lbl_title = tk.Label(kembalian_box, text="Kembalian:", font=("Helvetica", 8, "bold"), bg="#F8FAFC", fg="#64748B")
        kembalian_lbl_title.pack(anchor="w")

        self.kembalian_lbl = tk.Label(kembalian_box, text="Rp 0", font=("Helvetica", 14, "bold"), bg="#F8FAFC", fg="#10B981")
        self.kembalian_lbl.pack(anchor="w", pady=(2, 0))

        # Primary Button: Simpan & Bayar
        self.btn_simpan = tk.Button(
            pay_padding,
            text="💾 SIMPAN & BAYAR",
            font=("Helvetica", 10, "bold"),
            bg="#10B981",
            fg="#FFFFFF",
            activebackground="#059669",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=8,
            command=self.proses_simpan_transaksi
        )
        self.btn_simpan.pack(fill="x")

    def load_products(self):
        """Memuat daftar produk dari database"""
        try:
            db = koneksi_database()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id, kode_barang, nama_barang, harga, stok, satuan FROM products ORDER BY nama_barang ASC")
            self.products_list = cursor.fetchall()
            cursor.close()
            db.close()

            self.update_product_combobox(self.products_list)
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal memuat data produk:\n{e}")

    def update_product_combobox(self, items):
        self.filtered_products = items
        display_values = [
            f"{p['kode_barang']} - {p['nama_barang']} (Rp {float(p['harga']):,.0f} | Stok: {p['stok']})"
            for p in items
        ]
        self.product_cb['values'] = display_values

    def on_search_keyrelease(self, event):
        """Filter list produk secara real-time saat mengetik"""
        if event.keysym in ("Up", "Down", "Return", "Escape"):
            return

        keyword = self.search_var.get().lower().strip()
        if not keyword:
            self.update_product_combobox(self.products_list)
            return

        filtered = [
            p for p in self.products_list
            if keyword in p['nama_barang'].lower() or keyword in p['kode_barang'].lower()
        ]
        self.update_product_combobox(filtered)

    def on_product_selected(self, event):
        idx = self.product_cb.current()
        if idx >= 0 and idx < len(self.filtered_products):
            p = self.filtered_products[idx]
            harga_formatted = f"Rp {float(p['harga']):,.0f}".replace(",", ".")
            self.selected_info_lbl.config(
                text=f"📌 {p['nama_barang']} | Harga: {harga_formatted} | Stok Tersedia: {p['stok']} {p['satuan']}",
                fg="#2563EB"
            )

    def get_selected_product_object(self):
        idx = self.product_cb.current()
        if idx >= 0 and idx < len(self.filtered_products):
            return self.filtered_products[idx]
        
        # Jika user mengetik kode/nama langsung dan menekan enter/tambah
        typed = self.search_var.get().strip().lower()
        if not typed:
            return None

        for p in self.products_list:
            if typed == p['kode_barang'].lower() or typed == p['nama_barang'].lower():
                return p
            if p['kode_barang'].lower() in typed:
                return p
        return None

    def tambah_ke_keranjang(self):
        product = self.get_selected_product_object()
        if not product:
            messagebox.showwarning("Peringatan", "Silakan pilih produk yang valid dari daftar!")
            return

        try:
            qty = int(self.qty_spin.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Peringatan", "Jumlah (Qty) harus berupa angka positif lebih dari 0!")
            return

        # Cek stok
        stok_tersedia = product['stok']
        
        # Cek apakah produk sudah ada di keranjang
        existing_item = next((item for item in self.cart if item['product_id'] == product['id']), None)
        current_qty_in_cart = existing_item['jumlah'] if existing_item else 0

        if (current_qty_in_cart + qty) > stok_tersedia:
            messagebox.showwarning(
                "Stok Tidak Cukup",
                f"Stok produk '{product['nama_barang']}' hanya tersisa {stok_tersedia}.\n"
                f"Jumlah di keranjang saat ini: {current_qty_in_cart}."
            )
            return

        harga = float(product['harga'])
        if existing_item:
            existing_item['jumlah'] += qty
            existing_item['subtotal'] = existing_item['jumlah'] * harga
        else:
            self.cart.append({
                'product_id': product['id'],
                'kode_barang': product['kode_barang'],
                'nama_barang': product['nama_barang'],
                'harga': harga,
                'jumlah': qty,
                'subtotal': qty * harga,
                'stok_max': stok_tersedia
            })

        # Reset selection input
        self.search_var.set("")
        self.update_product_combobox(self.products_list)
        self.qty_spin.delete(0, tk.END)
        self.qty_spin.insert(0, "1")
        self.selected_info_lbl.config(text="Pilih produk untuk melihat detail harga & stok", fg="#64748B")

        self.render_cart()

    def render_cart(self):
        """Merender isi cart ke Treeview dan memperbarui total bayar"""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        self.total_bayar = 0.0
        for idx, item in enumerate(self.cart, start=1):
            self.total_bayar += item['subtotal']
            self.cart_tree.insert(
                "",
                "end",
                iid=str(idx - 1),
                values=(
                    idx,
                    item['kode_barang'],
                    item['nama_barang'],
                    f"{item['harga']:,.0f}".replace(",", "."),
                    item['jumlah'],
                    f"{item['subtotal']:,.0f}".replace(",", ".")
                )
            )

        # Update Display Total
        self.total_display_lbl.config(text=f"Rp {self.total_bayar:,.0f}".replace(",", "."))
        self.hitung_kembalian()

    def tambah_qty(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih baris produk di keranjang terlebih dahulu!")
            return
        idx = int(selected[0])
        item = self.cart[idx]

        if item['jumlah'] + 1 > item['stok_max']:
            messagebox.showwarning("Stok Terbatas", f"Stok maksimum untuk {item['nama_barang']} adalah {item['stok_max']}.")
            return

        item['jumlah'] += 1
        item['subtotal'] = item['jumlah'] * item['harga']
        self.render_cart()
        self.cart_tree.selection_set(str(idx))

    def kurangi_qty(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih baris produk di keranjang terlebih dahulu!")
            return
        idx = int(selected[0])
        item = self.cart[idx]

        if item['jumlah'] > 1:
            item['jumlah'] -= 1
            item['subtotal'] = item['jumlah'] * item['harga']
        else:
            if messagebox.askyesno("Hapus Item", f"Hapus '{item['nama_barang']}' dari keranjang?"):
                self.cart.pop(idx)

        self.render_cart()

    def hapus_item_keranjang(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih baris produk di keranjang yang ingin dihapus!")
            return
        idx = int(selected[0])
        nama_barang = self.cart[idx]['nama_barang']
        
        if messagebox.askyesno("Konfirmasi Hapus", f"Hapus item '{nama_barang}' dari keranjang?"):
            self.cart.pop(idx)
            self.render_cart()

    def kosongkan_keranjang(self):
        if not self.cart:
            return
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin me-reset / mengosongkan keranjang belanja?"):
            self.cart.clear()
            self.render_cart()
            self.bayar_entry.delete(0, tk.END)
            self.hitung_kembalian()

    def set_quick_bayar(self, val):
        if val == "pas":
            bayar_val = self.total_bayar
        else:
            bayar_val = float(val)

        self.bayar_entry.delete(0, tk.END)
        self.bayar_entry.insert(0, f"{int(bayar_val)}")
        self.hitung_kembalian()

    def hitung_kembalian(self, event=None):
        bayar_str = self.bayar_entry.get().strip().replace(".", "").replace(",", "")
        try:
            bayar = float(bayar_str) if bayar_str else 0.0
        except ValueError:
            bayar = 0.0

        kembalian = bayar - self.total_bayar

        if self.total_bayar <= 0:
            self.kembalian_lbl.config(text="Rp 0", fg="#64748B")
        elif bayar < self.total_bayar:
            kurang = abs(kembalian)
            self.kembalian_lbl.config(
                text=f"- Rp {kurang:,.0f} (Kurang)".replace(",", "."),
                fg="#EF4444"
            )
        else:
            self.kembalian_lbl.config(
                text=f"Rp {kembalian:,.0f}".replace(",", "."),
                fg="#10B981"
            )

    def proses_simpan_transaksi(self):
        # 1. Validasi Cart
        if not self.cart:
            messagebox.showwarning("Peringatan", "Keranjang belanja masih kosong!")
            return

        # 2. Validasi Pembayaran
        bayar_str = self.bayar_entry.get().strip().replace(".", "").replace(",", "")
        try:
            bayar = float(bayar_str)
        except ValueError:
            messagebox.showwarning("Peringatan", "Masukkan nominal pembayaran yang valid!")
            self.bayar_entry.focus()
            return

        if bayar < self.total_bayar:
            messagebox.showwarning(
                "Pembayaran Kurang",
                f"Nominal pembayaran (Rp {bayar:,.0f}) kurang dari total tagihan (Rp {self.total_bayar:,.0f}).".replace(",", ".")
            )
            self.bayar_entry.focus()
            return

        kembalian = bayar - self.total_bayar
        user_id = self.user_data.get("id", 1)

        # 3. Simpan Ke Database (Transactions & Transaction_Details & Update Products Stock)
        try:
            db = koneksi_database()
            cursor = db.cursor()

            # Matikan autocommit untuk transaksi atomik
            db.autocommit = False

            # Insert ke tabel transactions
            query_trx = """
                INSERT INTO transactions (nomor_transaksi, tanggal, user_id, total, bayar, kembalian)
                VALUES (%s, NOW(), %s, %s, %s, %s)
            """
            cursor.execute(query_trx, (self.nomor_transaksi, user_id, self.total_bayar, bayar, kembalian))
            transaction_id = cursor.lastrowid

            # Insert ke tabel transaction_details & Update stok produk
            query_detail = """
                INSERT INTO transaction_details (transaction_id, product_id, harga, jumlah, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """
            query_update_stok = """
                UPDATE products SET stok = stok - %s WHERE id = %s AND stok >= %s
            """

            for item in self.cart:
                # Detail
                cursor.execute(query_detail, (
                    transaction_id,
                    item['product_id'],
                    item['harga'],
                    item['jumlah'],
                    item['subtotal']
                ))

                # Update Stok
                cursor.execute(query_update_stok, (
                    item['jumlah'],
                    item['product_id'],
                    item['jumlah']
                ))

                if cursor.rowcount == 0:
                    raise Exception(f"Stok untuk produk '{item['nama_barang']}' tidak mencukupi di database.")

            # Commit Transaksi DB
            db.commit()
            cursor.close()
            db.close()

            # Tampilkan Nota / Struk Penjualan
            self.tampilkan_struk_modal(self.nomor_transaksi, bayar, kembalian)

            # Reset Halaman Transaksi untuk transaksi berikutnya
            self.reset_form_transaksi()

        except Exception as e:
            if 'db' in locals() and db.is_connected():
                db.rollback()
                db.close()
            messagebox.showerror("Gagal Menyimpan Transaksi", f"Terjadi kesalahan saat memproses transaksi:\n{e}")

    def reset_form_transaksi(self):
        self.cart.clear()
        self.render_cart()
        self.bayar_entry.delete(0, tk.END)
        self.hitung_kembalian()
        self.nomor_transaksi = self.generate_nomor_transaksi()
        self.load_products()  # Refresh stok produk terbaru

    def tampilkan_struk_modal(self, no_trx, bayar, kembalian):
        """Menampilkan popup dialog struk belanja"""
        modal = tk.Toplevel(self.parent_frame)
        modal.title(f"Struk Transaksi - {no_trx}")
        modal.geometry("400x580")
        modal.resizable(False, False)
        modal.transient(self.parent_frame.winfo_toplevel())
        modal.grab_set()

        # Center modal
        screen_w = modal.winfo_screenwidth()
        screen_h = modal.winfo_screenheight()
        x = (screen_w // 2) - 200
        y = (screen_h // 2) - 290
        modal.geometry(f"400x580+{x}+{y}")

        modal.configure(bg="#F8FAFC")

        # Struk Content Card
        card = tk.Frame(modal, bg="#FFFFFF", padx=20, pady=20, highlightthickness=1, highlightbackground="#E2E8F0")
        card.pack(fill="both", expand=True, padx=15, pady=15)

        # Header Struk
        store_lbl = tk.Label(card, text="TOKO KASIR POS", font=("Courier", 14, "bold"), bg="#FFFFFF", fg="#0F172A")
        store_lbl.pack()

        sub_lbl = tk.Label(card, text="Jl. Raya Utama No. 123, Jakarta\nTelp: (021) 555-0199", font=("Courier", 8), bg="#FFFFFF", fg="#64748B")
        sub_lbl.pack(pady=(2, 10))

        line1 = tk.Label(card, text="="*38, font=("Courier", 9), bg="#FFFFFF", fg="#CBD5E1")
        line1.pack()

        meta_text = (
            f"No. Trx : {no_trx}\n"
            f"Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Kasir   : {self.user_data.get('nama', 'Kasir')}"
        )
        meta_lbl = tk.Label(card, text=meta_text, font=("Courier", 9), justify="left", anchor="w", bg="#FFFFFF", fg="#334155")
        meta_lbl.pack(fill="x", pady=5)

        line2 = tk.Label(card, text="-"*38, font=("Courier", 9), bg="#FFFFFF", fg="#CBD5E1")
        line2.pack()

        # Text Frame for Items
        items_frame = tk.Frame(card, bg="#FFFFFF")
        items_frame.pack(fill="both", expand=True, pady=5)

        # Items listing
        items_text_widget = tk.Text(items_frame, font=("Courier", 9), bg="#FFFFFF", fg="#0F172A", bd=0, relief="flat")
        items_text_widget.pack(fill="both", expand=True)

        total_hitung = 0
        for item in self.cart:
            nama = item['nama_barang']
            if len(nama) > 20:
                nama = nama[:18] + ".."
            sub = item['subtotal']
            total_hitung += sub

            line_item = f"{nama:<20}\n  {item['jumlah']} x {item['harga']:>8,.0f} = {sub:>10,.0f}\n".replace(",", ".")
            items_text_widget.insert(tk.END, line_item)

        items_text_widget.config(state="disabled")

        line3 = tk.Label(card, text="-"*38, font=("Courier", 9), bg="#FFFFFF", fg="#CBD5E1")
        line3.pack()

        # Summary Struk
        summary_text = (
            f"TOTAL     : Rp {total_hitung:>14,.0f}\n".replace(",", ".") +
            f"BAYAR     : Rp {bayar:>14,.0f}\n".replace(",", ".") +
            f"KEMBALI   : Rp {kembalian:>14,.0f}\n".replace(",", ".")
        )
        summary_lbl = tk.Label(card, text=summary_text, font=("Courier", 9, "bold"), justify="left", anchor="w", bg="#FFFFFF", fg="#0F172A")
        summary_lbl.pack(fill="x", pady=5)

        line4 = tk.Label(card, text="="*38, font=("Courier", 9), bg="#FFFFFF", fg="#CBD5E1")
        line4.pack()

        footer_lbl = tk.Label(card, text="--- TERIMA KASIH --- \n Selamat Belanja Kembali!", font=("Courier", 8, "italic"), bg="#FFFFFF", fg="#64748B")
        footer_lbl.pack(pady=(5, 0))

        # Close Modal Button
        btn_close = tk.Button(
            modal,
            text="✅ Selesai / Transaksi Baru",
            font=("Helvetica", 10, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2",
            pady=8,
            command=modal.destroy
        )
        btn_close.pack(fill="x", padx=15, pady=(0, 15))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x680")
    sample_user = {"id": 1, "username": "admin", "nama": "Administrator", "role": "admin"}
    app = TransaksiView(root, sample_user)
    root.mainloop()
