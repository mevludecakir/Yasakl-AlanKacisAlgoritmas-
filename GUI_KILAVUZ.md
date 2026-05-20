# 🚁 TEKNOFEST Gelişmiş Yer Kontrol İstasyonu - Kullanım Kılavuzu

## 📋 Genel Bakış

Yeni `gui_enhanced.py` modülü, TEKNOFEST Savaşan İHA yarışması için özel olarak tasarlanmış profesyonel bir yer kontrol istasyonu sağlar.

---

## 🎯 Özellikler

### 1. **Canlı Kamera Görüntüsü**
- Gerçek zamanlı video akışı
- Hedef İHA tespiti ve vurgulama (kırmızı kutu + ★)
- Normal nesneler için yeşil bounding box
- Kritik engeller için turuncu bounding box
- Frame merkezinde crosshair (+)
- FPS ve tespit sayısı overlay
- Mesafe göstergeleri

### 2. **Durum Paneli** (Sağ Taraf)
- **Uçuş Modu Göstergesi**: Büyük, renkli mod göstergesi
  - 🔍 SEARCH (Mavi)
  - 🎯 TRACK (Yeşil)
  - ⚔️ ATTACK (Turuncu)
  - 🏠 RETURN (Sarı)
  - 🚨 EMERGENCY (Kırmızı)

- **Hedef İHA Bilgileri**:
  - Tespit durumu (✅/❌)
  - Mesafe (metre)
  - Pozisyon (piksel koordinatları)
  - Kilitlenme durumu

- **GPS & Navigasyon**:
  - Enlem, Boylam, İrtifa
  - Hız (m/s)
  - Heading (derece)

- **Batarya Durumu**:
  - Voltaj
  - Yüzde (progress bar)
  - Renk kodlu uyarılar (yeşil > turuncu > kırmızı)

- **Waypoint Bilgileri**:
  - Aktif waypoint (2/5 formatında)
  - Waypoint'e mesafe
  - Görev ilerleme yüzdesi

### 3. **Waypoint Haritası**
- 2D harita görünümü
- Waypoint işaretleri (renkli)
  - Yeşil: Tamamlanan
  - Turuncu: Aktif
  - Gri: Beklemede
- İHA pozisyonu (mavi üçgen)
- Rota çizgisi (kesikli çizgi)

### 4. **Kontrol Paneli**
- ▶️ Otonom Modu Başlat
- ⏹️ Otonom Modu Durdur
- 🚨 ACİL DURDUR
- 📂 Görev Yükle
- 🏠 Üsse Dön

### 5. **Sistem Logları**
- Zaman damgalı log mesajları
- Renk kodlu gösterim
- Otomatik scroll

---

## 🚀 Kullanım

### Başlatma

```bash
python3 main.py
```

Sistem otomatik olarak gelişmiş GUI'yi başlatacaktır.

### İlk Kurulum

1. **Hedef Sınıf ID Ayarlama**
   
   `config.py` dosyasında:
   ```python
   class TargetTrackingConfig:
       TARGET_CLASS_ID = 2  # YOLO modelinizdeki İHA sınıf ID'si
   ```

2. **Görev Dosyası Hazırlama**
   
   `missions/` klasöründe JSON dosyası oluşturun:
   ```json
   {
     "mission_name": "Test Görevi",
     "waypoints": [
       {"lat": 39.123, "lon": 35.456, "alt": 50, "name": "Kalkış", "loiter_time": 0},
       {"lat": 39.124, "lon": 35.457, "alt": 60, "name": "Arama 1", "loiter_time": 10}
     ]
   }
   ```

### Görev Yükleme

1. GUI'de **"📂 Görev Yükle"** butonuna tıklayın
2. `missions/` klasöründen görev dosyasını seçin
3. Waypoint haritası otomatik olarak güncellenecektir

### Otonom Mod Başlatma

1. **"▶️ Otonom Modu Başlat"** butonuna tıklayın
2. Sistem otomatik olarak:
   - Hedef İHA'yı arayacak
   - Waypoint'leri takip edecek
   - Engelleri tespit edip kaçacak
   - Mod geçişleri yapacak

### Acil Durdurma

**"🚨 ACİL DURDUR"** butonu her zaman aktiftir ve:
- Otonom modu durdurur
- İHA'yı disarm eder (MAVLink bağlantısı varsa)
- Tüm komutları iptal eder

