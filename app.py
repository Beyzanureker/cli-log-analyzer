import os
import csv
import yaml
import time
from datetime import datetime
class Renkler:
    KIRMIZI    = "\033[91m"
    YESIL      = "\033[92m"
    SARI       = "\033[93m"
    MAVI       = "\033[94m"
    MAGENTA    = "\033[95m"
    SIYAN      = "\033[96m"
    BEYAZ      = "\033[97m"
    KALIN      = "\033[1m"
    SIFIRLA    = "\033[0m"

class LogAnalyzer:
    def __init__(self):
        self.kurallar = self.kurallari_yukle()
        self.bulunan_olaylar = []
        
    def kurallari_yukle(self):
        try:
            with open('rules.yaml', 'r', encoding='utf-8') as f:
                veri = yaml.safe_load(f)
                return veri['rules']
        except Exception as e:
            print(f"{Renkler.KIRMIZI}❌ Kural dosyası yüklenirken hata: {e}{Renkler.SIFIRLA}")
            return []
    
    def dosya_analiz_et(self, dosya_yolu):
        print(f"\n{Renkler.MAVI}📁 {dosya_yolu} dosyası analiz ediliyor...{Renkler.SIFIRLA}")
        print(f"{Renkler.SIYAN}{'─' * 50}{Renkler.SIFIRLA}")
        
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                satirlar = f.readlines()
                
            toplam_eslesme = 0
            
            for satir_no, satir in enumerate(satirlar, 1):
                for kural in self.kurallar:
                    for kelime in kural['keywords']:
                        if kelime in satir:
                            toplam_eslesme += 1
                            mesaj_kisa = satir.strip()[:100] + '...' if len(satir.strip()) > 100 else satir.strip()
                            
                            self.bulunan_olaylar.append({
                                'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'dosya': os.path.basename(dosya_yolu),
                                'satir_no': satir_no,
                                'seviye': kural['severity'],
                                'kural_adi': kural['name'],
                                'mesaj': mesaj_kisa
                            })
                            if kural['severity'] == 'YUKSEK':
                                renk = Renkler.KIRMIZI
                            elif kural['severity'] == 'ORTA':
                                renk = Renkler.SARI
                            else:
                                renk = Renkler.YESIL
                            
                            print(f"  {renk}⚠️  [{kural['severity']}] {kural['name']}{Renkler.SIFIRLA} - Satır {satir_no}")
                            break
            
            print(f"{Renkler.SIYAN}{'─' * 50}{Renkler.SIFIRLA}")
            print(f"{Renkler.YESIL}✅ Toplam {toplam_eslesme} eşleşme bulundu{Renkler.SIFIRLA}\n")
            
        except FileNotFoundError:
            print(f"{Renkler.KIRMIZI}❌ Dosya bulunamadı: {dosya_yolu}{Renkler.SIFIRLA}\n")
        except Exception as e:
            print(f"{Renkler.KIRMIZI}❌ Hata oluştu: {e}{Renkler.SIFIRLA}\n")
    
    def gercek_zamanli_izle(self, dosya_yolu, sure=10):
        print(f"\n{Renkler.KIRMIZI}🔴 Gerçek zamanlı izleme başlatıldı: {dosya_yolu}{Renkler.SIFIRLA}")
        print(f"{Renkler.SARI}⏱️  {sure} saniye boyunca izlenecek... (Ctrl+C ile durabilirsin){Renkler.SIFIRLA}\n")
        
        try:
            with open(dosya_yolu, 'r') as f:
                f.seek(0, 2)
                
                baslangic = time.time()
                beklemede = True
                
                while (time.time() - baslangic) < sure:
                    satir = f.readline()
                    
                    if satir:
                        beklemede = False
                        for kural in self.kurallar:
                            for kelime in kural['keywords']:
                                if kelime in satir:
                                    if kural['severity'] == 'YUKSEK':
                                        renk = Renkler.KIRMIZI
                                    elif kural['severity'] == 'ORTA':
                                        renk = Renkler.SARI
                                    else:
                                        renk = Renkler.YESIL
                                    
                                    print(f"{renk}🚨 [{kural['severity']}] {kural['name']}{Renkler.SIFIRLA}")
                                    print(f"   {satir.strip()}\n")
                                    
                                    self.bulunan_olaylar.append({
                                        'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        'dosya': os.path.basename(dosya_yolu),
                                        'satir_no': '-',
                                        'seviye': kural['severity'],
                                        'kural_adi': kural['name'],
                                        'mesaj': satir.strip()[:100]
                                    })
                                    break
                    else:
                        if beklemede:
                            print(f"{Renkler.SIYAN}⏳ Yeni satır bekliyor...{Renkler.SIFIRLA}", end='\r')
                        time.sleep(0.5)
                
                print(f"\n{Renkler.YESIL}✅ İzleme tamamlandı{Renkler.SIFIRLA}\n")
                
        except KeyboardInterrupt:
            print(f"\n{Renkler.SARI}⚠️  İzleme durdu{Renkler.SIFIRLA}\n")
        except FileNotFoundError:
            print(f"{Renkler.KIRMIZI}❌ Dosya bulunamadı: {dosya_yolu}{Renkler.SIFIRLA}\n")
        except Exception as e:
            print(f"{Renkler.KIRMIZI}❌ Hata: {e}{Renkler.SIFIRLA}\n")
    
    def rapor_olustur(self):
        if not self.bulunan_olaylar:
            print(f"\n{Renkler.SARI}⚠️  Rapor için hiç olay bulunamadı! Önce analiz yapın.{Renkler.SIFIRLA}\n")
            return
        
        os.makedirs('output', exist_ok=True)
        zaman_damgasi = datetime.now().strftime('%Y%m%d_%H%M%S')
        rapor_yolu = f'output/report_{zaman_damgasi}.csv'
        
        try:
            with open(rapor_yolu, 'w', newline='', encoding='utf-8-sig') as f:
                alanlar = ['zaman', 'dosya', 'satir_no', 'seviye', 'kural_adi', 'mesaj']
                yazar = csv.DictWriter(f, fieldnames=alanlar, delimiter=';')
                
                yazar.writeheader()
                yazar.writerows(self.bulunan_olaylar)
            
            print(f"\n{Renkler.YESIL}✅ Rapor oluşturuldu: {rapor_yolu}{Renkler.SIFIRLA}")
            print(f"{Renkler.SIYAN}📊 Toplam {len(self.bulunan_olaylar)} olay kaydedildi{Renkler.SIFIRLA}\n")
            
        except Exception as e:
            print(f"\n{Renkler.KIRMIZI}❌ Rapor oluşturulurken hata: {e}{Renkler.SIFIRLA}\n")
    
    def ozet_goster(self):
        if not self.bulunan_olaylar:
            print(f"\n{Renkler.SARI}⚠️  Henüz analiz yapılmadı!{Renkler.SIFIRLA}\n")
            return
        
        yuksek = sum(1 for o in self.bulunan_olaylar if o['seviye'] == 'YUKSEK')
        orta   = sum(1 for o in self.bulunan_olaylar if o['seviye'] == 'ORTA')
        dusuk  = sum(1 for o in self.bulunan_olaylar if o['seviye'] == 'DUSUK')
        
        print(f"\n{Renkler.KALIN}{Renkler.SIYAN}{'═' * 40}{Renkler.SIFIRLA}")
        print(f"{Renkler.KALIN}{Renkler.SIYAN}      📊 ANALİZ ÖZETİ{Renkler.SIFIRLA}")
        print(f"{Renkler.KALIN}{Renkler.SIYAN}{'═' * 40}{Renkler.SIFIRLA}")
        print(f"  {Renkler.KIRMIZI}🔴 YUKSEK  :  {yuksek} olay{Renkler.SIFIRLA}")
        print(f"  {Renkler.SARI}🟡 ORTA    :  {orta} olay{Renkler.SIFIRLA}")
        print(f"  {Renkler.YESIL}🟢 DUSUK   :  {dusuk} olay{Renkler.SIFIRLA}")
        print(f"  {Renkler.SIYAN}{'─' * 36}{Renkler.SIFIRLA}")
        print(f"  {Renkler.BEYAZ}📌 TOPLAM  :  {len(self.bulunan_olaylar)} olay{Renkler.SIFIRLA}")
        print(f"{Renkler.KALIN}{Renkler.SIYAN}{'═' * 40}{Renkler.SIFIRLA}\n")
    
    def temizle(self):
        """Bulunan olayları temizle"""
        self.bulunan_olaylar = []
        print(f"\n{Renkler.YESIL}🗑️  Kayıtlar temizlendi{Renkler.SIFIRLA}\n")

