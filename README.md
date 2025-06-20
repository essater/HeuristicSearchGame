# 🧠 Sezgisel Kart Oyunu (AI Card Game)
 
Bu proje, **Artificial Intelligence III** dersi kapsamında geliştirilen, Python dilinde yazılmış sezgisel (heuristic) karar mekanizmasına sahip görsel bir kart oyunudur. Yapay zekâ, oyuncunun ve bilgisayarın kart seçimlerini olasılıklara ve durumsal verilere göre değerlendirerek hamle yapar.
 
## 🎮 Oyun Kuralları
 
- Oyuncu ve bilgisayara eşit sayıda kart dağıtılır (`Kolay` modda 3, `Zor` modda 6).
- Amaç, **aynı türden (suit) en az 3 veya 6 kartı** elde toplamaktır.
- Her turda hem oyuncuya hem de bilgisayara 1 yeni kart verilir.
- Oyuncu eski kartlarından birini veya yeni kartı atabilir.
- Bilgisayar, yapay zekâ algoritmasıyla en uygun kartı seçerek atar.
- Oyunculardan biri kazanma koşulunu sağlarsa oyun sona erer.
- Eğer kartlar biterse toplam puanlara göre kazanan belirlenir.
 
## 🧠 Yapay Zekâ ve Heuristik Yaklaşım
 
### Kolay Mod
- En çok tekrar eden suit'e (renge) odaklanır.
- Olasılık %33'ten düşükse en yüksek değerli kartı atar.
 
### Zor Mod
- El, deste ve rakipteki kart dağılımına göre **ağırlıklı skorlama** yapar.
- Karar verme süreci şunlara dayanır:
  - Elindeki suit sayısı
  - Destede o suit'ten kalan kart sayısı
  - Rakibin elindeki suit'ler
- Skoru en düşük olan suit’ten en büyük kartı atar.
 
## 🖼️ Görseller
 
- Kart görselleri `cards/` klasöründe bulunmalı.
- Kart isimleri `ace_of_spades.png`, `10_of_hearts.png` gibi isimlendirilmiş olmalı.
- Görseller `PIL.Image` ve `ImageTk` ile yüklenmektedir.
 
## 💻 Kurulum
 
1. Python 3.x yüklü olmalıdır.
2. Gerekli kütüphaneleri kur:
   ```bash
   pip install pillow