---

## 📊 Arayüz Bileşenleri

### Kamera Görüntüsü

```
┌─────────────────────────────────────────┐
│  [Canlı Kamera]                         │
│                                         │
│    ┌──────┐         ┏━━━━━━┓          │
│    │person│         ┃uav ★ ┃ ← Hedef  │
│    │0.92  │         ┃0.95  ┃          │
│    │15.3m │         ┃35.2m ┃          │
│    └──────┘         ┗━━━━━━┛          │
│                                         │
│         [+] ← Crosshair                 │
│                                         │
│  FPS: 24.3 | Tespit: 2 | Hedef: 35.2m │
└─────────────────────────────────────────┘
```

**Renk Kodları:**
- 🟢 Yeşil: Normal nesneler
- 🔴 Kırmızı + ★: Hedef İHA
- 🟠 Turuncu + ⚠️: Kritik engel (< 2m)

### Durum Paneli

```
┌─────────────────────────┐
│  🎯 UÇUŞ MODU           │
│  ┌───────────────────┐  │
│  │   TRACK 🎯        │  │
│  │  (Yeşil arka plan)│  │
│  └───────────────────┘  │
│  Hedef takip modu       │
├─────────────────────────┤
│  🎯 HEDEF İHA           │
│  Durum: ✅ Tespit      │
│  Mesafe: 35.2 m         │
│  Pozisyon: (500, 280)   │
│  Kilitlenme: Aktif      │
├─────────────────────────┤
│  📍 GPS & NAVİGASYON    │
│  Enlem: 39.123456°      │
│  Boylam: 35.654321°     │
│  İrtifa: 58.2 m         │
│  Hız: 5.2 m/s           │
│  Heading: 45.2°         │
├─────────────────────────┤
│  🔋 BATARYA             │
│  Voltaj: 12.6 V         │
│  ████████████░░░░ 85%   │
├─────────────────────────┤
│  📍 WAYPOINT            │
│  Aktif WP: 2/5          │
│  Mesafe: 125.3 m        │
│  ████████░░░░░░ 40%     │
└─────────────────────────┘
```

### Waypoint Haritası

```
┌─────────────────────────┐
│  Waypoint Haritası      │
│                         │
│    ●───────●            │
│   (1)     (2) ← Aktif   │
│    │       │            │
│    │       ▲ ← İHA      │
│    │       │            │
│    ●───────●            │
│   (5)     (3)           │
│            │            │
│            ●            │
│           (4)           │
└─────────────────────────┘
```

**Renkler:**
- 🟢 Yeşil: Tamamlanan waypoint
- 🟠 Turuncu: Aktif waypoint
- ⚪ Gri: Bekleyen waypoint
- 🔵 Mavi üçgen: İHA pozisyonu

---

## 🔧 Teknik Detaylar

### Modül Entegrasyonu

`gui_enhanced.py` şu modüllerle entegre çalışır:

1. **VisionProcessor** (`vision.py`)
   - Frame ve tespit verilerini alır
   - Kamera görüntüsünü günceller

2. **TargetTracker** (`target_tracker.py`)
   - Hedef İHA tespiti
   - Takip komutları

3. **WaypointNavigator** (`waypoint_navigator.py`)
   - Waypoint listesi
   - Navigasyon durumu
   - Harita güncellemesi

4. **HybridNavigator** (`hybrid_navigation.py`)
   - Uçuş modu (SEARCH/TRACK/ATTACK/RETURN/EMERGENCY)
   - Mod geçişleri

5. **MAVLinkInterface** (`communication.py`)
   - GPS, attitude, batarya verileri
   - Komut gönderimi

### Thread Yapısı

GUI iki ayrı thread kullanır:

1. **EnhancedVideoThread**
   - Video frame'lerini işler
   - Hedef tespiti yapar
   - 30-50ms güncelleme aralığı

2. **EnhancedTelemetryThread**
   - MAVLink telemetri verilerini toplar
   - Hybrid navigator durumunu okur
   - Waypoint bilgilerini günceller
   - 100ms güncelleme aralığı

### Veri Akışı

