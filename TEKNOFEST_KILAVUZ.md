# 🎯 TEKNOFEST Savaşan İHA - Yeni Özellikler Kılavuzu

## 📋 Genel Bakış

Bu sistem, TEKNOFEST Savaşan İHA yarışması gereksinimlerine göre genişletilmiştir. Artık sistem:

1. ✅ **Hedef İHA Tespiti ve Takibi** - Rakip İHA'yı tespit eder ve kamera frame'i içinde tutar
2. ✅ **Otonom Rota Takibi** - GPS waypoint'ler üzerinden otonom uçuş yapar
3. ✅ **Hibrit Navigasyon** - Engel kaçış, hedef takip ve rota takibini akıllıca birleştirir
4. ✅ **Çoklu Görev Modu** - SEARCH, TRACK, ATTACK, RETURN, EMERGENCY modları

---

## 🆕 Yeni Modüller

### 1. `target_tracker.py` - Hedef İHA Takip Modülü

**Özellikler:**
- **PID Kontrolcü**: Frame merkezinde hedef tutma (X ve Y ekseni)
- **Kalman Filtresi**: Hedef pozisyon tahmini ve gürültü filtreleme
- **Hedef Tespit**: YOLO tespitleri arasından İHA sınıfını filtreler
- **Kayıp Yönetimi**: Hedef kaybedildiğinde tahmin ile devam eder

**Kullanım:**
```python
from target_tracker import TargetTracker

tracker = TargetTracker()

# Hedef tespit et
target = tracker.detect_target_uav(detections)

# Takip komutu hesapla
command = tracker.calculate_tracking_command(target)
# Returns: {'tracking_active': bool, 'yaw_rate': float, 'pitch_rate': float, ...}
```

**Konfigürasyon** (`config.py`):
```python
class TargetTrackingConfig:
    TARGET_CLASS_ID = 2  # İHA sınıf ID (modelinize göre ayarlayın!)
    MIN_CONFIDENCE = 0.7
    PID_KP = 0.5  # PID parametreleri
    MAX_YAW_RATE = 0.5  # rad/s
    IDEAL_TRACKING_DISTANCE = 25.0  # metre
```

---

### 2. `waypoint_navigator.py` - Otonom Rota Takip Modülü

**Özellikler:**
- **GPS Navigasyon**: Haversine formülü ile mesafe hesaplama
- **Bearing Hesaplama**: İki nokta arası yön bulma
- **Cross-Track Error**: Rota sapması hesaplama ve düzeltme
- **Loiter Modu**: Waypoint'te bekleme

**Kullanım:**
```python
from waypoint_navigator import WaypointNavigator

navigator = WaypointNavigator()

# Görev yükle
navigator.load_mission_from_file("missions/example_mission.json")
navigator.start_mission()

# Navigasyon güncelle
current_pos = {'lat': 39.123, 'lon': 35.456, 'alt': 50.0}
nav_data = navigator.update_navigation(current_pos)
# Returns: {'active': bool, 'target_bearing': float, 'distance_to_wp': float, ...}
```

**Görev Dosyası Formatı** (`missions/example_mission.json`):
```json
{
  "mission_name": "Örnek Görev",
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
    }
  ]
}
```

---

### 3. `hybrid_navigation.py` - Hibrit Navigasyon Modülü

**Özellikler:**
- **Çoklu Mod Yönetimi**: 5 farklı uçuş modu
- **Öncelik Sistemi**: Acil > Hedef > Rota
- **Vektör Birleştirme**: Farklı navigasyon kaynaklarını birleştirir

**Uçuş Modları:**

| Mod | İkon | Açıklama | Öncelik |
|-----|------|----------|---------|
| **EMERGENCY** | 🚨 | Kritik engel (< 2m) | 1 (En yüksek) |
| **TRACK** | 🎯 | Hedef tespit edildi | 2 |
| **ATTACK** | ⚔️ | Hedef yakın (< 20m) | 2 |
| **RETURN** | 🏠 | Batarya düşük / Görev bitti | 3 |
| **SEARCH** | 🔍 | Normal waypoint takibi | 4 (En düşük) |

