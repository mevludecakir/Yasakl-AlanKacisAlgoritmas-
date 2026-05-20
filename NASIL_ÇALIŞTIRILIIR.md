# 🚁 Otonom İHA Sistemi - Nasıl Çalıştırılır?

**TEKNOFEST Savaşan İHA Yarışması** için geliştirilmiş kapsamlı kılavuz.

---

## 📋 Hızlı Başlangıç

### Adım 1: Kurulum Kontrolü

```bash
cd iha_gorevim
python3 -c "import torch, cv2, PyQt5; print('✅ Tüm paketler yüklü')"
```

### Adım 2: Model Kontrolü

```bash
ls models/yolov11.pt
# Dosya varsa ✅, yoksa modeli indirin
```

### Adım 3: Konfigürasyon (ÖNEMLİ!)

`config.py` dosyasını düzenleyin:

```python
# 1. Hedef İHA sınıf ID'sini ayarlayın
class TargetTrackingConfig:
    TARGET_CLASS_ID = 2  # YOLO modelinizdeki İHA sınıfının ID'si!

# 2. Üs konumunu ayarlayın
class MissionConfig:
    HOME_LAT = 39.123000  # Gerçek koordinatlarınız
    HOME_LON = 35.456000
    HOME_ALT = 0.0
```

### Adım 4: Sistemi Başlatın

```bash
python3 main.py
```

---

## 🎯 Beklenen Çıktılar

### 1. Konsol Çıktısı - Sistem Başlatma

```
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
✅ MAVLink bağlantısı başarılı
2026-02-07 20:15:06 | INFO     | 🖥️  GUI modülü başlatılıyor...
✅ GroundControlStation başlatıldı
2026-02-07 20:15:06 | INFO     | ✅ Tüm modüller başarıyla başlatıldı
2026-02-07 20:15:06 | INFO     | ▶️  Ana sistem döngüsü başlatıldı
```

**✅ Başarılı:** Tüm modüller "✅" işaretiyle başladıysa sistem hazır!

---

## 🖥️ GUI Arayüzü

### Ana Pencere Açıldı

GUI 3 tab içerir:

#### Tab 1: 📹 Video & Tespit

```
┌─────────────────────────────────────────────────────────┐
│  [Canlı Kamera Görüntüsü]                               │
│                                                          │
│  ┌──────────────┐                                       │
│  │ person 0.92  │  ← Tespit edilen nesne (yeşil kutu)  │
│  │   15.3m      │                                       │
│  └──────────────┘                                       │
│                                                          │
│                    ┌──────────────┐                     │
│                    │ uav 0.95     │  ← HEDEF İHA!       │
│                    │   35.2m      │     (kırmızı kutu)  │
│                    └──────────────┘                     │
│                                                          │
│  FPS: 24.3 | Tespit: 2 | En Yakın: 15.3m (person)      │
└─────────────────────────────────────────────────────────┘
```

**Renk Kodları:**
- 🟢 Yeşil Kutu: Normal nesneler
- 🔴 Kırmızı Kutu: Hedef İHA (TARGET_CLASS_ID)

#### Tab 2: 📡 Telemetri

```
┌─ GPS Bilgileri ─────────────────────────────────────────┐
│  Enlem:     39.123456                                    │
│  Boylam:    35.654321                                    │
│  İrtifa:    58.2 m                                       │
│  Fix:       3 (GPS Kilitli)                              │
└──────────────────────────────────────────────────────────┘

┌─ Attitude Bilgileri ────────────────────────────────────┐
│  Roll:      2.3°                                         │
│  Pitch:    -1.5°                                         │
│  Yaw:      45.2°                                         │
│  Heading:  45.2° (KD)                                    │
└──────────────────────────────────────────────────────────┘

┌─ Sistem Durumu ─────────────────────────────────────────┐
│  Mod:       TRACK  🎯 (Hedef takip modu)                │
│  Armed:     ✅ Evet                                      │
│  Hız:       5.2 m/s                                      │
│  Batarya:   12.6V (85%)                                  │
│  ████████████████░░░░ 85%                                │
└──────────────────────────────────────────────────────────┘
```

**Uçuş Modları:**
- 🔍 SEARCH - Arama modu (waypoint takibi)
- 🎯 TRACK - Hedef takip modu
- ⚔️ ATTACK - Saldırı modu (hedef yakın)
- 🏠 RETURN - Dönüş modu (batarya düşük)
- 🚨 EMERGENCY - Acil kaçış modu

#### Tab 3: 🎮 Kontrol

