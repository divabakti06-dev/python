# Mengimpor modul tkinter dasar untuk pembuatan komponen GUI
import tkinter as tk
# Mengimpor ttk untuk widget bertema (Combobox & Treeview) dan messagebox untuk dialog pop-up
from tkinter import ttk, messagebox
# Mengimpor mysql.connector untuk koneksi dan operasi database MySQL
import mysql.connector

# --- KONEKSI DATABASE ---
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="siakad"
    )

# Daftar kolom tabel (urutan sama dengan tabel di database)
KOLOM = ("nim", "nama_lengkap", "jenis_kelamin", "tanggal_lahir", "tempat_lahir",
         "alamat", "no_telepon", "email", "jurusan", "angkatan", "status")

# --- FUNGSI BANTU ---
# Mengambil seluruh nilai dari form dalam bentuk tuple (urutan sesuai KOLOM)
def ambil_form():
    return (
        entry_nim.get().strip(),
        entry_nama.get().strip(),
        combo_jk.get(),
        entry_tgl.get().strip(),          # format: YYYY-MM-DD
        entry_tempat.get().strip(),
        entry_alamat.get().strip(),
        entry_tlp.get().strip(),
        entry_email.get().strip(),
        combo_jurusan.get(),
        entry_angkatan.get().strip(),
        combo_status.get(),
    )

# Mengosongkan seluruh isian form
def clear_fields():
    entry_nim.config(state="normal")      # NIM bisa diisi lagi saat mode tambah
    for e in (entry_nim, entry_nama, entry_tgl, entry_tempat, entry_alamat,
              entry_tlp, entry_email, entry_angkatan):
        e.delete(0, tk.END)
    for c in (combo_jk, combo_jurusan, combo_status):
        c.set("")

# --- FUNGSI CRUD ---
# READ: memuat seluruh data dari tabel mahasiswa ke Treeview
def load_data(keyword=""):
    for row in tree.get_children():
        tree.delete(row)
    try:
        db = connect_db()
        cursor = db.cursor()
        if keyword:
            # Pencarian berdasarkan NIM atau nama
            sql = f"SELECT {', '.join(KOLOM)} FROM mahasiswa WHERE nim LIKE %s OR nama_lengkap LIKE %s ORDER BY nim"
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%"))
        else:
            cursor.execute(f"SELECT {', '.join(KOLOM)} FROM mahasiswa ORDER BY nim")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        db.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Gagal mengambil data: {e}")

# CREATE: menambahkan mahasiswa baru
def tambah_data():
    val = ambil_form()
    if not val[0] or not val[1]:
        messagebox.showwarning("Warning", "NIM dan Nama Lengkap wajib diisi!")
        return
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = f"INSERT INTO mahasiswa ({', '.join(KOLOM)}) VALUES ({', '.join(['%s'] * len(KOLOM))})"
        cursor.execute(sql, val)
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil ditambahkan!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menambah data: {e}")

# UPDATE: memperbarui data mahasiswa yang dipilih (acuan: NIM)
def edit_data():
    if not tree.selection():
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin diubah!")
        return
    val = ambil_form()
    try:
        db = connect_db()
        cursor = db.cursor()
        sql = """UPDATE mahasiswa SET nama_lengkap=%s, jenis_kelamin=%s, tanggal_lahir=%s,
                 tempat_lahir=%s, alamat=%s, no_telepon=%s, email=%s, jurusan=%s,
                 angkatan=%s, status=%s WHERE nim=%s"""
        # NIM dipindah ke urutan terakhir untuk klausa WHERE
        cursor.execute(sql, val[1:] + (val[0],))
        db.commit()
        db.close()
        messagebox.showinfo("Sukses", "Data berhasil diperbarui!")
        clear_fields()
        load_data()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memperbarui data: {e}")

# DELETE: menghapus mahasiswa yang dipilih
def hapus_data():
    if not tree.selection():
        messagebox.showwarning("Warning", "Pilih data di tabel yang ingin dihapus!")
        return
    nim = entry_nim.get()
    if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus mahasiswa NIM {nim}?"):
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM mahasiswa WHERE nim = %s", (nim,))
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
            clear_fields()
            load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")

