"""
ÖRNEK ÇIKTI - TEKNOFEST Savaşan İHA Sistemi
============================================

Bu dosya, sistemin çalışırken ürettiği örnek konsol çıktılarını gösterir.
"""

# ============================================================================
# 1. SİSTEM BAŞLATMA ÇIKTISI
# ============================================================================

"""
============================================================
OTONOM İHA SİSTEMİ BAŞLATILIYOR
============================================================
2026-02-07 20:15:00 | INFO     | 📋 Konfigürasyon doğrulanıyor...
2026-02-07 20:15:00 | INFO     | ✅ Konfigürasyon doğrulandı
2026-02-07 20:15:00 | INFO     | 📷 Vision modülü başlatılıyor...
📦 YOLO modeli yükleniyor: models/yolov11.pt
🚀 TensorRT optimizasyonu uygulanıyor...
   ✅ Mevcut TensorRT engine kullanılıyor: models/yolov11.engine
✅ Model yükleme tamamlandı
📷 USB kamera başlatılıyor (ID: 0)...
✅ Kamera başarıyla başlatıldı
✅ VisionProcessor başlatıldı
▶️  Görüntü işleme başlatıldı
2026-02-07 20:15:05 | INFO     | 🧭 Navigation modülü başlatılıyor...
✅ ObstacleAvoidance başlatıldı
2026-02-07 20:15:05 | INFO     | 🎯 TEKNOFEST modülleri başlatılıyor...
✅ TargetTracker başlatıldı
✅ WaypointNavigator başlatıldı
✅ HybridNavigator başlatıldı
2026-02-07 20:15:05 | INFO     | 📡 Communication modülü başlatılıyor...
🔌 MAVLink bağlantısı kuruluyor: /dev/ttyACM0
✅ MAVLink bağlantısı başarılı
▶️  Telemetri güncellemeleri başlatıldı
2026-02-07 20:15:06 | INFO     | 🖥️  GUI modülü başlatılıyor...
✅ GroundControlStation başlatıldı
2026-02-07 20:15:06 | INFO     | ✅ Tüm modüller başarıyla başlatıldı
2026-02-07 20:15:06 | INFO     | ▶️  Ana sistem döngüsü başlatıldı
2026-02-07 20:15:06 | INFO     |    Döngü frekansı: 20 Hz
"""

# ============================================================================
# 2. NORMAL ARAMA MODU (SEARCH) - Waypoint Takibi
# ============================================================================

"""
[GUI Açıldı - Kullanıcı "▶️ Otonom Modu Başlat" butonuna bastı]

2026-02-07 20:16:10 | INFO     | ▶️  Otonom mod başlatıldı
2026-02-07 20:16:10 | INFO     | 🔍 ARAMA - WP1/5 (245.3m) | Kaynak: waypoint
2026-02-07 20:16:11 | INFO     | 🔍 ARAMA - WP1/5 (238.7m) | Kaynak: waypoint
2026-02-07 20:16:12 | INFO     | 🔍 ARAMA - WP1/5 (231.2m) | Kaynak: waypoint

[Kamera görüntüsünde tespitler:]
- person (0.92 güven, 15.3m mesafe)
- car (0.87 güven, 25.8m mesafe)
- chair (0.78 güven, 8.2m mesafe)

2026-02-07 20:16:13 | INFO     | 🔍 ARAMA - WP1/5 (223.5m) | Kaynak: waypoint
"""

# ============================================================================
# 3. HEDEF İHA TESPİT EDİLDİ - TRACK Moduna Geçiş
# ============================================================================

"""
[Kamera görüntüsünde İHA tespit edildi!]
- uav (0.95 güven, 35.2m mesafe, merkez: (450, 280))

2026-02-07 20:16:45 | INFO     | 🔄 Mod Değişimi: SEARCH → TRACK
2026-02-07 20:16:45 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 35.2m | Kaynak: tracking
2026-02-07 20:16:46 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 33.8m | Kaynak: tracking
2026-02-07 20:16:47 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 31.5m | Kaynak: tracking

[PID Kontrolcü Çalışıyor:]
- Frame merkezi: (320, 240)
- Hedef pozisyonu: (450, 280)
- Hata X: -130 piksel → Yaw komutu: +0.35 rad/s (Sağa dön)
- Hata Y: -40 piksel → Pitch komutu: +0.12 rad/s (Yukarı bak)

2026-02-07 20:16:48 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 29.2m | Kaynak: tracking
2026-02-07 20:16:49 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 26.8m | Kaynak: tracking
2026-02-07 20:16:50 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 24.3m | Kaynak: tracking

[Hedef frame merkezine yaklaştı:]
- Hedef pozisyonu: (335, 245) → Merkeze çok yakın!
- Hata X: -15 piksel → Yaw komutu: +0.05 rad/s
- Hata Y: -5 piksel → Pitch komutu: +0.02 rad/s

2026-02-07 20:16:51 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 22.1m | Kaynak: tracking
"""

