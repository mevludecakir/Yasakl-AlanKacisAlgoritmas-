# Otonom İHA Engelden Kaçış ve Karar Destek Sistemi

**TEKNOFEST Savaşan İHA Yarışması** için geliştirilmiş, NVIDIA Jetson Nano üzerinde çalışan kapsamlı otonom İHA sistemi.

## 📋 Sistem Özellikleri

### Temel Özellikler
- **Görüntü İşleme**: YOLOv11 + TensorRT optimizasyonu ile gerçek zamanlı nesne tespiti
- **Otonom Navigasyon**: Yapay Potansiyel Alanlar (APF) algoritması ile engel kaçış
- **İletişim**: MAVLink protokolü ile Pixhawk entegrasyonu
- **Arayüz**: PyQt5 tabanlı Yer Kontrol İstasyonu (GCS)

### 🆕 TEKNOFEST Özellikleri
- **Hedef İHA Tespiti ve Takibi**: PID kontrolcü + Kalman filtresi ile frame merkezleme
- **Otonom Rota Takibi**: GPS waypoint navigasyonu (Haversine, cross-track error)
- **Hibrit Navigasyon**: 5 uçuş modu (SEARCH, TRACK, ATTACK, RETURN, EMERGENCY)
- **Çoklu Görev Yönetimi**: Öncelik bazlı mod geçişleri

### Platform
- NVIDIA Jetson Nano + Pixhawk
- USB/CSI Kamera
- GPS Modülü

## 📁 Proje Yapısı

```
iha_gorevim/
├── config.py                    # Sistem konfigürasyonu (güncellenmiş)
├── vision.py                    # YOLOv11 görüntü işleme modülü
├── navigation.py                # APF navigasyon modülü
├── communication.py             # MAVLink iletişim modülü
├── gui.py                       # PyQt5 GUI modülü
├── main.py                      # Ana orkestrasyon (güncellenmiş)
│
├── 🆕 target_tracker.py         # Hedef İHA takip modülü
├── 🆕 waypoint_navigator.py     # GPS waypoint navigasyon modülü
├── 🆕 hybrid_navigation.py      # Hibrit navigasyon sistemi
│
├── requirements.txt             # Python bağımlılıkları
├── README.md                    # Bu dosya
├── QUICKSTART.md                # Hızlı başlangıç kılavuzu
├── NASIL_ÇALIŞTIRILIIR.md       # Detaylı kullanım kılavuzu
├── 🆕 TEKNOFEST_KILAVUZ.md      # TEKNOFEST özellikleri kılavuzu
├── 🆕 ORNEK_CIKTILAR.py         # Örnek sistem çıktıları
│
├── models/                      # YOLO model dosyaları
│   └── yolov11.pt              # (Kullanıcı tarafından sağlanacak)
├── 🆕 missions/                 # Görev dosyaları
│   └── example_mission.json    # Örnek waypoint görevi
└── logs/                        # Sistem logları
```

## 🚀 Kurulum

### 1. Sistem Gereksinimleri

**Donanım:**
- NVIDIA Jetson Nano (4GB önerilir)
- USB veya CSI kamera
- Pixhawk uçuş kontrol kartı
- USB/Serial bağlantı kablosu

**Yazılım:**
- JetPack 4.6+ (CUDA, TensorRT dahil)
- Python 3.8+
- pip

### 2. Python Bağımlılıklarını Yükleyin

```bash
cd iha_gorevim
pip3 install -r requirements.txt
```

**Not:** TensorRT, Jetson Nano'da JetPack ile birlikte gelir. Ayrıca kurmanıza gerek yoktur.

### 3. YOLOv11 Modelini Hazırlayın

YOLOv11 modelinizi `models/` dizinine yerleştirin:

```bash
# Örnek: Ultralytics'ten pre-trained model indirme
cd models/
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov11n.pt
mv yolov11n.pt yolov11.pt
```