def ana_menu_goster():
    """Ana menüyü göster"""
    print(f"\n{Renkler.KALIN}{Renkler.SIYAN}{'═' * 50}{Renkler.SIFIRLA}")
    print(f"{Renkler.KALIN}{Renkler.MAGENTA}     🔍 CLI LOG ANALİZ VE UYARI ARACI 🔍{Renkler.SIFIRLA}")
    print(f"{Renkler.KALIN}{Renkler.SIYAN}{'═' * 50}{Renkler.SIFIRLA}")
    print(f"  {Renkler.YESIL}1.{Renkler.SIFIRLA}  Tüm Log Dosyalarını Analiz Et")
    print(f"  {Renkler.YESIL}2.{Renkler.SIFIRLA}  Belirli Bir Dosyayı Analiz Et")
    print(f"  {Renkler.YESIL}3.{Renkler.SIFIRLA}  Gerçek Zamanlı İzleme Başlat")
    print(f"  {Renkler.YESIL}4.{Renkler.SIFIRLA}  CSV Raporu Oluştur")
    print(f"  {Renkler.YESIL}5.{Renkler.SIFIRLA}  Analiz Özeti Göster")
    print(f"  {Renkler.YESIL}6.{Renkler.SIFIRLA}  Kayıtları Temizle")
    print(f"  {Renkler.KIRMIZI}7.{Renkler.SIFIRLA}  Çıkış")
    print(f"{Renkler.KALIN}{Renkler.SIYAN}{'═' * 50}{Renkler.SIFIRLA}")