# ============================================================================
# 4. SALDIRI MODU (ATTACK) - Hedef Yakın
# ============================================================================

"""
[Hedef mesafesi 20m'nin altına düştü]

2026-02-07 20:17:05 | INFO     | 🔄 Mod Değişimi: TRACK → ATTACK
2026-02-07 20:17:05 | INFO     | ⚔️ SALDIRI MODU - Mesafe: 18.5m | Kaynak: tracking
2026-02-07 20:17:06 | INFO     | ⚔️ SALDIRI MODU - Mesafe: 16.2m | Kaynak: tracking
2026-02-07 20:17:07 | INFO     | ⚔️ SALDIRI MODU - Mesafe: 14.8m | Kaynak: tracking

[Hız azaltıldı, hassas takip]
- Speed factor: 0.5 (Yavaş yaklaşma)
- Hedef pozisyonu: (318, 238) → Mükemmel merkezleme!
"""

# ============================================================================
# 5. ENGEL TESPİT EDİLDİ - Hibrit Navigasyon
# ============================================================================

"""
[Takip sırasında engel tespit edildi]
- person (0.88 güven, 12.3m mesafe, sol tarafta)

2026-02-07 20:17:20 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 25.7m | Kaynak: obstacle_avoidance + tracking

[Vektör Birleştirme:]
- Hedef yönü: 45° (Hedefi takip et)
- Engel kaçış yönü: 65° (Sağa kaç)
- Birleştirilmiş yön: 52° (Ağırlıklı ortalama: %40 engel, %60 hedef)
- Speed factor: 0.7 (Orta hız)

2026-02-07 20:17:21 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 24.2m | Kaynak: obstacle_avoidance + tracking
2026-02-07 20:17:22 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 23.8m | Kaynak: tracking

[Engel geçildi, normal takip devam ediyor]
"""

# ============================================================================
# 6. KRİTİK ENGEL - ACİL KAÇIŞ MODU (EMERGENCY)
# ============================================================================

"""
[Çok yakın engel tespit edildi!]
- person (0.95 güven, 1.5m mesafe, önde!)

2026-02-07 20:18:30 | INFO     | 🔄 Mod Değişimi: TRACK → EMERGENCY
2026-02-07 20:18:30 | WARNING  | 🚨 ACİL KAÇIŞ MODU AKTİF
2026-02-07 20:18:30 | INFO     | 🚨 ACİL KAÇIŞ MODU - Engel: 1.5m | Kaynak: obstacle_avoidance
2026-02-07 20:18:31 | WARNING  | 🚨 ACİL KAÇIŞ MODU AKTİF
2026-02-07 20:18:31 | INFO     | 🚨 ACİL KAÇIŞ MODU - Engel: 2.1m | Kaynak: obstacle_avoidance

[Maksimum kaçış manevrası:]
- Hedef takip: ASKIYA ALINDI
- Waypoint takip: ASKIYA ALINDI
- Engel kaçış: %100 öncelik
- Sapma açısı: 45° (Maksimum)
- Speed factor: 0.3 (Yavaşla)

2026-02-07 20:18:32 | INFO     | 🚨 ACİL KAÇIŞ MODU - Engel: 3.8m | Kaynak: obstacle_avoidance
2026-02-07 20:18:33 | INFO     | 🚨 ACİL KAÇIŞ MODU - Engel: 5.2m | Kaynak: obstacle_avoidance

[Engel geçildi, önceki moda dönülüyor]

2026-02-07 20:18:34 | INFO     | 🔄 Mod Değişimi: EMERGENCY → TRACK
2026-02-07 20:18:34 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 28.3m | Kaynak: tracking
"""