**Önemli:** Kendi veri setinizle eğitilmiş bir model kullanmanız önerilir.

### 4. Konfigürasyonu Ayarlayın

`config.py` dosyasını düzenleyin:

```python
# Kamera ayarları
CameraConfig.CAMERA_SOURCE = 0  # USB kamera için 0, CSI için pipeline kullanın

# MAVLink bağlantısı
MAVLinkConfig.CONNECTION_STRING = "/dev/ttyACM0"  # Pixhawk port'u
MAVLinkConfig.BAUD_RATE = 57600

# APF parametreleri (ihtiyaca göre ayarlayın)
NavigationConfig.K_REPULSIVE = 50.0
NavigationConfig.SAFE_DISTANCE = 5.0
NavigationConfig.MAX_DEVIATION_ANGLE = 45.0
```

## 🎮 Kullanım

### Hızlı Başlangıç

```bash
python3 main.py
```

Bu komut:
1. Tüm modülleri başlatır (vision, navigation, communication, TEKNOFEST modülleri)
2. Yer Kontrol İstasyonu GUI'sini açar
3. Kamera akışını ve telemetri verilerini gösterir

### 🆕 TEKNOFEST Özellikleri Kullanımı

#### 1. Hedef Sınıf ID Ayarlama (ÖNEMLİ!)

`config.py` dosyasında hedef İHA sınıf ID'sini ayarlayın:

```python
class TargetTrackingConfig:
    TARGET_CLASS_ID = 2  # YOLO modelinizdeki İHA sınıfının ID'si
    MIN_CONFIDENCE = 0.7
```

#### 2. Görev Dosyası Oluşturma

`missions/` klasöründe JSON görev dosyası oluşturun:

```json
{
  "mission_name": "TEKNOFEST Görev 1",
  "waypoints": [
    {"lat": 39.123, "lon": 35.456, "alt": 50, "name": "Kalkış", "loiter_time": 0},
    {"lat": 39.124, "lon": 35.457, "alt": 60, "name": "Arama 1", "loiter_time": 10},
    {"lat": 39.123, "lon": 35.456, "alt": 50, "name": "Dönüş", "loiter_time": 0}
  ]
}
```

#### 3. Görevi Yükle ve Başlat

GUI açıldıktan sonra veya `main.py` içinde:

```python
# Görev yükle
system.waypoint_navigator.load_mission_from_file("missions/my_mission.json")
system.waypoint_navigator.start_mission()
```

### GUI Kullanımı

**Video & Tespit Tab:**
- Gerçek zamanlı kamera görüntüsü
- Tespit edilen nesnelerin bounding box'ları (yeşil)
- **🆕 Hedef İHA göstergesi (kırmızı kutu)**
- FPS ve tespit sayısı
- En yakın engel mesafesi

**Telemetri Tab:**
- GPS konumu (enlem, boylam, irtifa)
- Attitude bilgileri (roll, pitch, yaw)
- Sistem durumu (mod, armed, hız, batarya)
- **🆕 Uçuş modu göstergesi (SEARCH/TRACK/ATTACK/RETURN/EMERGENCY)**

**Kontrol Tab:**
- "Otonom Modu Başlat" butonu
- "Otonom Modu Durdur" butonu
- "ACİL DURDUR" butonu
- **🆕 Gerçek zamanlı mod geçiş logları**
- Sistem logları

### Otonom Mod Aktivasyonu

1. GUI'de "Kontrol" tab'ına gidin
2. "▶️ Otonom Modu Başlat" butonuna tıklayın
3. Sistem otomatik olarak:
   - **Hedef İHA'yı tespit eder ve takip eder**
   - **Waypoint'leri takip eder**
   - **Engelleri tespit eder ve kaçar**
   - **Duruma göre mod değiştirir (SEARCH → TRACK → ATTACK vb.)**
   - Pixhawk'a komutlar gönderir

**⚠️ Güvenlik Uyarısı:** İlk testleri simülasyonda veya güvenli bir ortamda yapın!

