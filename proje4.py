import sqlite3
import time

def baglan():
    return sqlite3.connect("randevular.db")

def tablo():
    conn = baglan()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS randevular (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT,
        soyad TEXT,
        tarih TEXT,
        saat TEXT,
        hizmet TEXT,
        fiyat INTEGER
    )
    """)

    conn.commit()
    conn.close()

tablo()

#   VERİ

hizmetler = {
    "1": ("Saç", 200),
    "2": ("Sakal", 150),
    "3": ("Saç + Sakal", 350)
}

def saat_slotlari():
    slots = []

    for h in list(range(8, 12)) + list(range(13, 17)):
        for m in (0, 30):
            slots.append(f"{h:02d}:{m:02d}")
    slots.append("17:00") #17 00 olmadıgı icin ekledim
    return slots

def verileri_cek():
    conn = baglan()
    cur = conn.cursor()
    cur.execute("SELECT ad, soyad, tarih, saat, hizmet, fiyat FROM randevular")
    data = cur.fetchall()
    conn.close()
    return data

#   RANDEVU AL

def randevu_al(ad, soyad):

    data = verileri_cek()
    tarih = input("Tarih (GG-AA): ")

    dolu = [r[3] for r in data if r[2] == tarih]
    bos = [s for s in saat_slotlari() if s not in dolu]

    if not bos:
        print("Bugün tüm saatler dolu!")
        return

    print("\n--- BOŞ SAATLER ---")
    for i, s in enumerate(bos):
        print(f"{i+1}- {s}")

    while True:
        secim = input("Saat seçiniz(SS:DD): ")

        if secim.isdigit() and 1 <= int(secim) <= len(bos):
            saat = bos[int(secim)-1]
            break

        print("Yanlış seçim yapıldı, lütfen doğru seçim yapın.")

    print("\n--- HİZMETLER ---")
    print("1- Saç (200 TL)")
    print("2- Sakal (150 TL)")
    print("3- Saç + Sakal (350 TL)")
    while True:
        h = input("Seçim: ")

        if h in hizmetler:
            hizmet, fiyat = hizmetler[h]
            break

        print("Yanlış seçim yapıldı, lütfen doğru seçim yapın.")

    conn = baglan()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO randevular (ad, soyad, tarih, saat, hizmet, fiyat)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ad, soyad, tarih, saat, hizmet, fiyat))

    conn.commit()
    conn.close()

    print("Randevu oluşturuldu")

#   MÜŞTERİ

def randevulari_goster(ad, soyad):

    data = verileri_cek()

    bulundu = False

    for r in data:
        if r[0] == ad and r[1] == soyad:
            print(r)
            bulundu = True

    if not bulundu:
        print("Randevu yok")

def saat_degistir(ad, soyad):

    data = verileri_cek()

    tarih = input("Tarih (GG-AA): ")

    hedef = None

    for r in data:
        if r[0] == ad and r[1] == soyad and r[2] == tarih:
            hedef = r
            break

    if not hedef:
        print("Randevu bulunamadı")
        return

    print("Mevcut saat:", hedef[3])

    dolu = [r[3] for r in data if r[2] == tarih]
    bos = [s for s in saat_slotlari() if s not in dolu]

    print("\n--- BOŞ SAATLER ---")
    for i, s in enumerate(bos):
        print(f"{i+1}- {s}")

    while True:
        secim = input("Yeni saat seçiniz(SS:DD): ")

        if secim.isdigit() and 1 <= int(secim) <= len(bos):
            yeni = bos[int(secim)-1]
            break

        print("Yanlış seçim yapıldı, lütfen doğru seçim yapın.")

    conn = baglan()
    cur = conn.cursor()

    cur.execute("""
        UPDATE randevular
        SET saat=?
        WHERE ad=? AND soyad=? AND tarih=? AND saat=?
    """, (yeni, ad, soyad, tarih, hedef[3]))

    conn.commit()
    conn.close()

    print("Randevu saati değiştirildi")

#   ADMIN

def tum_randevular():
    for r in verileri_cek():
        print(r)

def gunluk_randevular():

    data = verileri_cek()
    tarih = input("Tarih (GG-AA): ")

    bulundu = False

    for r in data:
        if r[2] == tarih:
            print(r)
            bulundu = True

    if not bulundu:
        print("Randevu yok")

def randevu_sil():

    tarih = input("Tarih (GG-AA): ")
    saat = input("Saat(SS:DD): ")

    conn = baglan()
    cur = conn.cursor()

    cur.execute("SELECT * FROM randevular WHERE tarih=? AND saat=?", (tarih, saat))
    r = cur.fetchone()

    if not r:
        print("Randevu bulunamadı")
        return

    print("Randevu:", r[1], r[2])

    while True:

        onay = input("Silinsin mi? (evet/hayır): ")

        if onay == "evet":

            cur.execute("DELETE FROM randevular WHERE tarih=? AND saat=?", (tarih, saat))
            conn.commit()
            conn.close()

            print("Randevu silindi")
            return

        elif onay == "hayır":
            print("Silme iptal edildi")
            return

        else:
            print("Yanlış seçim yapıldı, lütfen doğru seçim yapın.")

def gunluk_kazanc():

    conn = baglan()
    cur = conn.cursor()

    tarih = input("Tarih (GG-AA): ")

    cur.execute("SELECT SUM(fiyat) FROM randevular WHERE tarih=?", (tarih,))
    sonuc = cur.fetchone()[0]

    print("Toplam kazanç:", sonuc or 0)

def tum_kazanc():

    conn = baglan()
    cur = conn.cursor()

    cur.execute("SELECT SUM(fiyat) FROM randevular")
    sonuc = cur.fetchone()[0]

    print("Tüm zamanların kazancı:", sonuc or 0)

#   ANA MENÜ

while True:

    print("\n--- BERBER RANDEVU SİSTEMİ ---")
    print("1- Müşteri Girişi")
    print("2- Yönetici Girişi")
    print("3- Çıkış")

    secim = input("Seçim: ")

    if secim == "1":

        ad = input("Ad: ")
        soyad = input("Soyad: ")

        while True:

            print("\n1- Randevu Al")
            print("2- Randevularımı Gör")
            print("3- Randevu Saatini Değiştir")
            print("4- Çıkış")

            alt = input("Seçim: ")

            if alt == "1":
                randevu_al(ad, soyad)

            elif alt == "2":
                randevulari_goster(ad, soyad)

            elif alt == "3":
                saat_degistir(ad, soyad)

            elif alt == "4":
                break

            else:
                print("Yanlış seçim yapıldı, lütfen doğru seçim yapın.")


    elif secim == "2":

        k = input("Kullanıcı adı: ")
        s = input("Şifre: ")

        if k == "admin" and s == "1234":

            while True:

                print("\n--- YÖNETİCİ PANEL ---")
                print("1- Günlük Randevular")
                print("2- Tüm Randevular")
                print("3- Randevu Sil")
                print("4- Günlük Kazanç")
                print("5- Tüm Kazanç")
                print("6- Çıkış")

                alt = input("Seçim: ")

                if alt == "1":
                    gunluk_randevular()
                elif alt == "2":
                    tum_randevular()
                elif alt == "3":
                    randevu_sil()
                elif alt == "4":
                    gunluk_kazanc()
                elif alt == "5":
                    tum_kazanc()
                elif alt == "6":
                    break
                else:
                    print("Yanlış seçim yapıldı, lütfen doğru seçim yapın.")

        else:
            print("Hatalı giriş")


    elif secim == "3":
        print("Çıkış yapılıyor...")
        time.sleep(1)
        break

    else:
        print("Yanlış seçim yapıldı, lütfen doğru seçim yapın.")