# ============================================================================
# 7. HEDEF KAYBEDİLDİ - SEARCH Moduna Dönüş
# ============================================================================

"""
[Hedef kamera görüş alanından çıktı]

2026-02-07 20:19:15 | INFO     | ⚠️  Hedef kaybedildi
2026-02-07 20:19:15 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 0.0m | Kaynak: tracking

[Kalman filtresi ile tahmin devam ediyor - 3 saniye]
- Tahmini pozisyon: (520, 260)
- Tahmini hız: (15 px/s, 5 px/s)

2026-02-07 20:19:16 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 0.0m | Kaynak: tracking
2026-02-07 20:19:17 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 0.0m | Kaynak: tracking
2026-02-07 20:19:18 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 0.0m | Kaynak: tracking

[3 saniye doldu, hedef tamamen kaybedildi]

2026-02-07 20:19:18 | INFO     | 🔄 Mod Değişimi: TRACK → SEARCH
2026-02-07 20:19:18 | INFO     | 🔍 ARAMA - WP2/5 (156.8m) | Kaynak: waypoint
2026-02-07 20:19:19 | INFO     | 🔍 ARAMA - WP2/5 (149.2m) | Kaynak: waypoint
"""

# ============================================================================
# 8. WAYPOINT'E ULAŞILDI - Loiter Modu
# ============================================================================

"""
2026-02-07 20:20:45 | INFO     | 🔍 ARAMA - WP2/5 (8.3m) | Kaynak: waypoint
2026-02-07 20:20:46 | INFO     | 🔍 ARAMA - WP2/5 (4.2m) | Kaynak: waypoint
2026-02-07 20:20:47 | INFO     | ✅ Waypoint 2 ulaşıldı: Arama Noktası 1
2026-02-07 20:20:47 | INFO     | ⏳ Loiter: 0.5/10.0s
2026-02-07 20:20:48 | INFO     | ⏳ Loiter: 1.5/10.0s
2026-02-07 20:20:49 | INFO     | ⏳ Loiter: 2.5/10.0s
...
2026-02-07 20:20:57 | INFO     | ⏳ Loiter: 9.8/10.0s
2026-02-07 20:20:58 | INFO     | ➡️  Sonraki waypoint: WP3 - Arama Noktası 2
2026-02-07 20:20:58 | INFO     | 🔍 ARAMA - WP3/5 (112.5m) | Kaynak: waypoint
"""

# ============================================================================
# 9. BATARYA DÜŞÜK - RETURN Modu
# ============================================================================

"""
[Batarya seviyesi %20'nin altına düştü]

2026-02-07 20:25:30 | INFO     | 🔄 Mod Değişimi: SEARCH → RETURN
2026-02-07 20:25:30 | INFO     | 🏠 DÖNÜŞ - Üsse: 245.8m | Kaynak: waypoint
2026-02-07 20:25:31 | INFO     | 🏠 DÖNÜŞ - Üsse: 238.3m | Kaynak: waypoint

[Dönüş sırasında engel tespit edildi]
- tree (0.82 güven, 18.5m mesafe)

2026-02-07 20:25:35 | INFO     | 🏠 DÖNÜŞ - Üsse: 215.7m | Kaynak: obstacle_avoidance + waypoint

[Vektör Birleştirme:]
- Üs yönü: 180° (Güneye dön)
- Engel kaçış yönü: 195° (Hafif sağa kaç)
- Birleştirilmiş yön: 186° (Ağırlıklı: %60 waypoint, %40 engel)

2026-02-07 20:25:36 | INFO     | 🏠 DÖNÜŞ - Üsse: 208.2m | Kaynak: waypoint
...
2026-02-07 20:26:45 | INFO     | 🏠 DÖNÜŞ - Üsse: 3.8m | Kaynak: waypoint
2026-02-07 20:26:46 | INFO     | ✅ Waypoint 5 ulaşıldı: Dönüş - İniş
2026-02-07 20:26:46 | INFO     | 🏁 Tüm waypoint'ler tamamlandı
2026-02-07 20:26:46 | INFO     | 🏁 Görev tamamlandı!
"""

# ============================================================================
# 10. PERFORMANS METRİKLERİ
# ============================================================================

