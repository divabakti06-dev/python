import os
import math
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import mysql.connector

# --- KONFIGURASI DATABASE ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'siakad'
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


# ==========================================
# 0. TEMA (PALET UNGU) + KOMPONEN TAMPILAN
# ==========================================
PURPLE       = "#6B5499"   # ungu utama
PURPLE_DARK  = "#4B3677"   # ungu tua (teks)
PURPLE_MID   = "#8E79BE"   # ungu sedang
PURPLE_SOFT  = "#B9A9D6"   # ungu lembut
LAVENDER     = "#EFEAF7"   # latar lavender muda
OUTER        = "#CFC4E3"   # latar luar jendela dashboard
SIDEBAR_BG   = "#E4DDF1"   # latar sidebar
FIELD_BG     = "#E4DDF1"   # latar kolom isian bentuk pil (login)
WHITE        = "#FFFFFF"
TEXT         = "#3F3552"   # warna teks biasa
ROSE         = "#C2547A"   # tombol hapus / logout
GREY_PURPLE  = "#A79DB8"   # tombol clear

FONT_FAMILY = "Segoe UI"   # otomatis diganti Poppins kalau terpasang


def terapkan_tema(root):
    """Menerapkan font, warna default widget, dan style ttk. Dipanggil sekali per jendela utama."""
    global FONT_FAMILY

    # Pilih font: Poppins -> Segoe UI -> Helvetica
    tersedia = set(tkfont.families(root))
    for f in ("Poppins", "Segoe UI", "Helvetica"):
        if f in tersedia:
            FONT_FAMILY = f
            break
    for nama in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        try:
            tkfont.nametofont(nama).configure(family=FONT_FAMILY, size=10)
        except tk.TclError:
            pass

    # Warna default widget tk biasa (Frame, Label, Entry, LabelFrame)
    root.option_add("*Frame.background", WHITE)
    root.option_add("*Label.background", WHITE)
    root.option_add("*Label.foreground", TEXT)
    root.option_add("*Labelframe.background", WHITE)
    root.option_add("*Labelframe.foreground", PURPLE)
    root.option_add("*Entry.background", WHITE)
    root.option_add("*Entry.foreground", TEXT)
    root.option_add("*Entry.relief", "flat")
    root.option_add("*Entry.borderWidth", 3)
    root.option_add("*Entry.highlightThickness", 1)
    root.option_add("*Entry.highlightBackground", "#CFC6E0")
    root.option_add("*Entry.highlightColor", PURPLE)
    root.option_add("*Entry.insertBackground", TEXT)
    root.option_add("*Entry.selectBackground", PURPLE_SOFT)

    # Daftar dropdown Combobox
    root.option_add("*TCombobox*Listbox.background", WHITE)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", PURPLE)
    root.option_add("*TCombobox*Listbox.selectForeground", WHITE)

    # Style ttk
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=WHITE)

    # Notebook dengan tab disembunyikan (perpindahan halaman lewat menu sidebar)
    style.layout("Hidden.TNotebook.Tab", [])
    style.configure("Hidden.TNotebook", background=WHITE, borderwidth=0,
                    bordercolor=WHITE, lightcolor=WHITE, darkcolor=WHITE,
                    tabmargins=[0, 0, 0, 0])

    style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                    foreground=TEXT, rowheight=26, borderwidth=0)
    style.map("Treeview",
              background=[("selected", PURPLE_MID)],
              foreground=[("selected", WHITE)])
    style.configure("Treeview.Heading", background=PURPLE, foreground=WHITE,
                    relief="flat", padding=6, font=(FONT_FAMILY, 10, "bold"))
    style.map("Treeview.Heading", background=[("active", PURPLE_MID)])

    style.configure("TCombobox", fieldbackground=WHITE, background="#E4DDF1",
                    foreground=TEXT, arrowcolor=PURPLE, bordercolor="#CFC6E0",
                    lightcolor=WHITE, darkcolor=WHITE, padding=4)
    style.map("TCombobox",
              fieldbackground=[("readonly", WHITE)],
              foreground=[("readonly", TEXT)],
              selectbackground=[("readonly", WHITE)],
              selectforeground=[("readonly", TEXT)])

    # Combobox bentuk pil untuk form login
    style.configure("Pill.TCombobox", fieldbackground=FIELD_BG, background=FIELD_BG,
                    foreground=PURPLE_DARK, arrowcolor=PURPLE, bordercolor=FIELD_BG,
                    lightcolor=FIELD_BG, darkcolor=FIELD_BG, padding=2)
    style.map("Pill.TCombobox",
              fieldbackground=[("readonly", FIELD_BG)],
              foreground=[("readonly", PURPLE_DARK)],
              selectbackground=[("readonly", FIELD_BG)],
              selectforeground=[("readonly", PURPLE_DARK)])

    for arah in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        style.configure(arah, background=PURPLE_SOFT, troughcolor=LAVENDER,
                        bordercolor=LAVENDER, arrowcolor=PURPLE, relief="flat")
        style.map(arah, background=[("active", PURPLE_MID)])