**Kullanım:**
```python
from hybrid_navigation import HybridNavigator, FlightMode

hybrid_nav = HybridNavigator()

# Mod belirle
mode = hybrid_nav.determine_flight_mode(
    obstacle_data, tracking_data, waypoint_data, telemetry
)

# Vektörleri birleştir
combined = hybrid_nav.combine_navigation_vectors(
    obstacle_maneuver, tracking_command, waypoint_nav, mode
)
# Returns: {'heading': float, 'speed_factor': float, 'priority_source': str}
```

---

## 🎮 Sistem Kullanımı

### Adım 1: Konfigürasyon

`config.py` dosyasını düzenleyin:

```python
# Hedef İHA sınıf ID'sini ayarlayın (YOLO modelinize göre)
class TargetTrackingConfig:
    TARGET_CLASS_ID = 2  # ÖNEMLİ: Modelinize göre değiştirin!

# Üs konumunu ayarlayın
class MissionConfig:
    HOME_LAT = 39.123000  # Gerçek koordinatlarınız
    HOME_LON = 35.456000
    HOME_ALT = 0.0
```

### Adım 2: Görev Dosyası Oluşturma

`missions/` klasöründe JSON görev dosyası oluşturun:

```json
{
  "mission_name": "TEKNOFEST Görev 1",
  "waypoints": [
    {"lat": 39.123, "lon": 35.456, "alt": 50, "name": "Start", "loiter_time": 0},
    {"lat": 39.124, "lon": 35.457, "alt": 60, "name": "Search 1", "loiter_time": 10},
    {"lat": 39.123, "lon": 35.456, "alt": 50, "name": "Return", "loiter_time": 0}
  ]
}
```

### Adım 3: Görevi Yükle ve Başlat

Ana sistemde waypoint navigator'ı kullanın:

```python
# main.py içinde
system.waypoint_navigator.load_mission_from_file("missions/my_mission.json")
system.waypoint_navigator.start_mission()
```

### Adım 4: Sistemi Çalıştır

```bash
python main.py
```

---

## 🎯 Çalışma Senaryoları

### Senaryo 1: Normal Arama Modu

```
1. Sistem başlar → SEARCH modu
2. Waypoint'leri takip eder
3. Engel tespit edilirse → Geçici kaçış
4. Waypoint takibine devam
```

**Konsol Çıktısı:**
```
🔍 ARAMA - WP1/4 (125.3m) | Kaynak: waypoint
```

### Senaryo 2: Hedef Tespit Edildi

```
1. SEARCH modunda waypoint takibi
2. Hedef İHA tespit edildi → TRACK moduna geçiş
3. Hedefi frame merkezinde tutar
4. Mesafe 20m'nin altına düşerse → ATTACK modu
5. Hedef kaybedilirse → SEARCH moduna dön
```

**Konsol Çıktısı:**
```
🔄 Mod Değişimi: SEARCH → TRACK
🎯 HEDEF TAKİP - Mesafe: 35.2m | Kaynak: tracking
⚔️ SALDIRI MODU - Mesafe: 18.5m | Kaynak: tracking
```

### Senaryo 3: Kritik Engel

```
1. Herhangi bir modda
2. Engel < 2m tespit edildi → EMERGENCY modu
3. Tüm diğer görevler askıya alınır
4. Maksimum kaçış manevrası
5. Engel geçildikten sonra → Önceki moda dön
```

**Konsol Çıktısı:**
```
🔄 Mod Değişimi: TRACK → EMERGENCY
🚨 ACİL KAÇIŞ MODU - Engel: 1.5m | Kaynak: obstacle_avoidance
🚨 ACİL KAÇIŞ MODU AKTİF
```

### Senaryo 4: Batarya Düşük

```
1. Batarya < 20% → RETURN modu
2. Üs waypoint'ine yönelir (HOME_LAT/LON)
3. Engel varsa kaçar ama üsse dönmeye devam eder
4. Üsse ulaşınca görev tamamlanır
```

**Konsol Çıktısı:**
```
🔄 Mod Değişimi: SEARCH → RETURN
🏠 DÖNÜŞ - Üsse: 245.8m | Kaynak: waypoint
```