```
Vision → EnhancedVideoThread → CameraWidget
                              → StatusPanel (Hedef)

MAVLink → EnhancedTelemetryThread → StatusPanel (GPS, Batarya)
                                   → WaypointMapWidget

HybridNavigator → EnhancedTelemetryThread → StatusPanel (Mod)

WaypointNavigator → EnhancedTelemetryThread → StatusPanel (WP)
                                             → WaypointMapWidget
```

---

## 🎨 Özelleştirme

### Renkleri Değiştirme

`gui_enhanced.py` dosyasında `Colors` sınıfını düzenleyin:

```python
class Colors:
    # Mod renkleri
    SEARCH = QColor(33, 150, 243)      # Mavi
    TRACK = QColor(76, 175, 80)        # Yeşil
    ATTACK = QColor(255, 152, 0)       # Turuncu
    # ...
```

### Pencere Boyutu

`TEKNOFESTGroundStation._init_ui()` metodunda:

```python
self.setGeometry(50, 50, 1400, 900)  # x, y, width, height
```

### Panel Genişliği

`StatusPanel.__init__()` metodunda:

```python
self.setMaximumWidth(350)  # Maksimum genişlik
self.setMinimumWidth(300)  # Minimum genişlik
```

---

## 🐛 Sorun Giderme

### Sorun 1: GUI Açılmıyor

**Belirti:**
```
ImportError: cannot import name 'TEKNOFESTGroundStation'
```

**Çözüm:**
```bash
# gui_enhanced.py dosyasının varlığını kontrol edin
ls gui_enhanced.py

# PyQt5 kurulu mu?
python3 -c "import PyQt5; print('OK')"
```

### Sorun 2: Kamera Görüntüsü Gelmiyor

**Belirti:** Siyah ekran

**Çözüm:**
1. Vision modülünün başlatıldığından emin olun
2. Kamera bağlantısını kontrol edin
3. `main.py` loglarını inceleyin

### Sorun 3: Waypoint Haritası Boş

**Belirti:** "Görev yüklenmedi" mesajı

**Çözüm:**
1. Görev dosyası yükleyin (📂 Görev Yükle)
2. JSON formatını kontrol edin
3. `missions/` klasörünün varlığını doğrulayın

### Sorun 4: Mod Göstergesi Güncellenmiyor

**Belirti:** Hep "SEARCH" modunda kalıyor

**Çözüm:**
1. `hybrid_navigator` modülünün başlatıldığından emin olun
2. Hedef tespit edildiğinde mod otomatik değişmeli
3. `main.py` loglarında mod geçişlerini kontrol edin

---

## 📝 Eski GUI ile Karşılaştırma

| Özellik | Eski GUI (`gui.py`) | Yeni GUI (`gui_enhanced.py`) |
|---------|---------------------|------------------------------|
| Kamera görüntüsü | ✅ Var | ✅ Gelişmiş (hedef vurgulama) |
| Telemetri | ✅ Temel | ✅ Kapsamlı |
| Hedef bilgileri | ❌ Yok | ✅ Var |
| Waypoint haritası | ❌ Yok | ✅ Var |
| Mod göstergesi | ❌ Yok | ✅ Var (renkli) |
| Görev yükleme | ❌ Yok | ✅ Var |
| Batarya renk kodlama | ❌ Yok | ✅ Var |
| TEKNOFEST uyumlu | ❌ Hayır | ✅ Evet |

---

## 🚀 Gelecek Geliştirmeler

- [ ] Hedef iz çizgisi (tracking trail)
- [ ] Kilitlenme süresi sayacı
- [ ] Harita zoom/pan
- [ ] Telemetri grafikleri
- [ ] Log export (TXT, CSV)
- [ ] Dark/Light tema seçimi
- [ ] Tam ekran modu
- [ ] Ekran görüntüsü kaydetme
- [ ] Video kaydı

---

## 📚 İlgili Dosyalar

- `gui_enhanced.py` - Ana GUI modülü
- `main.py` - Sistem entegrasyonu
- `config.py` - Konfigürasyon
- `target_tracker.py` - Hedef takip
- `waypoint_navigator.py` - Waypoint navigasyon
- `hybrid_navigation.py` - Mod yönetimi
- `vision.py` - Görüntü işleme
- `communication.py` - MAVLink

---

**İyi uçuşlar! 🚁**