## 📊 Örnek Çıktılar

### Sistem Başlatma

```
============================================================
OTONOM İHA SİSTEMİ BAŞLATILIYOR
============================================================
2026-02-07 20:15:00 | INFO     | 📋 Konfigürasyon doğrulanıyor...
2026-02-07 20:15:00 | INFO     | ✅ Konfigürasyon doğrulandı
2026-02-07 20:15:00 | INFO     | 📷 Vision modülü başlatılıyor...
✅ Model yükleme tamamlandı
✅ VisionProcessor başlatıldı
2026-02-07 20:15:05 | INFO     | 🎯 TEKNOFEST modülleri başlatılıyor...
✅ TargetTracker başlatıldı
✅ WaypointNavigator başlatıldı
✅ HybridNavigator başlatıldı
2026-02-07 20:15:06 | INFO     | ✅ Tüm modüller başarıyla başlatıldı
```

### Hedef Tespit ve Takip

```
[Kamera görüntüsünde tespitler:]
- person (0.92 güven, 15.3m mesafe)
- car (0.87 güven, 25.8m mesafe)
- uav (0.95 güven, 35.2m mesafe) ← HEDEF İHA!

2026-02-07 20:16:45 | INFO     | 🔄 Mod Değişimi: SEARCH → TRACK
2026-02-07 20:16:45 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 35.2m | Kaynak: tracking
2026-02-07 20:16:46 | INFO     | 🎯 HEDEF TAKİP - Mesafe: 33.8m | Kaynak: tracking

[PID Kontrolcü:]
- Frame merkezi: (320, 240)
- Hedef pozisyonu: (450, 280)
- Yaw komutu: +0.35 rad/s (Sağa dön)
```

### Saldırı Modu

```
2026-02-07 20:17:05 | INFO     | 🔄 Mod Değişimi: TRACK → ATTACK
2026-02-07 20:17:05 | INFO     | ⚔️ SALDIRI MODU - Mesafe: 18.5m | Kaynak: tracking
2026-02-07 20:17:06 | INFO     | ⚔️ SALDIRI MODU - Mesafe: 16.2m | Kaynak: tracking
```

### Acil Kaçış

```
[Kritik engel tespit edildi!]
2026-02-07 20:18:30 | INFO     | 🔄 Mod Değişimi: TRACK → EMERGENCY
2026-02-07 20:18:30 | WARNING  | 🚨 ACİL KAÇIŞ MODU AKTİF
2026-02-07 20:18:30 | INFO     | 🚨 ACİL KAÇIŞ MODU - Engel: 1.5m | Kaynak: obstacle_avoidance
```

**Daha fazla örnek için:** `ORNEK_CIKTILAR.py` dosyasına bakın.

## 🧪 Test Modları

### Vision Modülü Testi

```bash
python3 vision.py
```

Kamera görüntüsünü ve YOLO tespitlerini gösterir. ESC ile çıkış.

### 🆕 Target Tracker Testi

```bash
python3 target_tracker.py
```

Hedef takip modülünü test senaryolarıyla test eder.

### 🆕 Waypoint Navigator Testi

```bash
python3 waypoint_navigator.py
```

GPS navigasyon ve waypoint takibini test eder.

### 🆕 Hybrid Navigator Testi

```bash
python3 hybrid_navigation.py
```

Mod geçişlerini ve vektör birleştirmeyi test eder.

### Navigation Modülü Testi

```bash
python3 navigation.py
```

APF algoritmasını çeşitli senaryolarla test eder.

### Communication Modülü Testi

```bash
python3 communication.py
```

MAVLink bağlantısını ve telemetri verilerini test eder.

### Simülasyon Modu

Gerçek donanım olmadan test için `config.py`'de:

```python
SystemConfig.SIMULATION_MODE = True
```

## ⚙️ Konfigürasyon Parametreleri

