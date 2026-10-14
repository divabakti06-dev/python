# ===== Class Induk =====
class Karyawan:
    def __init__(self, nama, id_karyawan, gaji_pokok):
        self.nama = nama                # atribut public
        self.id_karyawan = id_karyawan  # atribut public
        self.__gaji_pokok = gaji_pokok  # atribut private (pakai __)

    # getter: ambil nilai gaji pokok
    def get_gaji_pokok(self):
        return self.__gaji_pokok

    # setter: ubah gaji pokok, tolak kalau nilainya <= 0
    def set_gaji_pokok(self, nilai):
        if nilai <= 0:
            print("Peringatan: gaji pokok harus lebih dari 0!")
        else:
            self.__gaji_pokok = nilai

    # hitung gaji versi dasar (gaji pokok saja)
    def hitung_gaji_total(self):
        return self.__gaji_pokok

    # tampilkan data dasar karyawan
    def tampilkan_info(self):
        print("Nama        :", self.nama)
        print("ID Karyawan :", self.id_karyawan)
        print("Gaji Pokok  :", self.get_gaji_pokok())


# ===== Class Anak 1 =====
class KaryawanTetap(Karyawan):
    def __init__(self, nama, id_karyawan, gaji_pokok, tunjangan):
        super().__init__(nama, id_karyawan, gaji_pokok)  # panggil constructor induk
        self.tunjangan = tunjangan                       # atribut tambahan

    # overriding: gaji pokok + tunjangan
    def hitung_gaji_total(self):
        return self.get_gaji_pokok() + self.tunjangan

    # overriding: tampilkan info lengkap karyawan tetap
    def tampilkan_info(self):
        print("--- Karyawan Tetap ---")
        print("Nama        :", self.nama)
        print("ID Karyawan :", self.id_karyawan)
        print("Gaji Pokok  :", self.get_gaji_pokok())
        print("Tunjangan   :", self.tunjangan)
        print("Total Gaji  :", self.hitung_gaji_total())


# ===== Class Anak 2 =====
class KaryawanKontrak(Karyawan):
    def __init__(self, nama, id_karyawan, gaji_pokok, jam_lembur, tarif_lembur):
        super().__init__(nama, id_karyawan, gaji_pokok)  # panggil constructor induk
        self.jam_lembur = jam_lembur                     # atribut tambahan
        self.tarif_lembur = tarif_lembur                 # atribut tambahan

    # overriding: gaji pokok + (jam lembur x tarif lembur)
    def hitung_gaji_total(self):
        return self.get_gaji_pokok() + (self.jam_lembur * self.tarif_lembur)

    # overriding: tampilkan info lengkap karyawan kontrak
    def tampilkan_info(self):
        print("--- Karyawan Kontrak ---")
        print("Nama         :", self.nama)
        print("ID Karyawan  :", self.id_karyawan)
        print("Gaji Pokok   :", self.get_gaji_pokok())
        print("Jam Lembur   :", self.jam_lembur)
        print("Tarif Lembur :", self.tarif_lembur)
        print("Total Gaji   :", self.hitung_gaji_total())


# ===== Main Program =====

# buat objek karyawan tetap dan kontrak
k1 = KaryawanTetap("Nadivatul Latifah", "202512014", 5000000, 1500000)
k2 = KaryawanKontrak("Nanad", "202511014", 3000000, 20, 50000)

# simpan ke list
daftar_karyawan = [k1, k2]

# polymorphism: method sama, hasil beda tiap objek
print("=== POLYMORPHISM ===")
for k in daftar_karyawan:
    k.tampilkan_info()
    print()

# encapsulation: ubah gaji lewat setter
print("=== ENCAPSULATION ===")
k1.set_gaji_pokok(-1000)     # tidak valid, muncul peringatan
k1.set_gaji_pokok(6000000)   # valid, gaji berubah
k1.tampilkan_info()          # tampilkan hasil setelah diubah