```
┌─ Otonom Mod Kontrolü ───────────────────────────────────┐
│  [▶️ Otonom Modu Başlat]  (Yeşil buton)                 │
│  [⏹️ Otonom Modu Durdur]  (Kırmızı buton - pasif)       │
└──────────────────────────────────────────────────────────┘

┌─ Acil Durum ────────────────────────────────────────────┐
│  [🚨 ACİL DURDUR]  (Turuncu buton - her zaman aktif)   │
└──────────────────────────────────────────────────────────┘

┌─ Sistem Logları ────────────────────────────────────────┐
│  ▶️  Otonom mod başlatıldı                              │
│  🔍 ARAMA - WP1/5 (245.3m)                              │
│  🔄 Mod Değişimi: SEARCH → TRACK                        │
│  🎯 HEDEF TAKİP - Mesafe: 35.2m                         │
│  ⚔️ SALDIRI MODU - Mesafe: 18.5m                        │
│  🚨 ACİL KAÇIŞ MODU - Engel: 1.5m                       │
│  🏠 DÖNÜŞ - Üsse: 245.8m                                │
│  🏁 Görev tamamlandı!                                   │
└──────────────────────────────────────────────────────────┘
```

---

## 🎮 Otonom Mod Kullanımı

### 1. Görev Dosyası Hazırlama (Opsiyonel)

`missions/my_mission.json` oluşturun:

```json
{
  "mission_name": "Test Uçuşu",
  "waypoints": [
    {
      "lat": 39.123000,
      "lon": 35.456000,
      "alt": 50.0,
      "name": "Kalkış",
      "loiter_time": 0.0
    },
    {
      "lat": 39.124000,
      "lon": 35.457000,
      "alt": 60.0,
      "name": "Arama Noktası 1",
      "loiter_time": 10.0
    },
    {
      "lat": 39.123000,
      "lon": 35.456000,
      "alt": 50.0,
      "name": "Dönüş",
      "loiter_time": 0.0
    }
  ]
}
```

### 2. Otonom Modu Başlatma

1. GUI'de **"Kontrol"** tab'ına gidin
2. **"▶️ Otonom Modu Başlat"** butonuna tıklayın
3. Sistem otomatik olarak çalışmaya başlar

### 3. Beklenen Davranışlar

#### Senaryo 1: Normal Arama (SEARCH Modu)

```
[Konsol]
2026-02-07 20:16:10 | INFO     | ▶️  Otonom mod başlatıldı
2026-02-07 20:16:10 | INFO     | 🔍 ARAMA - WP1/5 (245.3m) | Kaynak: waypoint
2026-02-07 20:16:11 | INFO     | 🔍 ARAMA - WP1/5 (238.7m) | Kaynak: waypoint

[GUI - Video Tab]
- Kamera görüntüsü akıyor
- Tespitler yeşil kutularla gösteriliyor
- FPS: ~20-30

[GUI - Telemetri Tab]
- Mod: SEARCH 🔍
- İHA waypoint'e doğru ilerliyor
```

#### Senaryo 2: Hedef Tespit Edildi (TRACK Modu)

```
[Konsol]
2026-02-07 20:16:45 | INFO     | 🔄 Mod Değişimi: SEARCH → TRACK
2026-02-07 20:16:45 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 35.2m | Kaynak: tracking
2026-02-07 20:16:46 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 33.8m | Kaynak: tracking

[GUI - Video Tab]
- Hedef İHA KIRMIZI kutu ile gösteriliyor
- Frame merkezine doğru hareket ediyor

[GUI - Telemetri Tab]
- Mod: TRACK 🎯
- İHA hedefi takip ediyor

[GUI - Kontrol Tab Logları]
🔄 Mod Değişimi: SEARCH → TRACK
🎯 HEDEF TAKİP - Mesafe: 35.2m
```

#### Senaryo 3: Saldırı Mesafesi (ATTACK Modu)

```
[Konsol]
2026-02-07 20:17:05 | INFO     | 🔄 Mod Değişimi: TRACK → ATTACK
2026-02-07 20:17:05 | INFO     | ⚔️ SALDIRI MODU - Mesafe: 18.5m | Kaynak: tracking

[GUI - Telemetri Tab]
- Mod: ATTACK ⚔️
- Hız azaltıldı (hassas yaklaşma)
```

#### Senaryo 4: Kritik Engel (EMERGENCY Modu)

```
[Konsol]
2026-02-07 20:18:30 | INFO     | 🔄 Mod Değişimi: TRACK → EMERGENCY
2026-02-07 20:18:30 | WARNING  | 🚨 ACİL KAÇIŞ MODU AKTİF
2026-02-07 20:18:30 | INFO     | 🚨 ACİL KAÇIŞ MODU - Engel: 1.5m | Kaynak: obstacle_avoidance

[GUI - Telemetri Tab]
- Mod: EMERGENCY 🚨
- Maksimum kaçış manevrası
- Hedef takip askıya alındı
```

