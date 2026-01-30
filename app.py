import os
import csv
import yaml
import time
from datetime import datetime

class LogAnalyzer:
    def __init__(self):
        self.kurallar = self.kurallari_yukle()
        self.bulunan_olaylar = []
        
    def kurallari_yukle(self):
        """YAML dosyasından kuralları yükle"""
        try:
            with open('rules.yaml', 'r', encoding='utf-8') as f:
                veri = yaml.safe_load(f)
                return veri['rules']
        except Exception as e:
            print(f"Kural dosyası yüklenirken hata: {e}")
            return []
    
    def dosya_analiz_et(self, dosya_yolu):
        """Belirtilen log dosyasını analiz et"""
        print(f"\n📁 {dosya_yolu} dosyası analiz ediliyor...")
        
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                satirlar = f.readlines()
                
            toplam_eslesme = 0
            
            for satir_no, satir in enumerate(satirlar, 1):
                for kural in self.kurallar:
                    for kelime in kural['keywords']:
                        if kelime in satir:
                            toplam_eslesme += 1
                            # Mesajı kısalt (ilk 150 karakter)
                            mesaj_kisa = satir.strip()[:150] + '...' if len(satir.strip()) > 150 else satir.strip()
                            
                            self.bulunan_olaylar.append({
                                'zaman': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'dosya': os.path.basename(dosya_yolu),
                                'satir_no': satir_no,
                                'seviye': kural['severity'],
                                'kural_adi': kural['name'],
                                'mesaj': mesaj_kisa
                            })
                            print(f"  ⚠️  [{kural['severity']}] {kural['name']} - Satır {satir_no}")
                            break
            
            print(f"✅ Toplam {toplam_eslesme} eşleşme bulundu\n")
            
        except FileNotFoundError:
            print(f"❌ Dosya bulunamadı: {dosya_yolu}\n")
        except Exception as e:
            print(f"❌ Hata oluştu: {e}\n")
    
    def gercek_zamanli_izle(self, dosya_yolu, sure=10):
        """Log dosyasını gerçek zamanlı izle (tail -f benzeri)"""
        print(f"\n🔴 Gerçek zamanlı izleme başlatıldı: {dosya_yolu}")
        print(f"⏱️  {sure} saniye boyunca izlenecek...\n")
        
        try:
            # Dosyanın sonuna git
            with open(dosya_yolu, 'r') as f:
                f.seek(0, 2)  # Dosya sonuna git
                
                baslangic = time.time()
                
                while (time.time() - baslangic) < sure:
                    satir = f.readline()
                    
                    if satir:
                        # Yeni satır geldi, kontrol et
                        for kural in self.kurallar:
                            for kelime in kural['keywords']:
                                if kelime in satir:
                                    print(f"🚨 [{kural['severity']}] {kural['name']}")
                                    print(f"   {satir.strip()}\n")
                                    break
                    else:
                        time.sleep(0.5)  # Yarım saniye bekle
                
                print("✅ İzleme tamamlandı\n")
                
        except FileNotFoundError:
            print(f"❌ Dosya bulunamadı: {dosya_yolu}\n")
        except Exception as e:
            print(f"❌ Hata: {e}\n")
    
    def rapor_olustur(self):
        """CSV raporu oluştur"""
        if not self.bulunan_olaylar:
            print("⚠️  Rapor için hiç olay bulunamadı!\n")
            return
        
        os.makedirs('output', exist_ok=True)
        rapor_yolu = 'output/report.csv'
        
        try:
            with open(rapor_yolu, 'w', newline='', encoding='utf-8-sig') as f:
                alanlar = ['zaman', 'dosya', 'satir_no', 'seviye', 'kural_adi', 'mesaj']
                yazar = csv.DictWriter(f, fieldnames=alanlar, delimiter=';')
                
                yazar.writeheader()
                yazar.writerows(self.bulunan_olaylar)
            
            print(f"✅ Rapor oluşturuldu: {rapor_yolu}")
            print(f"📊 Toplam {len(self.bulunan_olaylar)} olay kaydedildi\n")
            
        except Exception as e:
            print(f"❌ Rapor oluşturulurken hata: {e}\n")
    
    def temizle(self):
        """Bulunan olayları temizle"""
        self.bulunan_olaylar = []
        print("🗑️  Kayıtlar temizlendi\n")


def menu_goster():
    """Ana menüyü göster"""
    print("=" * 50)
    print("     🔍 CLI LOG ANALİZ VE UYARI ARACI 🔍")
    print("=" * 50)
    print("1. Tüm Log Dosyalarını Analiz Et")
    print("2. Belirli Bir Dosyayı Analiz Et")
    print("3. Gerçek Zamanlı İzleme Başlat")
    print("4. CSV Raporu Oluştur")
    print("5. Kayıtları Temizle")
    print("6. Çıkış")
    print("=" * 50)


def main():
    """Ana program"""
    analizci = LogAnalyzer()
    
    log_dosyalari = [
        'logs/auth.log',
        'logs/syslog',
        'logs/nginx_access.log'
    ]
    
    while True:
        menu_goster()
        secim = input("Seçiminiz (1-6): ").strip()
        
        if secim == '1':
            # Tüm dosyaları analiz et
            for dosya in log_dosyalari:
                analizci.dosya_analiz_et(dosya)
            input("Devam etmek için Enter'a basın...")
            
        elif secim == '2':
            # Belirli dosya analizi
            print("\nMevcut dosyalar:")
            for i, dosya in enumerate(log_dosyalari, 1):
                print(f"{i}. {dosya}")
            
            dosya_secim = input("Dosya numarası: ").strip()
            try:
                index = int(dosya_secim) - 1
                if 0 <= index < len(log_dosyalari):
                    analizci.dosya_analiz_et(log_dosyalari[index])
                else:
                    print("❌ Geçersiz numara!\n")
            except ValueError:
                print("❌ Lütfen sayı girin!\n")
            
            input("Devam etmek için Enter'a basın...")
            
        elif secim == '3':
            # Gerçek zamanlı izleme
            print("\nMevcut dosyalar:")
            for i, dosya in enumerate(log_dosyalari, 1):
                print(f"{i}. {dosya}")
            
            dosya_secim = input("Dosya numarası: ").strip()
            sure = input("Kaç saniye izlensin? (varsayılan 10): ").strip()
            
            try:
                index = int(dosya_secim) - 1
                sure_int = int(sure) if sure else 10
                
                if 0 <= index < len(log_dosyalari):
                    analizci.gercek_zamanli_izle(log_dosyalari[index], sure_int)
                else:
                    print("❌ Geçersiz numara!\n")
            except ValueError:
                print("❌ Lütfen geçerli değerler girin!\n")
            
            input("Devam etmek için Enter'a basın...")
            
        elif secim == '4':
            # Rapor oluştur
            analizci.rapor_olustur()
            input("Devam etmek için Enter'a basın...")
            
        elif secim == '5':
            # Temizle
            analizci.temizle()
            input("Devam etmek için Enter'a basın...")
            
        elif secim == '6':
            # Çıkış
            print("\n👋 Görüşmek üzere!\n")
            break
            
        else:
            print("\n❌ Geçersiz seçim! Lütfen 1-6 arası seçin.\n")
            input("Devam etmek için Enter'a basın...")


if __name__ == "__main__":
    main()