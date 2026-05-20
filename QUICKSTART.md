# Hızlı Başlangıç Kılavuzu

## 🚀 Kurulum (3 Adım)

### 1. Bağımlılıkları Yükle
```bash
cd iha_gorevim
pip3 install -r requirements.txt
```

### 2. YOLO Modelini Ekle
```bash
# Model dosyanızı models/ dizinine kopyalayın
cp /path/to/your/yolov11.pt models/yolov11.pt
```

### 3. Konfigürasyonu Ayarla
`config.py` dosyasını düzenleyin:
```python
# Kamera
CameraConfig.CAMERA_SOURCE = 0  # USB kamera ID

# MAVLink
MAVLinkConfig.CONNECTION_STRING = "/dev/ttyACM0"  # Pixhawk port
```

## ▶️ Çalıştırma

### Ana Sistem
```bash
python3 main.py
```

### Test Modları
```bash
# Vision testi
python3 vision.py

# Navigation testi
python3 navigation.py

# Communication testi
python3 communication.py

# Simülasyon modu
# config.py'de SystemConfig.SIMULATION_MODE = True
python3 main.py
```

## 🎮 GUI Kullanımı

1. **Video Tab**: Kamera görüntüsü ve tespitler
2. **Telemetri Tab**: GPS, attitude, batarya
3. **Kontrol Tab**: 
   - "Otonom Modu Başlat" → Sistem aktif
   - "ACİL DURDUR" → Acil durum

## ⚙️ Önemli Parametreler

### APF Ayarları (navigation.py için)
```python
NavigationConfig.K_REPULSIVE = 50.0        # İtici kuvvet
NavigationConfig.SAFE_DISTANCE = 5.0       # Güvenli mesafe (m)
NavigationConfig.MAX_DEVIATION_ANGLE = 45.0 # Maks sapma (°)
```

### YOLO Ayarları
```python
YOLOConfig.CONFIDENCE_THRESHOLD = 0.5  # Tespit eşiği
YOLOConfig.USE_TENSORRT = True         # GPU hızlandırma
```

## 🔧 Sorun Giderme

### Kamera Bulunamıyor
```bash
ls /dev/video*  # Kamera ID'sini kontrol et
```

### MAVLink Bağlanamıyor
```bash
ls /dev/ttyACM*  # Port'u kontrol et
sudo chmod 666 /dev/ttyACM0  # İzin ver
```

### Düşük FPS
- Çözünürlüğü düşür: `CameraConfig.FRAME_WIDTH = 320`
- TensorRT aktif olduğundan emin ol
- Daha küçük model kullan (yolov11n)

## 📊 Sistem Akışı

```
Kamera → YOLO Tespit → APF Hesaplama → MAVLink Komut → Pixhawk
   ↓                                                        ↓
  GUI ← ← ← ← ← ← ← ← ← Telemetri ← ← ← ← ← ← ← ← ← ← ← ┘
```

## 🛡️ Güvenlik Kontrol Listesi

- [ ] Model dosyası hazır (`models/yolov11.pt`)
- [ ] Kamera çalışıyor (test: `python3 vision.py`)
- [ ] MAVLink bağlantısı OK (test: `python3 communication.py`)
- [ ] Simülasyonda test edildi
- [ ] Güvenli test alanı hazır
- [ ] Manuel override hazır
- [ ] Acil durdur butonu test edildi

## 📝 Log Kontrolü

```bash
# Gerçek zamanlı log izleme
tail -f logs/uav_system_*.log
```

## 🎯 İlk Test Önerisi

1. Simülasyon modunda başlat
2. GUI'de tüm tab'ları kontrol et
3. Vision testi yap (engel göster)
4. Navigation hesaplamalarını loglardan izle
5. Gerçek donanımda motorlar disarm durumda test et
6. Güvenli alanda tethered test yap

---

**Destek**: README.md dosyasında detaylı bilgi bulabilirsiniz.