"""
[Sistem çalışırken periyodik metrikler]

2026-02-07 20:27:00 | INFO     | 📊 Performans Metrikleri:
   - FPS: 24.3
   - Tespit sayısı: 3
   - Hedef takip aktif: Evet
   - Mod: TRACK
   - Batarya: 45%
   - GPS Fix: 3D
   - Heading: 125.3°
   - Altitude: 58.2m
"""

# ============================================================================
# 11. GUI KONSOLU - Kontrol Tab'ı
# ============================================================================

"""
[GUI'deki "Kontrol" tab'ında görünen loglar:]

▶️  Otonom mod başlatıldı
🔍 ARAMA - WP1/5 (245.3m)
🔍 ARAMA - WP1/5 (231.2m)
🔄 Mod Değişimi: SEARCH → TRACK
🎯 HEDEF TAKİP - Mesafe: 35.2m
🎯 HEDEF TAKİP - Mesafe: 29.2m
🔄 Mod Değişimi: TRACK → ATTACK
⚔️ SALDIRI MODU - Mesafe: 18.5m
🚨 ACİL KAÇIŞ MODU - Engel: 1.5m
🚨 ACİL KAÇIŞ MODU AKTİF
🔄 Mod Değişimi: EMERGENCY → TRACK
⚠️  Hedef kaybedildi
🔄 Mod Değişimi: TRACK → SEARCH
✅ Waypoint 2 ulaşıldı: Arama Noktası 1
⏳ Loiter: 5.2/10.0s
➡️  Sonraki waypoint: WP3
🔄 Mod Değişimi: SEARCH → RETURN
🏠 DÖNÜŞ - Üsse: 245.8m
🏁 Görev tamamlandı!
⏹️  Otonom mod durduruldu
"""

# ============================================================================
# 12. VISION MODÜLÜ - Tespit Detayları
# ============================================================================

"""
[vision.py tarafından döndürülen tespit verileri]

Tespit Listesi (detections):
[
    {
        'bbox': [120, 80, 180, 150],
        'confidence': 0.92,
        'class_id': 0,
        'class_name': 'person',
        'center': (150, 115),
        'distance': 15.3
    },
    {
        'bbox': [450, 230, 550, 330],
        'confidence': 0.95,
        'class_id': 2,
        'class_name': 'uav',  # ← HEDEF İHA!
        'center': (500, 280),
        'distance': 35.2
    },
    {
        'bbox': [200, 300, 280, 380],
        'confidence': 0.87,
        'class_id': 2,
        'class_name': 'car',
        'center': (240, 340),
        'distance': 25.8
    }
]

[target_tracker.py bu listeden İHA'yı filtreler:]
- class_id == 2 (TARGET_CLASS_ID)
- confidence >= 0.7 (MIN_CONFIDENCE)
→ Hedef bulundu: uav (0.95, 35.2m)
"""

# ============================================================================
# 13. HATA DURUMU - Düşük FPS Uyarısı
# ============================================================================

"""
2026-02-07 20:28:15 | WARNING  | ⚠️  Düşük FPS: 8.3
2026-02-07 20:28:16 | WARNING  | ⚠️  Düşük FPS: 7.9
2026-02-07 20:28:17 | INFO     | 🔍 ARAMA - WP3/5 (98.5m) | Kaynak: waypoint
2026-02-07 20:28:18 | WARNING  | ⚠️  Düşük FPS: 9.2

[Çözüm: Çözünürlüğü düşürün veya TensorRT optimizasyonunu kontrol edin]
"""

# ============================================================================
# 14. SİSTEM KAPATMA
# ============================================================================

"""
[Kullanıcı "⏹️ Otonom Modu Durdur" butonuna bastı]

2026-02-07 20:30:00 | INFO     | ⏹️  Otonom mod durduruldu
2026-02-07 20:30:00 | INFO     | 🔌 Sistem kapatılıyor...
2026-02-07 20:30:00 | INFO     | ⏹️  Görüntü işleme durduruldu
2026-02-07 20:30:00 | INFO     | 🔌 VisionProcessor kaynakları serbest bırakıldı
2026-02-07 20:30:00 | INFO     | 🔌 MAVLink bağlantısı kapatıldı
2026-02-07 20:30:00 | INFO     | ✅ Sistem güvenli şekilde kapatıldı
"""
