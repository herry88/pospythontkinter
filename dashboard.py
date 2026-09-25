import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.conn import koneksi_database


class DashboardApp:
    def __init__(self, root, user_data=None):
        self.root = root
        self.user_data = user_data or {"nama": "User", "role": "kasir", "username": "user"}

        self.root.title(f"Dashboard POS - {self.user_data['nama']}")
        self.root.geometry("1100x680")
        self.root.minsize(900, 600)
        self.root.configure(bg="#F3F4F6")

        self.center_window(1100, 680)

        # Build UI Components
        self.create_header()
        self.create_main_layout()
        self.load_dashboard_data()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_header(self):
        # Header Container
        header_frame = tk.Frame(self.root, bg="#1E293B", height=60)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)

        # Logo / Title App
        logo_label = tk.Label(
            header_frame,
            text="POS SYSTEM",
            font=("Helvetica", 14, "bold"),
            bg="#1E293B",
            fg="#FFFFFF"
        )
        logo_label.pack(side="left", padx=20)

        # User Info & Logout Button Frame
        right_frame = tk.Frame(header_frame, bg="#1E293B")
        right_frame.pack(side="right", padx=20)

        user_info = f"👤 {self.user_data['nama']} ({self.user_data['role'].upper()})"
        user_label = tk.Label(
            right_frame,
            text=user_info,
            font=("Helvetica", 10, "bold"),
            bg="#334155",
            fg="#F8FAFC",
            padx=12,
            pady=4
        )
        user_label.pack(side="left", padx=(0, 15))

        logout_btn = tk.Button(
            right_frame,
            text="Logout",
            font=("Helvetica", 9, "bold"),
            bg="#EF4444",
            fg="#FFFFFF",
            activebackground="#DC2626",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.logout
        )
        logout_btn.pack(side="right")

    def create_main_layout(self):
        # Body Container
        body_frame = tk.Frame(self.root, bg="#F3F4F6")
        body_frame.pack(side="top", fill="both", expand=True)

        # Sidebar Left
        sidebar = tk.Frame(body_frame, bg="#0F172A", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        sidebar_title = tk.Label(
            sidebar,
            text="NAVIGASI UTAMA",
            font=("Helvetica", 8, "bold"),
            bg="#0F172A",
            fg="#64748B"
        )
        sidebar_title.pack(anchor="w", padx=20, pady=(20, 10))

        # Menu items
        menu_items = [
            ("📊 Dashboard", self.show_dashboard_view),
            ("🛒 Transaksi (Kasir)", self.show_transaksi_view),
            ("📦 Data Produk", self.show_produk_view),
            ("🏷️ Kategori", self.show_kategori_view),
            ("📄 Laporan Penjualan", self.show_laporan_view),
        ]

        if self.user_data.get("role") == "admin":
            menu_items.append(("👥 Kelola User", self.show_user_view))

        for text, command in menu_items:
            btn = tk.Button(
                sidebar,
                text=text,
                font=("Helvetica", 10),
                bg="#0F172A",
                fg="#CBD5E1",
                activebackground="#1E293B",
                activeforeground="#FFFFFF",
                anchor="w",
                relief="flat",
                cursor="hand2",
                padx=20,
                pady=10,
                command=command
            )
            btn.pack(fill="x")

        # Main Content Area Right
        self.content_frame = tk.Frame(body_frame, bg="#F8FAFC", padx=30, pady=25)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def show_dashboard_view(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Welcome Card
        welcome_frame = tk.Frame(self.content_frame, bg="#3B82F6", padx=20, pady=20)
        welcome_frame.pack(fill="x", pady=(0, 25))

        welcome_title = tk.Label(
            welcome_frame,
            text=f"Selamat Datang Kembali, {self.user_data['nama']}!",
            font=("Helvetica", 16, "bold"),
            bg="#3B82F6",
            fg="#FFFFFF"
        )
        welcome_title.pack(anchor="w")

        welcome_sub = tk.Label(
            welcome_frame,
            text="Sistem siap digunakan untuk melakukan transaksi dan mengelola data toko Anda.",
            font=("Helvetica", 10),
            bg="#3B82F6",
            fg="#E0F2FE"
        )
        welcome_sub.pack(anchor="w", pady=(5, 0))

        # Cards Frame (Metrics)
        cards_container = tk.Frame(self.content_frame, bg="#F8FAFC")
        cards_container.pack(fill="x", pady=(0, 25))
        cards_container.columnconfigure((0, 1, 2, 3), weight=1)

        self.card_produk_val = self.create_card(cards_container, "Total Produk", "0", "#10B981", 0)
        self.card_kategori_val = self.create_card(cards_container, "Total Kategori", "0", "#F59E0B", 1)
        self.card_transaksi_val = self.create_card(cards_container, "Transaksi Hari Ini", "0", "#6366F1", 2)
        self.card_pendapatan_val = self.create_card(cards_container, "Pendapatan Hari Ini", "Rp 0", "#EC4899", 3)

        # Table Transaksi Terbaru Section
        recent_label = tk.Label(
            self.content_frame,
            text="Aktivitas Penjualan Terbaru",
            font=("Helvetica", 12, "bold"),
            bg="#F8FAFC",
            fg="#1E293B"
        )
        recent_label.pack(anchor="w", pady=(0, 10))

        # Treeview Table Placeholder
        table_frame = tk.Frame(self.content_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E2E8F0")
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "kode", "tanggal", "kasir", "total")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("kode", text="No. Transaksi")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("kasir", text="Kasir")
        self.tree.heading("total", text="Total Pembayaran")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("kode", width=150, anchor="center")
        self.tree.column("tanggal", width=180, anchor="center")
        self.tree.column("kasir", width=150, anchor="w")
        self.tree.column("total", width=150, anchor="e")

        self.tree.pack(fill="both", expand=True, padx=1, pady=1)

        self.load_dashboard_data()

    def create_card(self, parent, title, value, color, col_idx):
        card = tk.Frame(parent, bg="#FFFFFF", padx=15, pady=15, highlightthickness=1, highlightbackground="#E2E8F0")
        card.grid(row=0, column=col_idx, sticky="ew", padx=8)

        # Color indicator line on left
        indicator = tk.Frame(card, bg=color, width=4)
        indicator.pack(side="left", fill="y", padx=(0, 12))

        text_frame = tk.Frame(card, bg="#FFFFFF")
        text_frame.pack(side="left", fill="both")

        lbl_title = tk.Label(text_frame, text=title, font=("Helvetica", 9), bg="#FFFFFF", fg="#64748B")
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(text_frame, text=value, font=("Helvetica", 14, "bold"), bg="#FFFFFF", fg="#0F172A")
        lbl_val.pack(anchor="w", pady=(4, 0))

        return lbl_val

    def load_dashboard_data(self):
        try:
            db = koneksi_database()
            cursor = db.cursor()

            # Hitung produk
            cursor.execute("SELECT COUNT(*) FROM products")
            total_produk = cursor.fetchone()[0]

            # Hitung kategori
            cursor.execute("SELECT COUNT(*) FROM categories")
            total_kategori = cursor.fetchone()[0]

            # Hitung transaksi hari ini
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM transactions WHERE DATE(tanggal) = CURDATE()")
            trx_res = cursor.fetchone()
            total_trx = trx_res[0] if trx_res else 0
            total_pendapatan = trx_res[1] if trx_res else 0

            cursor.close()
            db.close()

            # Update nilai di card
            if hasattr(self, "card_produk_val"):
                self.card_produk_val.config(text=str(total_produk))
                self.card_kategori_val.config(text=str(total_kategori))
                self.card_transaksi_val.config(text=str(total_trx))
                self.card_pendapatan_val.config(text=f"Rp {total_pendapatan:,.0f}".replace(",", "."))

        except Exception as e:
            print("Error loading dashboard data:", e)

    def show_transaksi_view(self):
        messagebox.showinfo("Fitur", "Halaman Transaksi Kasir siap dikembangkan.")

    def show_produk_view(self):
        from produk import ProdukView
        ProdukView(self.content_frame)

    def show_kategori_view(self):
        from kategori import KategoriView
        KategoriView(self.content_frame)

    def show_laporan_view(self):
        messagebox.showinfo("Fitur", "Halaman Laporan Penjualan siap dikembangkan.")

    def show_user_view(self):
        messagebox.showinfo("Fitur", "Halaman Kelola User siap dikembangkan.")

    def logout(self):
        if messagebox.askyesno("Konfirmasi Logout", "Apakah Anda yakin ingin keluar dari aplikasi?"):
            self.root.destroy()
            login_root = tk.Tk()
            from login import LoginApp
            LoginApp(login_root)
            login_root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    sample_user = {"id": 1, "username": "admin", "nama": "Administrator", "role": "admin"}
    app = DashboardApp(root, sample_user)
    app.show_dashboard_view()
    root.mainloop()