def _campur_warna(c1, c2, t):
    """Campur dua warna hex (gradasi)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    """Persegi dengan sudut membulat."""
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
           x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class TombolPill(tk.Canvas):
    """Tombol berbentuk pil dengan gradasi."""
    def __init__(self, parent, text, command, width=220, height=42,
                 c1="#A592CC", c2="#F1ECF8", fg=PURPLE_DARK, bg=PURPLE, ukuran=11):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.command = command
        r = height / 2
        for x in range(width):
            if x < r:
                dy = math.sqrt(max(r * r - (r - x) ** 2, 0))
            elif x > width - r:
                dy = math.sqrt(max(r * r - (x - (width - r)) ** 2, 0))
            else:
                dy = r
            warna = _campur_warna(c1, c2, x / (width - 1))
            self.create_line(x, r - dy, x, r + dy + 1, fill=warna)
        self.create_text(width / 2, height / 2, text=text, fill=fg,
                         font=(FONT_FAMILY, ukuran, "bold"))
        self.bind("<ButtonRelease-1>", lambda e: self.command())


class FieldPill(tk.Canvas):
    """Kolom isian berbentuk pil (Entry atau Combobox) seperti di foto login."""
    def __init__(self, parent, jenis="entry", values=None, show=None,
                 width=290, height=38, bg=WHITE, fill=FIELD_BG):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, bd=0)
        rounded_rect(self, 1, 1, width - 1, height - 1, height / 2, fill=fill, outline=fill)
        if jenis == "combo":
            self.widget = ttk.Combobox(self, values=values, state="readonly",
                                       font=(FONT_FAMILY, 11), style="Pill.TCombobox")
        else:
            self.widget = tk.Entry(self, bg=fill, fg=PURPLE_DARK, insertbackground=PURPLE_DARK,
                                   relief="flat", bd=0, highlightthickness=0,
                                   font=(FONT_FAMILY, 11), show=show)
        self.entry = self.widget
        self.create_window(18, height / 2, window=self.widget, anchor="w", width=width - 36)


class KartuBulat(tk.Canvas):
    """Wadah dengan sudut membulat. Isi widget ditaruh di atribut .isi"""
    def __init__(self, parent, fill=WHITE, outer=LAVENDER, radius=24, inset=10):
        super().__init__(parent, bg=outer, highlightthickness=0, bd=0)
        self.fill = fill
        self.radius = radius
        self.inset = inset
        self.isi = tk.Frame(self, bg=fill)
        self._win = self.create_window(inset, inset, window=self.isi, anchor="nw")
        self.bind("<Configure>", self._gambar)

    def _gambar(self, event):
        self.delete("bentuk")
        rounded_rect(self, 1, 1, event.width - 1, event.height - 1, self.radius,
                     fill=self.fill, outline=self.fill, tags="bentuk")
        self.tag_lower("bentuk")
        self.itemconfigure(self._win,
                           width=max(event.width - 2 * self.inset, 1),
                           height=max(event.height - 2 * self.inset, 1))


class NavItem(tk.Canvas):
    """Menu sidebar berbentuk pil. Item aktif berlatar putih."""
    def __init__(self, parent, text, command, width=190, height=42,
                 bg=SIDEBAR_BG, fg=PURPLE_DARK, titik=PURPLE_SOFT):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.teks = text
        self.w, self.h = width, height
        self.fg = fg
        self.titik = titik
        self.aktif = False
        self.bind("<Button-1>", lambda e: command())
        self.bind("<Enter>", lambda e: self._gambar(hover=True))
        self.bind("<Leave>", lambda e: self._gambar())
        self._gambar()

    def _gambar(self, hover=False):
        self.delete("all")
        if self.aktif:
            rounded_rect(self, 1, 1, self.w - 1, self.h - 1, self.h / 2, fill=WHITE, outline=WHITE)
        elif hover:
            rounded_rect(self, 1, 1, self.w - 1, self.h - 1, self.h / 2, fill="#D9D0EA", outline="#D9D0EA")
        warna_titik = PURPLE if self.aktif else self.titik
        self.create_oval(18, self.h / 2 - 5, 28, self.h / 2 + 5, fill=warna_titik, outline="")
        self.create_text(42, self.h / 2, text=self.teks, anchor="w",
                         fill=PURPLE if self.aktif else self.fg,
                         font=(FONT_FAMILY, 10, "bold" if self.aktif else "normal"))

    def set_aktif(self, nilai):
        self.aktif = nilai
        self._gambar()


def gambar_kupu_kupu(c, ox=0, oy=0, skala=1.0, warna=None):
    """Logo kupu-kupu sederhana. Bisa digeser (ox, oy), diskalakan, dan diganti warnanya."""
    w1, w2, w3, w4, badan = warna or ("#8E6FC0", "#B19BDA", PURPLE, "#9A83C9", PURPLE_DARK)
    t = "kupu"
    c.create_polygon(66, 52, 50, 18, 20, 6, 6, 28, 22, 52, 48, 62, smooth=True, fill=w1, outline="", tags=t)
    c.create_polygon(74, 52, 90, 18, 120, 6, 134, 28, 118, 52, 92, 62, smooth=True, fill=w2, outline="", tags=t)
    c.create_polygon(66, 58, 44, 66, 26, 86, 40, 104, 58, 92, 66, 72, smooth=True, fill=w3, outline="", tags=t)
    c.create_polygon(74, 58, 96, 66, 114, 86, 100, 104, 82, 92, 74, 72, smooth=True, fill=w4, outline="", tags=t)
    c.create_line(70, 40, 70, 92, width=4, fill=badan, capstyle="round", tags=t)
    c.create_line(70, 42, 60, 24, width=1, fill=badan, tags=t)
    c.create_line(70, 42, 80, 24, width=1, fill=badan, tags=t)
    if skala != 1.0:
        c.scale(t, 0, 0, skala, skala)
    c.move(t, ox, oy)


def buat_tombol_crud(parent, tambah, edit, hapus, clear):
    """Baris tombol Tambah / Edit / Hapus / Clear (dipakai semua tab)."""
    frame_btn = tk.Frame(parent)
    frame_btn.pack(fill="x", padx=15, pady=5)
    for teks, warna, cmd in (("Tambah", PURPLE, tambah),
                             ("Edit", PURPLE_MID, edit),
                             ("Hapus", ROSE, hapus),
                             ("Clear", GREY_PURPLE, clear)):
        tk.Button(frame_btn, text=teks, bg=warna, fg=WHITE,
                  activebackground=warna, activeforeground=WHITE,
                  relief="flat", bd=0, cursor="hand2", pady=4,
                  font=(FONT_FAMILY, 9, "bold"), width=12,
                  command=cmd).pack(side="left", padx=5)
    return frame_btn


# ==========================================
# 1. JENDELA LOGIN (LANDSCAPE: KIRI UNGU, KANAN PUTIH)
# ==========================================
class LoginWindow:
    LEBAR, TINGGI = 860, 520

    def __init__(self, root):
        self.root = root
        self.result = None   # menyimpan (user, role) kalau login berhasil
        terapkan_tema(self.root)
        self.root.title("Login - SIAKAD")
        self.root.geometry(f"{self.LEBAR}x{self.TINGGI}")
        self.root.resizable(False, False)
        self.root.configure(bg=WHITE)

        W, H = self.LEBAR, self.TINGGI
        latar = tk.Canvas(self.root, width=W, height=H, bg=WHITE, highlightthickness=0)
        latar.pack()
        self.gambar_latar(latar, W, H)

        # --- Form di sisi kanan (putih) ---
        form = tk.Frame(latar, bg=WHITE)
        latar.create_window(705, 70, window=form, anchor="n")

        tk.Label(
            form,
            text="SIAKAD LOGIN",
            font=(FONT_FAMILY, 18, "bold"),
            bg=WHITE,
            fg=PURPLE
        ).pack(pady=(0, 18))

        label_font = (FONT_FAMILY, 9, "bold")

        tk.Label(form, text="Login Sebagai:", font=label_font, bg=WHITE, fg=PURPLE_DARK, anchor="w").pack(fill="x", padx=6)
        pill_role = FieldPill(form, jenis="combo", values=["Dosen", "Mahasiswa"])
        self.combo_role = pill_role.widget
        self.combo_role.set("Dosen")
        pill_role.pack(pady=(2, 12))

        tk.Label(form, text="Username:", font=label_font, bg=WHITE, fg=PURPLE_DARK, anchor="w").pack(fill="x", padx=6)
        pill_user = FieldPill(form)
        self.entry_user = pill_user.entry
        pill_user.pack(pady=(2, 12))
        self.entry_user.focus()

        tk.Label(form, text="Password:", font=label_font, bg=WHITE, fg=PURPLE_DARK, anchor="w").pack(fill="x", padx=6)
        pill_pass = FieldPill(form, show="*")
        self.entry_pass = pill_pass.entry
        pill_pass.pack(pady=(2, 10))

        lbl_info = tk.Label(
            form,
            text="*Gunakan NIP/NIM sebagai Username & Email sebagai Password",
            font=(FONT_FAMILY, 8, "italic"),
            bg=WHITE,
            fg="#8A7FA0",
            wraplength=290,
            justify="center"
        )
        lbl_info.pack(pady=(0, 14))

        TombolPill(form, "LOGIN", self.proses_login, width=290, height=40,
                   c1=PURPLE, c2=PURPLE_MID, fg=WHITE, bg=WHITE).pack()

        self.root.bind('<Return>', lambda event: self.proses_login())

    def gambar_latar(self, c, W, H):
        """Sisi kiri ungu + awan putih pembatas + logo, seperti foto referensi."""
        # Latar ungu kiri
        c.create_rectangle(0, 0, 600, H, fill=PURPLE, outline="")

        # Hiasan lingkaran dan bintang
        c.create_oval(28, 28, 92, 92, fill="#7A62A6", outline="")
        c.create_oval(60, 400, 140, 480, fill="#7A62A6", outline="")
        c.create_oval(370, 60, 404, 94, fill="#8E79BE", outline="")
        for (x, y) in ((150, 40), (300, 30), (400, 200), (40, 250), (330, 420), (200, 480), (420, 330)):
            c.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#E4DDF1", outline="")

        # Awan pembatas (lingkaran putih dengan lingkar lavender di belakangnya)
        awan = [(520, 30, 60), (540, 140, 55), (505, 250, 62),
                (540, 360, 55), (515, 460, 60), (545, 520, 45)]
        for (x, y, r) in awan:
            c.create_oval(x - r - 12, y - r - 12, x + r + 12, y + r + 12, fill="#8A74B5", outline="")
        for (x, y, r) in awan:
            c.create_oval(x - r, y - r, x + r, y + r, fill=WHITE, outline="")
        c.create_rectangle(545, 0, W, H, fill=WHITE, outline="")

        # Judul dan logo di sisi kiri
        c.create_text(55, 120, text="SIAKAD", anchor="w", fill=WHITE,
                      font=(FONT_FAMILY, 34, "bold"))
        c.create_text(57, 168, text="Sistem Informasi Akademik", anchor="w", fill="#E4DDF1",
                      font=(FONT_FAMILY, 13))
        gambar_kupu_kupu(c, ox=110, oy=225, skala=1.6,
                         warna=("#E4DDF1", "#CFC4E3", "#B9A9D6", "#F1ECF8", WHITE))

    def proses_login(self):
        role = self.combo_role.get()
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Peringatan", "Username dan Password wajib diisi!")
            return

        conn = None
        cursor = None

        try:
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)

            if role == "Dosen":
                query = "SELECT nip AS id, nama_dosen AS nama, email FROM dosen WHERE nip = %s AND email = %s"
            else:
                query = "SELECT nim AS id, nama_lengkap AS nama, email FROM mahasiswa WHERE nim = %s AND email = %s"

            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                messagebox.showinfo("Berhasil", f"Login Berhasil sebagai {role}!\nSelamat datang, {user['nama']}.")
                self.buka_dashboard(user, role)
            else:
                messagebox.showerror("Gagal", f"Login {role} Gagal!\nUsername atau Password salah.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Koneksi database bermasalah:\n{err}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def buka_dashboard(self, user, role):
        # Simpan data login, lalu tutup form login.
        # Dashboard dibuka oleh fungsi main() di bagian paling bawah.
        self.result = (user, role)
        self.root.destroy()


# ==========================================
# 2. TABULAR DASHBOARD (6 TABEL SIAKAD + HALAMAN DASHBOARD)
# ==========================================

# --- TAB DASHBOARD (BARU) ---
class TabDashboard(ttk.Frame):
    # (judul kartu, nama tabel, warna angka)
    KARTU = [
        ("Total Dosen",          "dosen",          PURPLE),
        ("Total Mahasiswa",      "mahasiswa",      PURPLE_MID),
        ("Total Mata Kuliah",    "mata_kuliah",    PURPLE),
        ("Total Jadwal Kuliah",  "jadwal_kuliah",  PURPLE_MID),
        ("Total KRS",            "krs",            PURPLE),
        ("Total Pembayaran UKT", "pembayaran_ukt", PURPLE_MID),
    ]

    def __init__(self, parent, user, role):
        super().__init__(parent)
        self.user = user
        self.role = role
        self.lbl_angka = {}
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        tk.Label(self, text=f"Selamat datang, {self.user['nama']}!",
                 font=(FONT_FAMILY, 18, "bold"), fg=PURPLE
                 ).pack(anchor="w", padx=20, pady=(20, 2))
        tk.Label(self, text=f"Anda login sebagai {self.role}. Berikut ringkasan data SIAKAD.",
                 font=(FONT_FAMILY, 10), fg=PURPLE_MID
                 ).pack(anchor="w", padx=20, pady=(0, 15))

        grid = tk.Frame(self)
        grid.pack(fill="x", padx=12)
        for c in range(3):
            grid.grid_columnconfigure(c, weight=1, uniform="kartu")

        for i, (judul, tabel, warna) in enumerate(self.KARTU):
            kartu = KartuBulat(grid, fill=LAVENDER, outer=WHITE, radius=20, inset=14)
            kartu.configure(width=220, height=120)
            kartu.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")

            lbl = tk.Label(kartu.isi, text="0", font=(FONT_FAMILY, 28, "bold"),
                           bg=LAVENDER, fg=warna)
            lbl.pack(anchor="w")
            tk.Label(kartu.isi, text=judul, font=(FONT_FAMILY, 10),
                     bg=LAVENDER, fg=PURPLE_DARK).pack(anchor="w")
            self.lbl_angka[tabel] = lbl

    def refresh(self):
        """Ambil ulang jumlah data dari database."""
        try:
            db = connect_db()
            cursor = db.cursor()
            for _, tabel, _ in self.KARTU:
                cursor.execute(f"SELECT COUNT(*) FROM {tabel}")
                self.lbl_angka[tabel].config(text=str(cursor.fetchone()[0]))
            cursor.close()
            db.close()
        except Exception:
            for lbl in self.lbl_angka.values():
                lbl.config(text="-")


# --- TAB DATA DOSEN ---
class TabDosen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        frame_form = tk.LabelFrame(self, text=" Form Data Dosen ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=10)

        labels = ["NIP", "Nama Dosen", "Jenis Kelamin", "Email", "No Telepon", "Pendidikan Terakhir", "Bidang Keahlian"]
        for i, label_text in enumerate(labels):
            tk.Label(frame_form, text=label_text).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=3)

        self.entry_nip = tk.Entry(frame_form)
        self.entry_nip.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

        self.entry_nama = tk.Entry(frame_form)
        self.entry_nama.grid(row=0, column=3, padx=5, pady=3, sticky="ew")

        self.combo_jk = ttk.Combobox(frame_form, values=["Laki-laki", "Perempuan"], state="readonly")
        self.combo_jk.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

        self.entry_email = tk.Entry(frame_form)
        self.entry_email.grid(row=1, column=3, padx=5, pady=3, sticky="ew")

        self.entry_tlp = tk.Entry(frame_form)
        self.entry_tlp.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

        self.entry_pendidikan = tk.Entry(frame_form)
        self.entry_pendidikan.grid(row=2, column=3, padx=5, pady=3, sticky="ew")

        self.entry_bidang = tk.Entry(frame_form)
        self.entry_bidang.grid(row=3, column=1, padx=5, pady=3, sticky="ew")

        frame_form.grid_columnconfigure(1, weight=1)
        frame_form.grid_columnconfigure(3, weight=1)

        buat_tombol_crud(self, self.tambah_data, self.edit_data, self.hapus_data, self.clear_fields)

        frame_table = tk.Frame(self)
        frame_table.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("nip", "nama_dosen", "jenis_kelamin", "email", "no_telepon", "pendidikan_terakhir", "bidang_keahlian")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")

        headers = ["NIP", "Nama Dosen", "Jenis Kelamin", "Email", "No Telepon", "Pendidikan", "Bidang Keahlian"]
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=120)

        self.tree.bind("<<TreeviewSelect>>", self.select_item)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM dosen")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data dosen: {e}")

    def tambah_data(self):
        nip = self.entry_nip.get()
        nama = self.entry_nama.get()
        if not nip or not nama:
            messagebox.showwarning("Warning", "NIP dan Nama wajib diisi!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = "INSERT INTO dosen VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (nip, nama, self.combo_jk.get(), self.entry_email.get(), self.entry_tlp.get(), self.entry_pendidikan.get(), self.entry_bidang.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambah data: {e}")

    def edit_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Pilih data di tabel yang ingin diubah!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = """UPDATE dosen SET nama_dosen=%s, jenis_kelamin=%s, email=%s, 
                     no_telepon=%s, pendidikan_terakhir=%s, bidang_keahlian=%s WHERE nip=%s"""
            val = (self.entry_nama.get(), self.combo_jk.get(), self.entry_email.get(), 
                   self.entry_tlp.get(), self.entry_pendidikan.get(), self.entry_bidang.get(), self.entry_nip.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

    def hapus_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        nip = self.entry_nip.get()
        if messagebox.askyesno("Konfirmasi", f"Yakin hapus dosen NIP {nip}?"):
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM dosen WHERE nip = %s", (nip,))
                db.commit()
                db.close()
                messagebox.showinfo("Sukses", "Data berhasil dihapus!")
                self.clear_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data: {e}")

    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clear_fields()
            self.entry_nip.insert(0, values[0])
            self.entry_nama.insert(0, values[1])
            self.combo_jk.set(values[2])
            self.entry_email.insert(0, values[3])
            self.entry_tlp.insert(0, values[4])
            self.entry_pendidikan.insert(0, values[5])
            self.entry_bidang.insert(0, values[6])

    def clear_fields(self):
        self.entry_nip.delete(0, tk.END)
        self.entry_nama.delete(0, tk.END)
        self.combo_jk.set("")
        self.entry_email.delete(0, tk.END)
        self.entry_tlp.delete(0, tk.END)
        self.entry_pendidikan.delete(0, tk.END)
        self.entry_bidang.delete(0, tk.END)


# --- TAB DATA MAHASISWA ---
class TabMahasiswa(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        frame_form = tk.LabelFrame(self, text=" Form Data Mahasiswa ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_form, text="NIM").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.entry_nim = tk.Entry(frame_form)
        self.entry_nim.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Nama Lengkap").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self.entry_nama = tk.Entry(frame_form)
        self.entry_nama.grid(row=0, column=3, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Jenis Kelamin").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.combo_jk = ttk.Combobox(frame_form, values=["Laki-laki", "Perempuan"], state="readonly")
        self.combo_jk.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Tgl Lahir (YYYY-MM-DD)").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        self.entry_tgl = tk.Entry(frame_form)
        self.entry_tgl.grid(row=1, column=3, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Tempat Lahir").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.entry_tmpt = tk.Entry(frame_form)
        self.entry_tmpt.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Alamat").grid(row=2, column=2, sticky="w", padx=5, pady=3)
        self.entry_alamat = tk.Entry(frame_form)
        self.entry_alamat.grid(row=2, column=3, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="No Telepon").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        self.entry_tlp = tk.Entry(frame_form)
        self.entry_tlp.grid(row=3, column=1, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Email").grid(row=3, column=2, sticky="w", padx=5, pady=3)
        self.entry_email = tk.Entry(frame_form)
        self.entry_email.grid(row=3, column=3, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Jurusan").grid(row=4, column=0, sticky="w", padx=5, pady=3)
        self.entry_jurusan = tk.Entry(frame_form)
        self.entry_jurusan.grid(row=4, column=1, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Angkatan").grid(row=4, column=2, sticky="w", padx=5, pady=3)
        self.entry_angkatan = tk.Entry(frame_form)
        self.entry_angkatan.grid(row=4, column=3, padx=5, pady=3, sticky="ew")

        tk.Label(frame_form, text="Status").grid(row=5, column=0, sticky="w", padx=5, pady=3)
        self.combo_status = ttk.Combobox(frame_form, values=["Aktif", "Cuti", "Lulus", "Non-Aktif"], state="readonly")
        self.combo_status.grid(row=5, column=1, padx=5, pady=3, sticky="ew")

        frame_form.grid_columnconfigure(1, weight=1)
        frame_form.grid_columnconfigure(3, weight=1)

        buat_tombol_crud(self, self.tambah_data, self.edit_data, self.hapus_data, self.clear_fields)

        frame_table = tk.Frame(self)
        frame_table.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("nim", "nama_lengkap", "jenis_kelamin", "tanggal_lahir", "tempat_lahir", "alamat", "no_telepon", "email", "jurusan", "angkatan", "status")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")

        headers = ["NIM", "Nama Lengkap", "JK", "Tgl Lahir", "Tempat Lahir", "Alamat", "No Tlp", "Email", "Jurusan", "Angkatan", "Status"]
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=100)

        self.tree.bind("<<TreeviewSelect>>", self.select_item)

        scrollbar_v = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(frame_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM mahasiswa")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data mahasiswa: {e}")

    def tambah_data(self):
        nim = self.entry_nim.get()
        nama = self.entry_nama.get()
        if not nim or not nama:
            messagebox.showwarning("Warning", "NIM dan Nama Wajib diisi!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = "INSERT INTO mahasiswa VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (nim, nama, self.combo_jk.get(), self.entry_tgl.get(), self.entry_tmpt.get(),
                   self.entry_alamat.get(), self.entry_tlp.get(), self.entry_email.get(),
                   self.entry_jurusan.get(), self.entry_angkatan.get(), self.combo_status.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data Mahasiswa berhasil ditambahkan!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambah data: {e}")

    def edit_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel yang ingin diubah!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = """UPDATE mahasiswa SET nama_lengkap=%s, jenis_kelamin=%s, tanggal_lahir=%s, 
                     tempat_lahir=%s, alamat=%s, no_telepon=%s, email=%s, jurusan=%s, 
                     angkatan=%s, status=%s WHERE nim=%s"""
            val = (self.entry_nama.get(), self.combo_jk.get(), self.entry_tgl.get(),
                   self.entry_tmpt.get(), self.entry_alamat.get(), self.entry_tlp.get(),
                   self.entry_email.get(), self.entry_jurusan.get(), self.entry_angkatan.get(),
                   self.combo_status.get(), self.entry_nim.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data mahasiswa berhasil diperbarui!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

    def hapus_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        nim = self.entry_nim.get()
        if messagebox.askyesno("Konfirmasi", f"Yakin hapus mahasiswa NIM {nim}?"):
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM mahasiswa WHERE nim = %s", (nim,))
                db.commit()
                db.close()
                messagebox.showinfo("Sukses", "Data berhasil dihapus!")
                self.clear_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data: {e}")

    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clear_fields()
            self.entry_nim.insert(0, values[0])
            self.entry_nama.insert(0, values[1])
            self.combo_jk.set(values[2])
            self.entry_tgl.insert(0, values[3])
            self.entry_tmpt.insert(0, values[4])
            self.entry_alamat.insert(0, values[5])
            self.entry_tlp.insert(0, values[6])
            self.entry_email.insert(0, values[7])
            self.entry_jurusan.insert(0, values[8])
            self.entry_angkatan.insert(0, values[9])
            self.combo_status.set(values[10])

    def clear_fields(self):
        self.entry_nim.delete(0, tk.END)
        self.entry_nama.delete(0, tk.END)
        self.combo_jk.set("")
        self.entry_tgl.delete(0, tk.END)
        self.entry_tmpt.delete(0, tk.END)
        self.entry_alamat.delete(0, tk.END)
        self.entry_tlp.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_jurusan.delete(0, tk.END)
        self.entry_angkatan.delete(0, tk.END)
        self.combo_status.set("")


# --- TAB MATA KULIAH ---
class TabMataKuliah(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        frame_form = tk.LabelFrame(self, text=" Form Mata Kuliah ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=10)

        labels = ["Kode MK", "Nama MK", "SKS", "Semester", "NIP Dosen Pengampu"]
        for i, label_text in enumerate(labels):
            tk.Label(frame_form, text=label_text).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=3)

        self.entry_kode = tk.Entry(frame_form)
        self.entry_kode.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

        self.entry_nama = tk.Entry(frame_form)
        self.entry_nama.grid(row=0, column=3, padx=5, pady=3, sticky="ew")

        self.entry_sks = tk.Entry(frame_form)
        self.entry_sks.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

        self.entry_smt = tk.Entry(frame_form)
        self.entry_smt.grid(row=1, column=3, padx=5, pady=3, sticky="ew")

        self.entry_nip = tk.Entry(frame_form)
        self.entry_nip.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

        frame_form.grid_columnconfigure(1, weight=1)
        frame_form.grid_columnconfigure(3, weight=1)

        buat_tombol_crud(self, self.tambah_data, self.edit_data, self.hapus_data, self.clear_fields)

        frame_table = tk.Frame(self)
        frame_table.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("kode_mk", "nama_mk", "sks", "semester", "nip_dosen")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")

        headers = ["Kode MK", "Nama Mata Kuliah", "SKS", "Semester", "NIP Dosen"]
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=130)

        self.tree.bind("<<TreeviewSelect>>", self.select_item)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM mata_kuliah")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data mata kuliah: {e}")

    def tambah_data(self):
        kode = self.entry_kode.get()
        if not kode:
            messagebox.showwarning("Warning", "Kode MK wajib diisi!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = "INSERT INTO mata_kuliah VALUES (%s, %s, %s, %s, %s)"
            val = (kode, self.entry_nama.get(), self.entry_sks.get(), self.entry_smt.get(), self.entry_nip.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Mata Kuliah berhasil ditambahkan!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambah data: {e}")

    def edit_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = "UPDATE mata_kuliah SET nama_mk=%s, sks=%s, semester=%s, nip_dosen=%s WHERE kode_mk=%s"
            val = (self.entry_nama.get(), self.entry_sks.get(), self.entry_smt.get(), self.entry_nip.get(), self.entry_kode.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data Mata Kuliah diperbarui!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

    def hapus_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        kode = self.entry_kode.get()
        if messagebox.askyesno("Konfirmasi", f"Yakin hapus MK {kode}?"):
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM mata_kuliah WHERE kode_mk = %s", (kode,))
                db.commit()
                db.close()
                messagebox.showinfo("Sukses", "Data berhasil dihapus!")
                self.clear_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data: {e}")

    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clear_fields()
            self.entry_kode.insert(0, values[0])
            self.entry_nama.insert(0, values[1])
            self.entry_sks.insert(0, values[2])
            self.entry_smt.insert(0, values[3])
            self.entry_nip.insert(0, values[4])

    def clear_fields(self):
        self.entry_kode.delete(0, tk.END)
        self.entry_nama.delete(0, tk.END)
        self.entry_sks.delete(0, tk.END)
        self.entry_smt.delete(0, tk.END)
        self.entry_nip.delete(0, tk.END)


# --- TAB JADWAL KULIAH ---
class TabJadwal(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        frame_form = tk.LabelFrame(self, text=" Form Jadwal Kuliah ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=10)

        labels = ["ID Jadwal", "Kode MK", "Hari", "Jam Mulai", "Jam Selesai", "Ruangan"]
        for i, label_text in enumerate(labels):
            tk.Label(frame_form, text=label_text).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=3)

        self.entry_id = tk.Entry(frame_form)
        self.entry_id.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

        self.entry_kodemk = tk.Entry(frame_form)
        self.entry_kodemk.grid(row=0, column=3, padx=5, pady=3, sticky="ew")

        self.combo_hari = ttk.Combobox(frame_form, values=["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"], state="readonly")
        self.combo_hari.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

        self.entry_jammulai = tk.Entry(frame_form)
        self.entry_jammulai.grid(row=1, column=3, padx=5, pady=3, sticky="ew")

        self.entry_jamselesai = tk.Entry(frame_form)
        self.entry_jamselesai.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

        self.entry_ruangan = tk.Entry(frame_form)
        self.entry_ruangan.grid(row=2, column=3, padx=5, pady=3, sticky="ew")

        frame_form.grid_columnconfigure(1, weight=1)
        frame_form.grid_columnconfigure(3, weight=1)

        buat_tombol_crud(self, self.tambah_data, self.edit_data, self.hapus_data, self.clear_fields)

        frame_table = tk.Frame(self)
        frame_table.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id_jadwal", "kode_mk", "hari", "jam_mulai", "jam_selesai", "ruangan")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")

        headers = ["ID Jadwal", "Kode MK", "Hari", "Jam Mulai", "Jam Selesai", "Ruangan"]
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=120)

        self.tree.bind("<<TreeviewSelect>>", self.select_item)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM jadwal_kuliah")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data jadwal: {e}")

    def tambah_data(self):
        id_j = self.entry_id.get()
        if not id_j:
            messagebox.showwarning("Warning", "ID Jadwal wajib diisi!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = "INSERT INTO jadwal_kuliah VALUES (%s, %s, %s, %s, %s, %s)"
            val = (id_j, self.entry_kodemk.get(), self.combo_hari.get(), self.entry_jammulai.get(), self.entry_jamselesai.get(), self.entry_ruangan.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data Jadwal berhasil ditambahkan!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambah data: {e}")

    def edit_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = """UPDATE jadwal_kuliah SET kode_mk=%s, hari=%s, jam_mulai=%s, 
                     jam_selesai=%s, ruangan=%s WHERE id_jadwal=%s"""
            val = (self.entry_kodemk.get(), self.combo_hari.get(), self.entry_jammulai.get(), self.entry_jamselesai.get(), self.entry_ruangan.get(), self.entry_id.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

    def hapus_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        id_j = self.entry_id.get()
        if messagebox.askyesno("Konfirmasi", f"Yakin hapus ID Jadwal {id_j}?"):
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM jadwal_kuliah WHERE id_jadwal = %s", (id_j,))
                db.commit()
                db.close()
                messagebox.showinfo("Sukses", "Data berhasil dihapus!")
                self.clear_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data: {e}")

    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clear_fields()
            self.entry_id.insert(0, values[0])
            self.entry_kodemk.insert(0, values[1])
            self.combo_hari.set(values[2])
            self.entry_jammulai.insert(0, values[3])
            self.entry_jamselesai.insert(0, values[4])
            self.entry_ruangan.insert(0, values[5])

    def clear_fields(self):
        self.entry_id.delete(0, tk.END)
        self.entry_kodemk.delete(0, tk.END)
        self.combo_hari.set("")
        self.entry_jammulai.delete(0, tk.END)
        self.entry_jamselesai.delete(0, tk.END)
        self.entry_ruangan.delete(0, tk.END)


# --- TAB KRS ---
class TabKRS(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        frame_form = tk.LabelFrame(self, text=" Form Kartu Rencana Studi (KRS) ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=10)

        labels = ["ID KRS", "NIM", "Kode MK", "Semester Ambil", "Tahun Ajaran", "Nilai Huruf", "Nilai Angka"]
        for i, label_text in enumerate(labels):
            tk.Label(frame_form, text=label_text).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=3)

        self.entry_id = tk.Entry(frame_form)
        self.entry_id.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

        self.entry_nim = tk.Entry(frame_form)
        self.entry_nim.grid(row=0, column=3, padx=5, pady=3, sticky="ew")

        self.entry_kodemk = tk.Entry(frame_form)
        self.entry_kodemk.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

        self.entry_smt = tk.Entry(frame_form)
        self.entry_smt.grid(row=1, column=3, padx=5, pady=3, sticky="ew")

        self.entry_thn = tk.Entry(frame_form)
        self.entry_thn.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

        self.combo_huruf = ttk.Combobox(frame_form, values=["A", "A-", "B+", "B", "B-", "C+", "C", "D", "E"], state="readonly")
        self.combo_huruf.grid(row=2, column=3, padx=5, pady=3, sticky="ew")

        self.entry_angka = tk.Entry(frame_form)
        self.entry_angka.grid(row=3, column=1, padx=5, pady=3, sticky="ew")

        frame_form.grid_columnconfigure(1, weight=1)
        frame_form.grid_columnconfigure(3, weight=1)

        buat_tombol_crud(self, self.tambah_data, self.edit_data, self.hapus_data, self.clear_fields)

        frame_table = tk.Frame(self)
        frame_table.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id_krs", "nim", "kode_mk", "semester_ambil", "tahun_ajaran", "nilai_huruf", "nilai_angka")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")

        headers = ["ID KRS", "NIM", "Kode MK", "Semester", "Tahun Ajaran", "Nilai Huruf", "Nilai Angka"]
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=110)

        self.tree.bind("<<TreeviewSelect>>", self.select_item)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM krs")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data KRS: {e}")

    def tambah_data(self):
        id_krs = self.entry_id.get()
        if not id_krs:
            messagebox.showwarning("Warning", "ID KRS wajib diisi!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = "INSERT INTO krs VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (id_krs, self.entry_nim.get(), self.entry_kodemk.get(), self.entry_smt.get(), self.entry_thn.get(), self.combo_huruf.get(), self.entry_angka.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data KRS berhasil ditambahkan!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambah data: {e}")

    def edit_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = """UPDATE krs SET nim=%s, kode_mk=%s, semester_ambil=%s, 
                     tahun_ajaran=%s, nilai_huruf=%s, nilai_angka=%s WHERE id_krs=%s"""
            val = (self.entry_nim.get(), self.entry_kodemk.get(), self.entry_smt.get(), self.entry_thn.get(), self.combo_huruf.get(), self.entry_angka.get(), self.entry_id.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data KRS diperbarui!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

    def hapus_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        id_krs = self.entry_id.get()
        if messagebox.askyesno("Konfirmasi", f"Yakin hapus ID KRS {id_krs}?"):
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM krs WHERE id_krs = %s", (id_krs,))
                db.commit()
                db.close()
                messagebox.showinfo("Sukses", "Data berhasil dihapus!")
                self.clear_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data: {e}")

    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clear_fields()
            self.entry_id.insert(0, values[0])
            self.entry_nim.insert(0, values[1])
            self.entry_kodemk.insert(0, values[2])
            self.entry_smt.insert(0, values[3])
            self.entry_thn.insert(0, values[4])
            self.combo_huruf.set(values[5])
            self.entry_angka.insert(0, values[6])

    def clear_fields(self):
        self.entry_id.delete(0, tk.END)
        self.entry_nim.delete(0, tk.END)
        self.entry_kodemk.delete(0, tk.END)
        self.entry_smt.delete(0, tk.END)
        self.entry_thn.delete(0, tk.END)
        self.combo_huruf.set("")
        self.entry_angka.delete(0, tk.END)


# --- TAB PEMBAYARAN UKT ---
class TabPembayaranUKT(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        frame_form = tk.LabelFrame(self, text=" Form Pembayaran UKT ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=10)

        labels = ["ID Pembayaran", "NIM", "Semester", "Tahun Ajaran", "Jumlah Bayar", "Tgl Bayar (YYYY-MM-DD)", "Metode Pembayaran", "Status"]
        for i, label_text in enumerate(labels):
            tk.Label(frame_form, text=label_text).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=3)

        self.entry_id = tk.Entry(frame_form)
        self.entry_id.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

        self.entry_nim = tk.Entry(frame_form)
        self.entry_nim.grid(row=0, column=3, padx=5, pady=3, sticky="ew")

        self.entry_smt = tk.Entry(frame_form)
        self.entry_smt.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

        self.entry_thn = tk.Entry(frame_form)
        self.entry_thn.grid(row=1, column=3, padx=5, pady=3, sticky="ew")

        self.entry_jumlah = tk.Entry(frame_form)
        self.entry_jumlah.grid(row=2, column=1, padx=5, pady=3, sticky="ew")

        self.entry_tgl = tk.Entry(frame_form)
        self.entry_tgl.grid(row=2, column=3, padx=5, pady=3, sticky="ew")

        self.combo_metode = ttk.Combobox(frame_form, values=["Transfer Bank", "Virtual Account", "Tunai"], state="readonly")
        self.combo_metode.grid(row=3, column=1, padx=5, pady=3, sticky="ew")

        self.combo_status = ttk.Combobox(frame_form, values=["Lunas", "Belum Lunas"], state="readonly")
        self.combo_status.grid(row=3, column=3, padx=5, pady=3, sticky="ew")

        frame_form.grid_columnconfigure(1, weight=1)
        frame_form.grid_columnconfigure(3, weight=1)

        buat_tombol_crud(self, self.tambah_data, self.edit_data, self.hapus_data, self.clear_fields)

        frame_table = tk.Frame(self)
        frame_table.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id_pembayaran", "nim", "semester", "tahun_ajaran", "jumlah_bayar", "tanggal_bayar", "metode_pembayaran", "status")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")

        headers = ["ID Bayar", "NIM", "Semester", "Tahun Ajaran", "Jumlah Bayar", "Tanggal Bayar", "Metode", "Status"]
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=110)

        self.tree.bind("<<TreeviewSelect>>", self.select_item)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM pembayaran_ukt")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data pembayaran UKT: {e}")

    def tambah_data(self):
        id_p = self.entry_id.get()
        if not id_p:
            messagebox.showwarning("Warning", "ID Pembayaran wajib diisi!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = "INSERT INTO pembayaran_ukt VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (id_p, self.entry_nim.get(), self.entry_smt.get(), self.entry_thn.get(),
                   self.entry_jumlah.get(), self.entry_tgl.get() or None,
                   self.combo_metode.get() or None, self.combo_status.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data Pembayaran UKT berhasil ditambahkan!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambah data: {e}")

    def edit_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        try:
            db = connect_db()
            cursor = db.cursor()
            sql = """UPDATE pembayaran_ukt SET nim=%s, semester=%s, tahun_ajaran=%s, 
                     jumlah_bayar=%s, tanggal_bayar=%s, metode_pembayaran=%s, status=%s WHERE id_pembayaran=%s"""
            val = (self.entry_nim.get(), self.entry_smt.get(), self.entry_thn.get(),
                   self.entry_jumlah.get(), self.entry_tgl.get() or None,
                   self.combo_metode.get() or None, self.combo_status.get(), self.entry_id.get())
            cursor.execute(sql, val)
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data Pembayaran UKT diperbarui!")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

    def hapus_data(self):
        if not self.tree.selection():
            messagebox.showwarning("Warning", "Pilih data di tabel!")
            return
        id_p = self.entry_id.get()
        if messagebox.askyesno("Konfirmasi", f"Yakin hapus ID Pembayaran {id_p}?"):
            try:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM pembayaran_ukt WHERE id_pembayaran = %s", (id_p,))
                db.commit()
                db.close()
                messagebox.showinfo("Sukses", "Data berhasil dihapus!")
                self.clear_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus data: {e}")

    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clear_fields()
            self.entry_id.insert(0, values[0])
            self.entry_nim.insert(0, values[1])
            self.entry_smt.insert(0, values[2])
            self.entry_thn.insert(0, values[3])
            self.entry_jumlah.insert(0, values[4])
            if values[5] and values[5] != "None":
                self.entry_tgl.insert(0, values[5])
            if values[6] and values[6] != "None":
                self.combo_metode.set(values[6])
            self.combo_status.set(values[7])

    def clear_fields(self):
        self.entry_id.delete(0, tk.END)
        self.entry_nim.delete(0, tk.END)
        self.entry_smt.delete(0, tk.END)
        self.entry_thn.delete(0, tk.END)
        self.entry_jumlah.delete(0, tk.END)
        self.entry_tgl.delete(0, tk.END)
        self.combo_metode.set("")
        self.combo_status.set("")


# ==========================================
# 3. APLIKASI DASHBOARD UTAMA (SIDEBAR KIRI + KONTEN KANAN)
# ==========================================
class AplikasiSIAKAD(tk.Tk):
    def __init__(self, user, role):
        super().__init__()
        terapkan_tema(self)
        self.logout_requested = False   # penanda: keluar lewat tombol Logout
        self.title("Sistem Informasi Akademik (SIAKAD)")
        self.geometry("1150x700")
        self.minsize(1000, 620)
        self.configure(bg=OUTER)

        # Kartu besar membulat sebagai badan aplikasi
        shell = KartuBulat(self, fill=LAVENDER, outer=OUTER, radius=30, inset=12)
        shell.pack(fill="both", expand=True, padx=14, pady=14)
        body = shell.isi

        # ---------- SIDEBAR ----------
        sidebar = KartuBulat(body, fill=SIDEBAR_BG, outer=LAVENDER, radius=24, inset=10)
        sidebar.configure(width=236)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sb = sidebar.isi

        # Logo + nama aplikasi
        brand = tk.Frame(sb, bg=SIDEBAR_BG)
        brand.pack(fill="x", pady=(4, 14))
        logo = tk.Canvas(brand, width=56, height=46, bg=SIDEBAR_BG, highlightthickness=0)
        logo.pack(side="left", padx=(8, 4))
        gambar_kupu_kupu(logo, skala=0.4)
        tk.Label(brand, text="SIAKAD", font=(FONT_FAMILY, 18, "bold"),
                 bg=SIDEBAR_BG, fg=PURPLE).pack(side="left")

        # Profil pengguna
        inisial = (user['nama'].strip()[:1] or "?").upper()
        avatar = tk.Canvas(sb, width=76, height=76, bg=SIDEBAR_BG, highlightthickness=0)
        avatar.pack(pady=(4, 6))
        avatar.create_oval(2, 2, 74, 74, fill=PURPLE, outline=WHITE, width=3)
        avatar.create_text(38, 38, text=inisial, fill=WHITE, font=(FONT_FAMILY, 26, "bold"))
        tk.Label(sb, text=user['nama'], font=(FONT_FAMILY, 11, "bold"),
                 bg=SIDEBAR_BG, fg=PURPLE_DARK, wraplength=190, justify="center").pack()
        tk.Label(sb, text=role, font=(FONT_FAMILY, 9),
                 bg=SIDEBAR_BG, fg=PURPLE).pack(pady=(0, 16))

        # Menu navigasi (diisi setelah tab dibuat)
        nav = tk.Frame(sb, bg=SIDEBAR_BG)
        nav.pack(fill="x")

        # Logout di bagian bawah sidebar
        NavItem(sb, "Logout", self.logout, fg=ROSE, titik=ROSE).pack(side="bottom", pady=(0, 4))

        # ---------- KONTEN UTAMA ----------
        main = tk.Frame(body, bg=LAVENDER)
        main.pack(side="left", fill="both", expand=True)

        tk.Label(
            main,
            text=f"DASHBOARD SIAKAD - [{role.upper()}: {user['nama']}]",
            font=(FONT_FAMILY, 14, "bold"),
            bg=LAVENDER,
            fg=PURPLE
        ).pack(anchor="w", padx=6, pady=(6, 10))

        card = KartuBulat(main, fill=WHITE, outer=LAVENDER, radius=24, inset=10)
        card.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(card.isi, style="Hidden.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Inisialisasi seluruh tab (Dashboard + 6 tabel)
        self.tab_dashboard = TabDashboard(self.notebook, user, role)
        self.tab_dosen = TabDosen(self.notebook)
        self.tab_mahasiswa = TabMahasiswa(self.notebook)
        self.tab_matakuliah = TabMataKuliah(self.notebook)
        self.tab_jadwal = TabJadwal(self.notebook)
        self.tab_krs = TabKRS(self.notebook)
        self.tab_ukt = TabPembayaranUKT(self.notebook)

        halaman = [
            ("Dashboard", self.tab_dashboard),
            ("Data Dosen", self.tab_dosen),
            ("Data Mahasiswa", self.tab_mahasiswa),
            ("Mata Kuliah", self.tab_matakuliah),
            ("Jadwal Kuliah", self.tab_jadwal),
            ("KRS", self.tab_krs),
            ("Pembayaran UKT", self.tab_ukt),
        ]
        self.halaman = []
        self.nav_items = []
        for i, (teks, tab) in enumerate(halaman):
            self.notebook.add(tab, text=f" {teks} ")
            item = NavItem(nav, teks, lambda idx=i: self.pilih_halaman(idx))
            item.pack(pady=3)
            self.halaman.append(tab)
            self.nav_items.append(item)

        self.pilih_halaman(0)

    def pilih_halaman(self, indeks):
        self.notebook.select(self.halaman[indeks])
        for i, item in enumerate(self.nav_items):
            item.set_aktif(i == indeks)
        if indeks == 0:                      # refresh angka saat membuka Dashboard
            self.tab_dashboard.refresh()

    def logout(self):
        if messagebox.askyesno("Konfirmasi Logout", "Yakin ingin logout?"):
            self.logout_requested = True
            self.destroy()


# ==========================================
# 4. LOOP UTAMA: LOGIN -> DASHBOARD -> LOGOUT -> LOGIN ...
# ==========================================
def main():
    while True:
        # 1) Tampilkan form login
        root = tk.Tk()
        login = LoginWindow(root)
        root.mainloop()

        # Kalau form login ditutup tanpa login (klik X), program berhenti
        if login.result is None:
            break

        # 2) Login berhasil, buka dashboard
        user, role = login.result
        app = AplikasiSIAKAD(user, role)
        app.mainloop()

        # 3) Kalau keluar lewat tombol Logout, ulangi dari form login.
        #    Kalau dashboard ditutup lewat tombol X, program berhenti.
        if not app.logout_requested:
            break


if __name__ == "__main__":
    main()