---

## 🔧 Test ve Doğrulama

### Modül Testleri

Her modül bağımsız test edilebilir:

```bash
# Hedef takip testi
python target_tracker.py

# Waypoint navigasyon testi
python waypoint_navigator.py

# Hibrit navigasyon testi
python hybrid_navigation.py
```

### Simülasyon Modu

Gerçek donanım olmadan test için:

```python
# config.py
class SystemConfig:
    SIMULATION_MODE = True  # Kamera ve MAVLink devre dışı
```

---

## ⚙️ İleri Seviye Ayarlar

### PID Tuning

Hedef takip performansını optimize etmek için:

```python
class TargetTrackingConfig:
    # Daha agresif takip için Kp'yi artırın
    PID_KP = 0.7  # Varsayılan: 0.5
    
    # Daha stabil takip için Kd'yi artırın
    PID_KD = 0.3  # Varsayılan: 0.2
    
    # Uzun süreli hata düzeltmesi için Ki'yi ayarlayın
    PID_KI = 0.15  # Varsayılan: 0.1
```

### Waypoint Hassasiyeti

```python
class WaypointConfig:
    # Daha hassas varış için yarıçapı küçültün
    WAYPOINT_RADIUS = 3.0  # Varsayılan: 5.0
    
    # Rota sapma toleransı
    MAX_ROUTE_DEVIATION = 5.0  # Varsayılan: 10.0
```

### Mod Geçiş Ağırlıkları

`hybrid_navigation.py` içinde `_get_mode_weights()` metodunu düzenleyin:

```python
FlightMode.TRACK: {
    'obstacle': 0.3,  # Engel kaçışa daha az ağırlık
    'tracking': 0.7,  # Hedef takibe daha fazla ağırlık
    'waypoint': 0.0
}
```

---

## 🐛 Sorun Giderme

### Hedef Tespit Edilmiyor

**Çözüm:**
1. `TargetTrackingConfig.TARGET_CLASS_ID` değerini kontrol edin
2. YOLO modelinizin İHA sınıfını desteklediğinden emin olun
3. `MIN_CONFIDENCE` değerini düşürün (örn. 0.5)

### Waypoint'e Ulaşılamıyor

**Çözüm:**
1. GPS koordinatlarının doğru olduğundan emin olun
2. `WAYPOINT_RADIUS` değerini artırın
3. `ALTITUDE_TOLERANCE` değerini artırın

### Mod Geçişleri Çok Sık

**Çözüm:**
1. Öncelik eşiklerini ayarlayın
2. `TARGET_LOST_TIMEOUT` değerini artırın
3. Hibrit navigasyon ağırlıklarını düzenleyin

---

## 📊 Performans Beklentileri

| Metrik | Hedef | Gerçek (Jetson Nano) |
|--------|-------|----------------------|
| FPS | > 20 | 20-30 |
| Hedef Tespit Oranı | > 90% | Model'e bağlı |
| Takip Stabilitesi | ±10 piksel | PID tuning'e bağlı |
| Waypoint Hassasiyeti | ±5 metre | GPS'e bağlı |
| Karar Verme Hızı | < 50ms | ~30ms |

---

## 🎓 Önemli Notlar

1. **Hedef Sınıf ID**: Mutlaka YOLO modelinize göre ayarlayın!
2. **GPS Koordinatları**: Gerçek konumunuzu kullanın
3. **PID Tuning**: Gerçek uçuş testlerinde fine-tuning yapın
4. **Güvenlik**: Acil kaçış her zaman en yüksek öncelik
5. **Test**: Önce simülasyonda, sonra gerçek donanımda test edin

---

## 📚 İlgili Dosyalar

- `target_tracker.py` - Hedef takip implementasyonu
- `waypoint_navigator.py` - Rota takip implementasyonu
- `hybrid_navigation.py` - Hibrit navigasyon implementasyonu
- `config.py` - Tüm konfigürasyonlar
- `main.py` - Ana sistem entegrasyonu
- `missions/example_mission.json` - Örnek görev dosyası

---

**İyi uçuşlar! 🚁**