# Event: saat baris tabel dipilih, isi form dengan datanya
def select_item(event):
    selected = tree.selection()
    if selected:
        v = tree.item(selected[0], "values")
        clear_fields()
        entry_nim.insert(0, v[0])
        entry_nama.insert(0, v[1])
        combo_jk.set(v[2])
        entry_tgl.insert(0, v[3])
        entry_tempat.insert(0, v[4])
        entry_alamat.insert(0, v[5])
        entry_tlp.insert(0, v[6])
        entry_email.insert(0, v[7])
        combo_jurusan.set(v[8])
        entry_angkatan.insert(0, v[9])
        combo_status.set(v[10])

# Event: tombol cari
def cari_data():
    load_data(entry_cari.get().strip())

# Event: tombol reset pencarian
def reset_data():
    entry_cari.delete(0, tk.END)
    load_data()

# --- GUI MAIN WINDOW ---
root = tk.Tk()
root.title("Aplikasi Data Mahasiswa - SIAKAD")
root.geometry("1200x650")

# Form input
frame_form = tk.LabelFrame(root, text=" Form Data Mahasiswa ", padx=10, pady=10)
frame_form.pack(fill="x", padx=15, pady=10)

labels = ["NIM", "Nama Lengkap", "Jenis Kelamin", "Tanggal Lahir (YYYY-MM-DD)",
          "Tempat Lahir", "Alamat", "No Telepon", "Email", "Jurusan", "Angkatan", "Status"]
for i, teks in enumerate(labels):
    tk.Label(frame_form, text=teks).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=3)

entry_nim = tk.Entry(frame_form)
entry_nama = tk.Entry(frame_form)
combo_jk = ttk.Combobox(frame_form, values=["Laki-laki", "Perempuan"], state="readonly")
entry_tgl = tk.Entry(frame_form)
entry_tempat = tk.Entry(frame_form)
entry_alamat = tk.Entry(frame_form)
entry_tlp = tk.Entry(frame_form)
entry_email = tk.Entry(frame_form)
combo_jurusan = ttk.Combobox(frame_form, values=["Teknik Informatika", "Sistem Informasi", "Manajemen Informatika"])
entry_angkatan = tk.Entry(frame_form)
combo_status = ttk.Combobox(frame_form, values=["Aktif", "Cuti", "Lulus", "Non-Aktif"], state="readonly")

# Penempatan widget pada grid (2 kolom pasangan label-input)
widgets = [entry_nim, entry_nama, combo_jk, entry_tgl, entry_tempat, entry_alamat,
           entry_tlp, entry_email, combo_jurusan, entry_angkatan, combo_status]
for i, w in enumerate(widgets):
    w.grid(row=i//2, column=(i%2)*2 + 1, padx=5, pady=3, sticky="ew")

frame_form.grid_columnconfigure(1, weight=1)
frame_form.grid_columnconfigure(3, weight=1)

# Tombol aksi + pencarian
frame_btn = tk.Frame(root)
frame_btn.pack(fill="x", padx=15, pady=5)

tk.Button(frame_btn, text="Tambah", bg="#4CAF50", fg="white", command=tambah_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Edit", bg="#2196F3", fg="white", command=edit_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Hapus", bg="#f44336", fg="white", command=hapus_data, width=12).pack(side="left", padx=5)
tk.Button(frame_btn, text="Clear", bg="#9E9E9E", fg="white", command=clear_fields, width=12).pack(side="left", padx=5)

tk.Button(frame_btn, text="Reset", command=reset_data, width=8).pack(side="right", padx=5)
tk.Button(frame_btn, text="Cari", command=cari_data, width=8).pack(side="right", padx=5)
entry_cari = tk.Entry(frame_btn, width=25)
entry_cari.pack(side="right", padx=5)
tk.Label(frame_btn, text="Cari (NIM/Nama):").pack(side="right")

# Tabel
frame_table = tk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=15, pady=10)

tree = ttk.Treeview(frame_table, columns=KOLOM, show="headings")

judul = ["NIM", "Nama Lengkap", "Jenis Kelamin", "Tgl Lahir", "Tempat Lahir",
         "Alamat", "No Telepon", "Email", "Jurusan", "Angkatan", "Status"]
lebar = [80, 140, 90, 90, 90, 160, 110, 150, 130, 65, 60]
for k, j, w in zip(KOLOM, judul, lebar):
    tree.heading(k, text=j)
    tree.column(k, width=w)

tree.bind("<<TreeviewSelect>>", select_item)

scroll_y = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_table, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
tree.pack(side="left", fill="both", expand=True)

# Tampilkan data awal lalu jalankan aplikasi
load_data()
root.mainloop()