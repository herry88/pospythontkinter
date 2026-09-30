import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.conn import koneksi_database


class LaporanView:
    def __init__(self, parent_frame, user_data=None):
        self.parent_frame = parent_frame
        self.user_data = user_data or {"id": 1, "nama": "User", "username": "user", "role": "admin"}

        # Bersihkan widget yang ada sebelumnya di parent_frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.users_map = {}  # {"Nama (Role)": user_id}
        self.build_ui()
        self.load_users_data()
        self.set_preset_bulan_ini()  # Default filter ke bulan ini
        self.load_laporan_data()

    def build_ui(self):
        # 1. Header Section
        header_frame = tk.Frame(self.parent_frame, bg="#F8FAFC")
        header_frame.pack(fill="x", pady=(0, 15))

        title_label = tk.Label(
            header_frame,
            text="📄 Laporan Penjualan & Transaksi",
            font=("Helvetica", 16, "bold"),
            bg="#F8FAFC",
            fg="#1E293B"
        )
        title_label.pack(side="left")

        subtitle_label = tk.Label(
            header_frame,
            text="Ringkasan dan filter transaksi berdasarkan periode dan kasir/user",
            font=("Helvetica", 9),
            bg="#F8FAFC",
            fg="#64748B"
        )
        subtitle_label.pack(side="left", padx=(12, 0), pady=(4, 0))

        # 2. Filter Bar Container Card
        filter_card = tk.Frame(
            self.parent_frame,
            bg="#FFFFFF",
            padx=15,
            pady=12,
            highlightthickness=1,
            highlightbackground="#E2E8F0"
        )
        filter_card.pack(fill="x", pady=(0, 15))

        # Baris 1: Filter Periode & Preset
        lbl_periode = tk.Label(
            filter_card,
            text="Periode Tanggal:",
            font=("Helvetica", 9, "bold"),
            bg="#FFFFFF",
            fg="#334155"
        )
        lbl_periode.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)

        self.entry_tgl_mulai = tk.Entry(
            filter_card,
            font=("Helvetica", 9),
            width=11,
            bg="#F8FAFC",
            relief="solid",
            bd=1
        )
        self.entry_tgl_mulai.grid(row=0, column=1, padx=(0, 5), pady=5, ipady=3)

        lbl_sd = tk.Label(filter_card, text="s/d", font=("Helvetica", 9), bg="#FFFFFF", fg="#64748B")
        lbl_sd.grid(row=0, column=2, padx=(0, 5), pady=5)

        self.entry_tgl_selesai = tk.Entry(
            filter_card,
            font=("Helvetica", 9),
            width=11,
            bg="#F8FAFC",
            relief="solid",
            bd=1
        )
        self.entry_tgl_selesai.grid(row=0, column=3, padx=(0, 10), pady=5, ipady=3)

        # Quick Presets Buttons
        preset_frame = tk.Frame(filter_card, bg="#FFFFFF")
        preset_frame.grid(row=0, column=4, columnspan=3, sticky="w", pady=5)

        btn_hari_ini = tk.Button(
            preset_frame,
            text="Hari Ini",
            font=("Helvetica", 8, "bold"),
            bg="#E0F2FE",
            fg="#0369A1",
            activebackground="#BAE6FD",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.set_preset_hari_ini
        )
        btn_hari_ini.pack(side="left", padx=(0, 4))

        btn_bulan_ini = tk.Button(
            preset_frame,
            text="Bulan Ini",
            font=("Helvetica", 8, "bold"),
            bg="#E0F2FE",
            fg="#0369A1",
            activebackground="#BAE6FD",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.set_preset_bulan_ini
        )
        btn_bulan_ini.pack(side="left", padx=(0, 4))

        btn_semua_tgl = tk.Button(
            preset_frame,
            text="Semua Tgl",
            font=("Helvetica", 8, "bold"),
            bg="#F1F5F9",
            fg="#475569",
            activebackground="#E2E8F0",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.set_preset_semua
        )
        btn_semua_tgl.pack(side="left")

        # Baris 2: Filter User/Kasir & Pencarian TRX
        lbl_user = tk.Label(
            filter_card,
            text="Kasir / User:",
            font=("Helvetica", 9, "bold"),
            bg="#FFFFFF",
            fg="#334155"
        )
        lbl_user.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=5)

        self.cb_user = ttk.Combobox(filter_card, font=("Helvetica", 9), state="readonly", width=18)
        self.cb_user.grid(row=1, column=1, columnspan=2, sticky="w", padx=(0, 10), pady=5)

        lbl_search = tk.Label(
            filter_card,
            text="Cari No. TRX:",
            font=("Helvetica", 9, "bold"),
            bg="#FFFFFF",
            fg="#334155"
        )
        lbl_search.grid(row=1, column=3, sticky="w", padx=(0, 5), pady=5)

        self.entry_search = tk.Entry(
            filter_card,
            font=("Helvetica", 9),
            width=18,
            bg="#F8FAFC",
            relief="solid",
            bd=1
        )
        self.entry_search.grid(row=1, column=4, sticky="w", padx=(0, 15), pady=5, ipady=3)
        self.entry_search.bind("<Return>", lambda e: self.load_laporan_data())

        # Tombol Filter & Reset
        btn_filter = tk.Button(
            filter_card,
            text="🔍 Tampilkan",
            font=("Helvetica", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=3,
            command=self.load_laporan_data
        )
        btn_filter.grid(row=1, column=5, padx=(0, 5), pady=5)

        btn_reset = tk.Button(
            filter_card,
            text="🔄 Reset",
            font=("Helvetica", 9),
            bg="#64748B",
            fg="#FFFFFF",
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.reset_filter
        )
        btn_reset.grid(row=1, column=6, pady=5)

        # 3. Metrics Cards (Ringkasan Statistik)
        cards_container = tk.Frame(self.parent_frame, bg="#F8FAFC")
        cards_container.pack(fill="x", pady=(0, 15))
        cards_container.columnconfigure((0, 1, 2, 3), weight=1)

        self.card_trx_val = self.create_metric_card(cards_container, "Total Transaksi", "0", "#3B82F6", 0)
        self.card_omset_val = self.create_metric_card(cards_container, "Total Omset", "Rp 0", "#10B981", 1)
        self.card_avg_val = self.create_metric_card(cards_container, "Rata-Rata / TRX", "Rp 0", "#8B5CF6", 2)
        self.card_items_val = self.create_metric_card(cards_container, "Barang Terjual", "0 Pcs", "#F59E0B", 3)

        # 4. Table Frame & Treeview
        table_container = tk.Frame(self.parent_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0")
        table_container.pack(fill="both", expand=True, pady=(0, 10))

        columns = ("id", "nomor_transaksi", "tanggal", "kasir", "total_item", "total", "bayar", "kembalian")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=10)

        self.tree.heading("id", text="ID")
        self.tree.heading("nomor_transaksi", text="No. Transaksi")
        self.tree.heading("tanggal", text="Tanggal & Waktu")
        self.tree.heading("kasir", text="Kasir / User")
        self.tree.heading("total_item", text="Qty Barang")
        self.tree.heading("total", text="Total Pembayaran")
        self.tree.heading("bayar", text="Bayar")
        self.tree.heading("kembalian", text="Kembalian")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nomor_transaksi", width=160, anchor="center")
        self.tree.column("tanggal", width=160, anchor="center")
        self.tree.column("kasir", width=150, anchor="w")
        self.tree.column("total_item", width=90, anchor="center")
        self.tree.column("total", width=140, anchor="e")
        self.tree.column("bayar", width=130, anchor="e")
        self.tree.column("kembalian", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda event: self.open_detail_dialog())

        # 5. Footer Actions (Detail & Cetak Summary)
        footer_frame = tk.Frame(self.parent_frame, bg="#F8FAFC")
        footer_frame.pack(fill="x")

        btn_detail = tk.Button(
            footer_frame,
            text="👁️ Lihat Detail Transaksi",
            font=("Helvetica", 9, "bold"),
            bg="#0284C7",
            fg="#FFFFFF",
            activebackground="#0369A1",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.open_detail_dialog
        )
        btn_detail.pack(side="left")

        btn_print = tk.Button(
            footer_frame,
            text="🖨️ Cetak Ringkasan Laporan",
            font=("Helvetica", 9, "bold"),
            bg="#059669",
            fg="#FFFFFF",
            activebackground="#047857",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.cetak_ringkasan
        )
        btn_print.pack(side="right")

    def create_metric_card(self, parent, title, value, color, col_idx):
        card = tk.Frame(
            parent,
            bg="#FFFFFF",
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground="#E2E8F0"
        )
        card.grid(row=0, column=col_idx, sticky="ew", padx=5)

        indicator = tk.Frame(card, bg=color, width=4)
        indicator.pack(side="left", fill="y", padx=(0, 10))

        content = tk.Frame(card, bg="#FFFFFF")
        content.pack(side="left", fill="both")

        lbl_title = tk.Label(content, text=title, font=("Helvetica", 8, "bold"), bg="#FFFFFF", fg="#64748B")
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(content, text=value, font=("Helvetica", 13, "bold"), bg="#FFFFFF", fg="#0F172A")
        lbl_val.pack(anchor="w", pady=(3, 0))

        return lbl_val

    def load_users_data(self):
        """Memuat daftar kasir/user untuk dropdown filter"""
        try:
            db = koneksi_database()
            cursor = db.cursor()
            cursor.execute("SELECT id, nama, role FROM users ORDER BY nama ASC")
            rows = cursor.fetchall()
            cursor.close()
            db.close()

            self.users_map = {"Semua Kasir / User": None}
            options = ["Semua Kasir / User"]

            for u_id, nama, role in rows:
                display_text = f"{nama} ({role.capitalize()})"
                self.users_map[display_text] = u_id
                options.append(display_text)

            self.cb_user["values"] = options
            self.cb_user.current(0)

        except Exception as e:
            print("Error load users:", e)
            self.cb_user["values"] = ["Semua Kasir / User"]
            self.cb_user.current(0)

    def set_preset_hari_ini(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.entry_tgl_mulai.delete(0, tk.END)
        self.entry_tgl_mulai.insert(0, today)
        self.entry_tgl_selesai.delete(0, tk.END)
        self.entry_tgl_selesai.insert(0, today)

    def set_preset_bulan_ini(self):
        now = datetime.now()
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
        today = now.strftime("%Y-%m-%d")
        self.entry_tgl_mulai.delete(0, tk.END)
        self.entry_tgl_mulai.insert(0, start_date)
        self.entry_tgl_selesai.delete(0, tk.END)
        self.entry_tgl_selesai.insert(0, today)

    def set_preset_semua(self):
        self.entry_tgl_mulai.delete(0, tk.END)
        self.entry_tgl_selesai.delete(0, tk.END)

    def reset_filter(self):
        self.set_preset_bulan_ini()
        self.cb_user.current(0)
        self.entry_search.delete(0, tk.END)
        self.load_laporan_data()

    def load_laporan_data(self):
        tgl_mulai = self.entry_tgl_mulai.get().strip()
        tgl_selesai = self.entry_tgl_selesai.get().strip()
        user_selected = self.cb_user.get()
        user_id = self.users_map.get(user_selected)
        search = self.entry_search.get().strip()

        # Validasi format tanggal jika diisi
        if tgl_mulai:
            try:
                datetime.strptime(tgl_mulai, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Format Tanggal Salah", "Format Tanggal Mulai harus YYYY-MM-DD (Contoh: 2026-09-01)")
                return

        if tgl_selesai:
            try:
                datetime.strptime(tgl_selesai, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Format Tanggal Salah", "Format Tanggal Selesai harus YYYY-MM-DD (Contoh: 2026-09-30)")
                return

        try:
            db = koneksi_database()
            cursor = db.cursor()

            query = """
                SELECT 
                    t.id, 
                    t.nomor_transaksi, 
                    t.tanggal as tgl,
                    u.nama as kasir,
                    COALESCE(SUM(td.jumlah), 0) as total_items,
                    t.total, 
                    t.bayar, 
                    t.kembalian
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                LEFT JOIN transaction_details td ON t.id = td.transaction_id
                WHERE 1=1
            """
            params = []

            if tgl_mulai:
                query += " AND DATE(t.tanggal) >= %s"
                params.append(tgl_mulai)

            if tgl_selesai:
                query += " AND DATE(t.tanggal) <= %s"
                params.append(tgl_selesai)

            if user_id is not None:
                query += " AND t.user_id = %s"
                params.append(user_id)

            if search:
                query += " AND (t.nomor_transaksi LIKE %s OR u.nama LIKE %s)"
                params.append(f"%{search}%")
                params.append(f"%{search}%")

            query += " GROUP BY t.id ORDER BY t.id DESC"

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            cursor.close()
            db.close()

            # Clear Treeview
            for r in self.tree.get_children():
                self.tree.delete(r)

            # Recalculate Metrics
            total_trx = len(rows)
            total_omset = 0.0
            total_items_sold = 0

            for row in rows:
                trx_id, no_trx, tgl, kasir, qty_items, total, bayar, kembalian = row
                tgl_str = tgl.strftime("%Y-%m-%d %H:%M:%S") if hasattr(tgl, 'strftime') else str(tgl or '')
                total_float = float(total or 0)
                bayar_float = float(bayar or 0)
                kembalian_float = float(kembalian or 0)
                qty_int = int(qty_items or 0)

                total_omset += total_float
                total_items_sold += qty_int

                self.tree.insert("", "end", values=(
                    trx_id,
                    no_trx,
                    tgl_str,
                    kasir,
                    f"{qty_int} Pcs",
                    f"Rp {total_float:,.0f}".replace(",", "."),
                    f"Rp {bayar_float:,.0f}".replace(",", "."),
                    f"Rp {kembalian_float:,.0f}".replace(",", ".")
                ))

            avg_per_trx = total_omset / total_trx if total_trx > 0 else 0.0

            # Update Metrics Cards
            self.card_trx_val.config(text=f"{total_trx} Trx")
            self.card_omset_val.config(text=f"Rp {total_omset:,.0f}".replace(",", "."))
            self.card_avg_val.config(text=f"Rp {avg_per_trx:,.0f}".replace(",", "."))
            self.card_items_val.config(text=f"{total_items_sold} Pcs")

        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal memuat data laporan:\n{e}")

    def open_detail_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Pilih Transaksi", "Silakan pilih salah satu transaksi dari tabel untuk melihat detail.")
            return

        values = self.tree.item(selected_item[0], "values")
        trx_id = values[0]
        no_trx = values[1]
        tgl_trx = values[2]
        kasir_name = values[3]
        total_str = values[5]
        bayar_str = values[6]
        kembalian_str = values[7]

        # Fetch detail items from database
        try:
            db = koneksi_database()
            cursor = db.cursor()
            query = """
                SELECT p.kode_barang, p.nama_barang, td.harga, td.jumlah, td.subtotal
                FROM transaction_details td
                JOIN products p ON td.product_id = p.id
                WHERE td.transaction_id = %s
            """
            cursor.execute(query, (trx_id,))
            details = cursor.fetchall()
            cursor.close()
            db.close()

            # Buat Modal Window Toplevel
            dialog = tk.Toplevel(self.parent_frame)
            dialog.title(f"Detail Transaksi - {no_trx}")
            dialog.geometry("680x480")
            dialog.resizable(False, False)
            dialog.configure(bg="#F8FAFC")
            dialog.transient(self.parent_frame.winfo_toplevel())
            dialog.grab_set()

            # Posisikan dialog di tengah
            screen_w = dialog.winfo_screenwidth()
            screen_h = dialog.winfo_screenheight()
            x = (screen_w // 2) - 340
            y = (screen_h // 2) - 240
            dialog.geometry(f"680x480+{x}+{y}")

            # Header Dialog
            header = tk.Frame(dialog, bg="#1E293B", padx=20, pady=15)
            header.pack(fill="x")

            lbl_dialog_title = tk.Label(
                header,
                text=f"Detail Transaksi: {no_trx}",
                font=("Helvetica", 13, "bold"),
                bg="#1E293B",
                fg="#FFFFFF"
            )
            lbl_dialog_title.pack(anchor="w")

            lbl_dialog_sub = tk.Label(
                header,
                text=f"Tanggal: {tgl_trx}  |  Kasir: {kasir_name}",
                font=("Helvetica", 9),
                bg="#1E293B",
                fg="#94A3B8"
            )
            lbl_dialog_sub.pack(anchor="w", pady=(2, 0))

            # Table Detail Items
            table_frame = tk.Frame(dialog, bg="#FFFFFF", padx=15, pady=15)
            table_frame.pack(fill="both", expand=True)

            cols = ("kode", "nama", "harga", "jumlah", "subtotal")
            tree_detail = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)

            tree_detail.heading("kode", text="Kode")
            tree_detail.heading("nama", text="Nama Produk")
            tree_detail.heading("harga", text="Harga Satuan")
            tree_detail.heading("jumlah", text="Qty")
            tree_detail.heading("subtotal", text="Subtotal")

            tree_detail.column("kode", width=100, anchor="center")
            tree_detail.column("nama", width=220, anchor="w")
            tree_detail.column("harga", width=110, anchor="e")
            tree_detail.column("jumlah", width=60, anchor="center")
            tree_detail.column("subtotal", width=120, anchor="e")

            scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree_detail.yview)
            tree_detail.configure(yscrollcommand=scroll.set)

            tree_detail.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")

            for item in details:
                k_kode, k_nama, k_harga, k_qty, k_subtotal = item
                tree_detail.insert("", "end", values=(
                    k_kode,
                    k_nama,
                    f"Rp {float(k_harga):,.0f}".replace(",", "."),
                    k_qty,
                    f"Rp {float(k_subtotal):,.0f}".replace(",", ".")
                ))

            # Payment Summary Card at Bottom
            summary_card = tk.Frame(dialog, bg="#F1F5F9", padx=20, pady=10)
            summary_card.pack(fill="x", side="bottom")

            lbl_sum_text = f"Total: {total_str}   |   Bayar: {bayar_str}   |   Kembali: {kembalian_str}"
            lbl_sum = tk.Label(summary_card, text=lbl_sum_text, font=("Helvetica", 10, "bold"), bg="#F1F5F9", fg="#0F172A")
            lbl_sum.pack(side="left")

            btn_close = tk.Button(
                summary_card,
                text="Tutup",
                font=("Helvetica", 9, "bold"),
                bg="#EF4444",
                fg="#FFFFFF",
                activebackground="#DC2626",
                relief="flat",
                cursor="hand2",
                padx=15,
                pady=4,
                command=dialog.destroy
            )
            btn_close.pack(side="right")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat detail transaksi:\n{e}")

    def cetak_ringkasan(self):
        """Menampilkan popup ringkasan laporan yang siap dicetak/disimpan"""
        tgl_m = self.entry_tgl_mulai.get().strip() or "Awal"
        tgl_s = self.entry_tgl_selesai.get().strip() or "Hari Ini"
        kasir_text = self.cb_user.get()

        val_trx = self.card_trx_val.cget("text")
        val_omset = self.card_omset_val.cget("text")
        val_avg = self.card_avg_val.cget("text")
        val_items = self.card_items_val.cget("text")

        summary_text = (
            "==========================================\n"
            "        RINGKASAN LAPORAN PENJUALAN       \n"
            "==========================================\n"
            f"Periode Tanggal : {tgl_m} s/d {tgl_s}\n"
            f"Filter User     : {kasir_text}\n"
            "------------------------------------------\n"
            f"Total Transaksi : {val_trx}\n"
            f"Total Omset     : {val_omset}\n"
            f"Rata-rata/Trx   : {val_avg}\n"
            f"Barang Terjual  : {val_items}\n"
            "==========================================\n"
            "Laporan berhasil dicetak & dibuat otomatis."
        )

        messagebox.showinfo("Ringkasan Laporan Penjualan", summary_text)