### Kamera Ayarları (`CameraConfig`)

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `CAMERA_SOURCE` | Kamera ID veya pipeline | 0 |
| `FRAME_WIDTH` | Görüntü genişliği | 640 |
| `FRAME_HEIGHT` | Görüntü yüksekliği | 480 |
| `FPS` | Kare hızı | 30 |

### YOLO Ayarları (`YOLOConfig`)

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `CONFIDENCE_THRESHOLD` | Güven eşiği | 0.5 |
| `USE_TENSORRT` | TensorRT kullan | True |
| `INPUT_SIZE` | Model giriş boyutu | 640 |

### APF Ayarları (`NavigationConfig`)

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `K_ATTRACTIVE` | Çekici kuvvet kazancı | 1.0 |
| `K_REPULSIVE` | İtici kuvvet kazancı | 50.0 |
| `SAFE_DISTANCE` | Güvenli mesafe (m) | 5.0 |
| `CRITICAL_DISTANCE` | Kritik mesafe (m) | 2.0 |
| `MAX_DEVIATION_ANGLE` | Maks. sapma açısı (°) | 45.0 |

### MAVLink Ayarları (`MAVLinkConfig`)

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `CONNECTION_STRING` | Bağlantı string'i | /dev/ttyACM0 |
| `BAUD_RATE` | Baud rate | 57600 |
| `AUTO_MODE` | Otonom flight mode | GUIDED |

## 📊 Sistem Akışı

```
┌─────────────┐
│   Kamera    │
└──────┬──────┘
       │ Frame
       ▼
┌─────────────┐
│   YOLOv11   │ ◄── TensorRT Optimizasyonu
│  Detector   │
└──────┬──────┘
       │ Detections
       ▼
┌─────────────┐
│     APF     │
│  Algorithm  │
└──────┬──────┘
       │ Maneuver
       ▼
┌─────────────┐
│   MAVLink   │ ──► Pixhawk
│  Interface  │
└─────────────┘
       │
       ▼
┌─────────────┐
│   PyQt5     │
│     GUI     │
└─────────────┘
```

## 🔧 Sorun Giderme

### Kamera Açılmıyor

```bash
# USB kameraları listele
ls /dev/video*

# CSI kamera için
gst-launch-1.0 nvarguscamerasrc ! nvoverlaysink
```

### YOLO Model Yüklenmiyor

- Model dosyasının `models/yolov11.pt` konumunda olduğundan emin olun
- Model formatının `.pt` (PyTorch) olduğunu kontrol edin

### MAVLink Bağlantı Hatası

```bash
# Port'u kontrol et
ls /dev/ttyACM*
ls /dev/ttyUSB*

# İzinleri düzenle
sudo chmod 666 /dev/ttyACM0
```

### Düşük FPS

- TensorRT optimizasyonunun aktif olduğundan emin olun
- Görüntü çözünürlüğünü düşürün (örn: 640x480)
- Daha küçük YOLO modeli kullanın (yolov11n)

## 📝 Loglar

Sistem logları `logs/` dizininde saklanır:

```bash
# Son logları görüntüle
tail -f logs/uav_system_*.log
```

## 🛡️ Güvenlik Notları

1. **İlk testleri simülasyonda yapın**
2. **Güvenli bir test alanı kullanın**
3. **Her zaman manuel override hazır bulundurun**
4. **Acil durdur butonunu test edin**
5. **Batarya seviyesini izleyin**

## 🤝 Katkıda Bulunma

Proje geliştirmeleri için:
1. Yeni özellikler ekleyin
2. Hata düzeltmeleri yapın
3. Dokümantasyonu iyileştirin

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 👨‍💻 Geliştirici

Computer Engineering
Platform: NVIDIA Jetson Nano

---

**⚠️ UYARI:** Bu sistem otonom uçuş kontrolü yapar. Gerçek donanımda kullanmadan önce kapsamlı testler yapın ve yerel havacılık kurallarına uyun.