def dosya_mensu_goster(log_dosyalari):
    print(f"\n{Renkler.SIYAN}{'─' * 35}{Renkler.SIFIRLA}")
    print(f"{Renkler.KALIN}  📂 Mevcut Log Dosyaları:{Renkler.SIFIRLA}")
    print(f"{Renkler.SIYAN}{'─' * 35}{Renkler.SIFIRLA}")
    for i, dosya in enumerate(log_dosyalari, 1):
        print(f"  {Renkler.YESIL}{i}.{Renkler.SIFIRLA} {dosya}")
    print(f"{Renkler.SIYAN}{'─' * 35}{Renkler.SIFIRLA}")

def main():
    """Ana program"""
    analizci = LogAnalyzer()
    
    log_dosyalari = [
        'logs/auth.log',
        'logs/syslog',
        'logs/nginx_access.log'
    ]
  
    print(f"\n{Renkler.KALIN}{Renkler.YESIL}  ✓ Sistem hazır!{Renkler.SIFIRLA}")
    print(f"{Renkler.SIYAN}  ✓ {len(analizci.kurallar)} kural yüklendu{Renkler.SIFIRLA}")
    print(f"{Renkler.SIYAN}  ✓ {len(log_dosyalari)} log dosyası tespit edildi{Renkler.SIFIRLA}")
    
    while True:
        ana_menu_goster()
        secim = input(f"{Renkler.KALIN}  Seçiminiz (1-7): {Renkler.SIFIRLA}").strip()
        
        if secim == '1':
            for dosya in log_dosyalari:
                analizci.dosya_analiz_et(dosya)
            analizci.ozet_goster()
            input(f"{Renkler.SARI}  Enter'a basın...{Renkler.SIFIRLA}")
            
        elif secim == '2':
            dosya_mensu_goster(log_dosyalari)
            dosya_secim = input(f"{Renkler.KALIN}  Dosya numarası: {Renkler.SIFIRLA}").strip()
            try:
                index = int(dosya_secim) - 1
                if 0 <= index < len(log_dosyalari):
                    analizci.dosya_analiz_et(log_dosyalari[index])
                else:
                    print(f"{Renkler.KIRMIZI}  ❌ Geçersiz numara!{Renkler.SIFIRLA}\n")
            except ValueError:
                print(f"{Renkler.KIRMIZI}  ❌ Lütfen sayı girin!{Renkler.SIFIRLA}\n")
            input(f"{Renkler.SARI}  Enter'a basın...{Renkler.SIFIRLA}")
            
        elif secim == '3':
            dosya_mensu_goster(log_dosyalari)
            dosya_secim = input(f"{Renkler.KALIN}  Dosya numarası: {Renkler.SIFIRLA}").strip()
            sure = input(f"{Renkler.KALIN}  Kaç saniye izlensin? (varsayılan 10): {Renkler.SIFIRLA}").strip()
            
            try:
                index = int(dosya_secim) - 1
                sure_int = int(sure) if sure else 10
                
                if 0 <= index < len(log_dosyalari):
                    analizci.gercek_zamanli_izle(log_dosyalari[index], sure_int)
                else:
                    print(f"{Renkler.KIRMIZI}  ❌ Geçersiz numara!{Renkler.SIFIRLA}\n")
            except ValueError:
                print(f"{Renkler.KIRMIZI}  ❌ Lütfen geçerli değerler girin!{Renkler.SIFIRSA}\n")
            input(f"{Renkler.SARI}  Enter'a basın...{Renkler.SIFIRLA}")
            
        elif secim == '4':
            analizci.rapor_olustur()
            input(f"{Renkler.SARI}  Enter'a basın...{Renkler.SIFIRLA}")
            
        elif secim == '5':
            analizci.ozet_goster()
            input(f"{Renkler.SARI}  Enter'a basın...{Renkler.SIFIRLA}")
            
        elif secim == '6':
            analizci.temizle()
            input(f"{Renkler.SARI}  Enter'a basın...{Renkler.SIFIRLA}")
            
        elif secim == '7':
            print(f"\n{Renkler.YESIL}{Renkler.KALIN}  👋 Görüşmek üzere!{Renkler.SIFIRLA}\n")
            break
            
        else:
            print(f"\n{Renkler.KIRMIZI}  ❌ Geçersiz seçim! 1-7 arası seçin.{Renkler.SIFIRLA}\n")
            input(f"{Renkler.SARI}  Enter'a basın...{Renkler.SIFIRLA}")


if __name__ == "__main__":
    main()