#### Senaryo 5: Batarya Düşük (RETURN Modu)

```
[Konsol]
2026-02-07 20:25:30 | INFO     | 🔄 Mod Değişimi: SEARCH → RETURN
2026-02-07 20:25:30 | INFO     | 🏠 DÖNÜŞ - Üsse: 245.8m | Kaynak: waypoint

[GUI - Telemetri Tab]
- Mod: RETURN 🏠
- Batarya: 18% (Düşük!)
- Üs waypoint'ine dönüyor
```

---

## 🔧 Sorun Giderme

### Sorun 1: Hedef Tespit Edilmiyor

**Belirti:**
```
[Konsol]
🔍 ARAMA - WP1/5 (...)
🔍 ARAMA - WP1/5 (...)
# Hiç TRACK moduna geçmiyor
```

**Çözüm:**
1. `config.py` → `TARGET_CLASS_ID` doğru mu?
2. YOLO modeliniz İHA sınıfını destekliyor mu?
3. `MIN_CONFIDENCE` değerini düşürün (örn. 0.5)

```python
class TargetTrackingConfig:
    TARGET_CLASS_ID = 2  # Modelinize göre değiştirin!
    MIN_CONFIDENCE = 0.5  # Daha düşük eşik
```

### Sorun 2: Waypoint'e Ulaşılamıyor

**Belirti:**
```
[Konsol]
🔍 ARAMA - WP1/5 (5.2m)
🔍 ARAMA - WP1/5 (4.8m)
🔍 ARAMA - WP1/5 (5.1m)
# Waypoint'e ulaşıldı mesajı gelmiyor
```

**Çözüm:**
```python
# config.py
class WaypointConfig:
    WAYPOINT_RADIUS = 10.0  # Daha büyük yarıçap
    ALTITUDE_TOLERANCE = 5.0  # Daha büyük tolerans
```

### Sorun 3: FPS Çok Düşük

**Belirti:**
```
[Konsol]
2026-02-07 20:28:15 | WARNING  | ⚠️  Düşük FPS: 8.3
```

**Çözüm:**
1. Çözünürlüğü düşürün:
```python
class CameraConfig:
    FRAME_WIDTH = 416  # 640'tan düşürün
    FRAME_HEIGHT = 416  # 480'den düşürün
```

2. TensorRT kullandığınızdan emin olun:
```python
class YOLOConfig:
    USE_TENSORRT = True
```

### Sorun 4: MAVLink Bağlantı Hatası

**Belirti:**
```
[Konsol]
⚠️  MAVLink bağlantısı kurulamadı
```

**Çözüm:**
```bash
# Port'u kontrol et
ls /dev/ttyACM*

# İzinleri düzenle
sudo chmod 666 /dev/ttyACM0

# config.py'de doğru port'u ayarla
class MAVLinkConfig:
    CONNECTION_STRING = "/dev/ttyACM0"  # Doğru port
```

---

## 📊 Performans Beklentileri

| Metrik | Beklenen | Jetson Nano |
|--------|----------|-------------|
| FPS | > 20 | 20-30 |
| Tespit Gecikmesi | < 50ms | ~30ms |
| Mod Geçiş Süresi | < 100ms | ~50ms |
| Waypoint Hassasiyeti | ±5m | GPS'e bağlı |

---

## 📝 Log Dosyaları

Sistem logları `logs/` dizininde:

```bash
# Son logları görüntüle
tail -f logs/uav_system_2026-02-07.log

# Hata loglarını filtrele
grep "ERROR" logs/uav_system_2026-02-07.log

# Mod geçişlerini görüntüle
grep "Mod Değişimi" logs/uav_system_2026-02-07.log
```

---

## 🎓 Önemli Hatırlatmalar

1. **Hedef Sınıf ID**: Mutlaka YOLO modelinize göre ayarlayın!
2. **GPS Koordinatları**: Gerçek konumunuzu kullanın
3. **İlk Test**: Simülasyon modunda yapın
4. **Güvenlik**: Acil durdur butonunu test edin
5. **Batarya**: %20'nin altında otomatik dönüş

---

## 📚 Ek Kaynaklar

- **Detaylı Kılavuz**: `TEKNOFEST_KILAVUZ.md`
- **Örnek Çıktılar**: `ORNEK_CIKTILAR.py`
- **Hızlı Başlangıç**: `QUICKSTART.md`
- **Teknik Detaylar**: `README.md`

---

**İyi uçuşlar! 🚁**
