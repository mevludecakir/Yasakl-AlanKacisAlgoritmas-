# 📸 GÖRSEL ÇIKTI ÖRNEKLERİ - TEKNOFEST Savaşan İHA Sistemi

Bu dosya, sistemin görsel çıktılarını ASCII art ve detaylı açıklamalarla gösterir.

---

## 🖥️ GUI ARAYÜZÜ - Ana Pencere

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║  🚁 Otonom İHA Kontrol Sistemi - TEKNOFEST Savaşan İHA                    [_][□][X] ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  [📹 Video & Tespit]  [📡 Telemetri]  [🎮 Kontrol]                                  ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                       ║
║  ┌─────────────────────────────────────────────┐  ┌──────────────────────────────┐ ║
║  │                                             │  │  📊 DURUM BİLGİLERİ          │ ║
║  │   [CANLI KAMERA GÖRÜNTÜSÜ]                 │  │                              │ ║
║  │                                             │  │  Mod: TRACK 🎯               │ ║
║  │    ┌──────────┐                            │  │  Hedef: Tespit Edildi        │ ║
║  │    │person    │  ← Yeşil kutu              │  │  Mesafe: 35.2m               │ ║
║  │    │0.92      │                             │  │                              │ ║
║  │    │15.3m     │                             │  │  ─────────────────────────   │ ║
║  │    └──────────┘                             │  │                              │ ║
║  │                                             │  │  GPS: 39.123456, 35.654321   │ ║
║  │                  ┌──────────┐               │  │  İrtifa: 58.2m               │ ║
║  │                  │uav  ★    │  ← KIRMIZI!   │  │  Heading: 45.2° (KD)         │ ║
║  │                  │0.95      │                │  │                              │ ║
║  │                  │35.2m     │                │  │  ─────────────────────────   │ ║
║  │                  └──────────┘                │  │                              │ ║
║  │                                             │  │  Batarya: 12.6V (85%)        │ ║
║  │         ┌──────────┐                        │  │  ████████████████░░░░        │ ║
║  │         │car       │                        │  │                              │ ║
║  │         │0.87      │                        │  │  Hız: 5.2 m/s                │ ║
║  │         │25.8m     │                        │  │  Armed: ✅                   │ ║
║  │         └──────────┘                        │  │                              │ ║
║  │                                             │  └──────────────────────────────┘ ║
║  │                                             │                                   ║
║  │  FPS: 24.3 | Tespit: 3 | En Yakın: 15.3m  │                                   ║
║  └─────────────────────────────────────────────┘                                   ║
║                                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
```

**Renk Kodları:**
- 🟢 **Yeşil Kutu**: Normal nesneler (person, car, chair, vb.)
- 🔴 **Kırmızı Kutu + Yıldız (★)**: Hedef İHA (TARGET_CLASS_ID)
- Kutu içinde: Sınıf adı, güven skoru, mesafe

---

## 📹 KAMERA GÖRÜNTÜSÜ - Farklı Senaryolar

### Senaryo 1: Normal Arama Modu (SEARCH)

```
┌─────────────────────────────────────────────────────────────┐
│  KAMERA GÖRÜNTÜSÜ - SEARCH Modu                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    ┌──────────┐                             │
│                    │ tree     │  ← Engel tespit edildi      │
│                    │ 0.85     │                             │
│                    │ 12.5m    │                             │
│                    └──────────┘                             │
│                                                              │
│         ┌──────────┐                                        │
│         │ person   │                                        │
│         │ 0.92     │                                        │
│         │ 8.3m     │                                        │
│         └──────────┘                                        │
│                                                              │
│                                                              │
│  [+] Merkez                                                 │
│                                                              │
│  FPS: 26.1 | Tespit: 2 | Mod: SEARCH 🔍                    │
│  Waypoint: WP2/5 (125.3m)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Senaryo 2: Hedef Tespit Edildi (TRACK Modu)

```
┌─────────────────────────────────────────────────────────────┐
│  KAMERA GÖRÜNTÜSÜ - TRACK Modu                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                                                              │
│                       ┏━━━━━━━━━━┓  ← HEDEF İHA!           │
│                       ┃ uav  ★   ┃     (Kırmızı kutu)       │
│                       ┃ 0.95     ┃                           │
│                       ┃ 35.2m    ┃                           │
│                       ┗━━━━━━━━━━┛                           │
│                                                              │
│                                                              │
│  [+] Merkez ← Hedef buraya çekiliyor                        │
│                                                              │
│                                                              │
│  FPS: 24.3 | Tespit: 1 | Mod: TRACK 🎯                     │
│  Hedef Mesafe: 35.2m | Yaw: +0.35 rad/s (Sağa dön)         │
└─────────────────────────────────────────────────────────────┘
```

### Senaryo 3: Hedef Merkezlendi (ATTACK Modu)

```
┌─────────────────────────────────────────────────────────────┐
│  KAMERA GÖRÜNTÜSÜ - ATTACK Modu                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                                                              │
│                                                              │
│                    ┏━━━━━━━━━━┓                             │
│                    ┃ uav  ★   ┃  ← Hedef merkezde!          │
│                    ┃ 0.96     ┃                             │
│                    ┃ 18.5m    ┃     Saldırı mesafesi!       │
│                    ┗━━━━━━━━━━┛                             │
│                    [+] Merkez                                │
│                                                              │
│                                                              │
│  FPS: 25.8 | Tespit: 1 | Mod: ATTACK ⚔️                    │
│  Hedef Kilitli! | Hız: 2.5 m/s (Yavaş yaklaşma)            │
└─────────────────────────────────────────────────────────────┘
```

### Senaryo 4: Kritik Engel (EMERGENCY Modu)

```
┌─────────────────────────────────────────────────────────────┐
│  KAMERA GÖRÜNTÜSÜ - EMERGENCY Modu                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️  │
│                                                              │
│              ┌──────────┐                                   │
│              │ person   │  ← KRİTİK ENGEL!                  │
│              │ 0.95     │     1.5m mesafede!                │
│              │ 1.5m ⚠️  │                                   │
│              └──────────┘                                   │
│                                                              │
│                                                              │
│  [+] Merkez                                                 │
│                                                              │
│  ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️  │
│  FPS: 23.1 | Tespit: 1 | Mod: EMERGENCY 🚨                 │
│  ACİL KAÇIŞ! Sapma: 45° (Maksimum)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 TELEMETRİ TAB'I

```
╔══════════════════════════════════════════════════════════════╗
║  📡 TELEMETRİ BİLGİLERİ                                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─ GPS Bilgileri ────────────────────────────────────────┐  ║
║  │                                                         │  ║
║  │  📍 Konum                                               │  ║
║  │     Enlem:     39.123456°                              │  ║
║  │     Boylam:    35.654321°                              │  ║
║  │     İrtifa:    58.2 m                                  │  ║
║  │     Fix Tipi:  3D GPS ✅                               │  ║
║  │     Uydu:      12 adet                                 │  ║
║  │                                                         │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─ Attitude Bilgileri ────────────────────────────────────┐  ║
║  │                                                         │  ║
║  │  🧭 Yönelim                                             │  ║
║  │     Roll:      2.3°   [====|    ]                      │  ║
║  │     Pitch:    -1.5°   [   |=    ]                      │  ║
║  │     Yaw:      45.2°   [=====|   ]                      │  ║
║  │     Heading:  45.2° (Kuzeydoğu)                        │  ║
║  │                                                         │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─ Sistem Durumu ─────────────────────────────────────────┐  ║
║  │                                                         │  ║
║  │  ⚙️ Durum                                               │  ║
║  │     Mod:       TRACK 🎯                                │  ║
║  │     Armed:     ✅ Evet                                 │  ║
║  │     Hız:       5.2 m/s                                 │  ║
║  │     Batarya:   12.6V (85%)                             │  ║
║  │                ████████████████░░░░ 85%                │  ║
║  │                                                         │  ║
║  │  🎯 Hedef Bilgileri                                     │  ║
║  │     Durum:     Tespit Edildi ✅                        │  ║
║  │     Mesafe:    35.2 m                                  │  ║
║  │     Pozisyon:  (500, 280) px                           │  ║
║  │     Hız:       (15, 5) px/s                            │  ║
║  │                                                         │  ║
║  │  📍 Waypoint Bilgileri                                  │  ║
║  │     Aktif WP:  2/5 (Arama Noktası 1)                   │  ║
║  │     Mesafe:    125.3 m                                 │  ║
║  │     Yön:       45.2° (KD)                              │  ║
║  │     CTE:       2.1 m (Rota sapması)                    │  ║
║  │                                                         │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🎮 KONTROL TAB'I

```
╔══════════════════════════════════════════════════════════════╗
║  🎮 OTONOM MOD KONTROLÜ                                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─ Mod Kontrolü ──────────────────────────────────────────┐  ║
║  │                                                         │  ║
║  │  ┌───────────────────────────────────────────────────┐ │  ║
║  │  │  ▶️  OTONOM MODU BAŞLAT                           │ │  ║
║  │  └───────────────────────────────────────────────────┘ │  ║
║  │         (Yeşil buton - Tıklanabilir)                   │  ║
║  │                                                         │  ║
║  │  ┌───────────────────────────────────────────────────┐ │  ║
║  │  │  ⏹️  OTONOM MODU DURDUR                           │ │  ║
║  │  └───────────────────────────────────────────────────┘ │  ║
║  │         (Kırmızı buton - Şu an pasif)                  │  ║
║  │                                                         │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─ Acil Durum ────────────────────────────────────────────┐  ║
║  │                                                         │  ║
║  │  ┌───────────────────────────────────────────────────┐ │  ║
║  │  │  🚨  ACİL DURDUR                                  │ │  ║
║  │  └───────────────────────────────────────────────────┘ │  ║
║  │         (Turuncu buton - Her zaman aktif)              │  ║
║  │                                                         │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
║  ┌─ Sistem Logları ────────────────────────────────────────┐  ║
║  │                                                         │  ║
║  │  [20:16:10] ▶️  Otonom mod başlatıldı                  │  ║
║  │  [20:16:10] 🔍 ARAMA - WP1/5 (245.3m)                  │  ║
║  │  [20:16:11] 🔍 ARAMA - WP1/5 (238.7m)                  │  ║
║  │  [20:16:12] 🔍 ARAMA - WP1/5 (231.2m)                  │  ║
║  │  [20:16:45] 🔄 Mod Değişimi: SEARCH → TRACK            │  ║
║  │  [20:16:45] 🎯 HEDEF TAKİP - Mesafe: 35.2m             │  ║
║  │  [20:16:46] 🎯 HEDEF TAKİP - Mesafe: 33.8m             │  ║
║  │  [20:16:47] 🎯 HEDEF TAKİP - Mesafe: 31.5m             │  ║
║  │  [20:17:05] 🔄 Mod Değişimi: TRACK → ATTACK            │  ║
║  │  [20:17:05] ⚔️ SALDIRI MODU - Mesafe: 18.5m            │  ║
║  │  [20:17:06] ⚔️ SALDIRI MODU - Mesafe: 16.2m            │  ║
║  │  [20:18:30] 🔄 Mod Değişimi: ATTACK → EMERGENCY        │  ║
║  │  [20:18:30] 🚨 ACİL KAÇIŞ MODU - Engel: 1.5m           │  ║
║  │  [20:18:30] ⚠️  ACİL KAÇIŞ MODU AKTİF                  │  ║
║  │  [20:18:34] 🔄 Mod Değişimi: EMERGENCY → TRACK         │  ║
║  │  [20:19:18] 🔄 Mod Değişimi: TRACK → SEARCH            │  ║
║  │  [20:20:47] ✅ Waypoint 2 ulaşıldı: Arama Noktası 1    │  ║
║  │  [20:20:47] ⏳ Loiter: 0.5/10.0s                       │  ║
║  │  [20:25:30] 🔄 Mod Değişimi: SEARCH → RETURN           │  ║
║  │  [20:26:46] 🏁 Görev tamamlandı!                       │  ║
║  │  [20:27:00] ⏹️  Otonom mod durduruldu                  │  ║
║  │                                                         │  ║
║  └─────────────────────────────────────────────────────────┘  ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🔄 MOD GEÇİŞ DİYAGRAMI

```
                    ┌─────────────────────────────────────┐
                    │      UÇUŞ MODLARI AKIŞI             │
                    └─────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────┐
    │                    ÖNCELİK HİYERARŞİSİ                       │
    │                                                               │
    │  1️⃣  EMERGENCY 🚨  (En Yüksek - Kritik engel < 2m)          │
    │  2️⃣  TRACK/ATTACK 🎯⚔️  (Hedef tespit edildi)               │
    │  3️⃣  RETURN 🏠  (Batarya < 20%)                              │
    │  4️⃣  SEARCH 🔍  (Normal waypoint takibi)                     │
    └──────────────────────────────────────────────────────────────┘


                         ┌─────────────┐
                         │  SEARCH 🔍  │  ← Başlangıç modu
                         │   (Arama)   │     Waypoint takibi
                         └──────┬──────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
         Hedef tespit    Batarya < 20%   Kritik engel
                │               │               │
                ▼               ▼               ▼
         ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
         │  TRACK 🎯   │ │  RETURN 🏠  │ │ EMERGENCY🚨 │
         │  (Takip)    │ │  (Dönüş)    │ │ (Acil Kaçış)│
         └──────┬──────┘ └─────────────┘ └──────┬──────┘
                │                                │
         Mesafe < 20m                     Engel geçildi
                │                                │
                ▼                                │
         ┌─────────────┐                        │
         │  ATTACK ⚔️  │                        │
         │  (Saldırı)  │                        │
         └──────┬──────┘                        │
                │                                │
         Hedef kayıp                            │
                │                                │
                └────────────┬───────────────────┘
                             │
                             ▼
                      ┌─────────────┐
                      │  SEARCH 🔍  │  ← Geri dönüş
                      │   (Arama)   │
                      └─────────────┘


    MOD DETAYLARI:

    🔍 SEARCH (Arama)
       • Waypoint'leri takip eder
       • Hedef İHA arar
       • Engel varsa kaçar (%30 ağırlık)
       • Waypoint takibi öncelikli (%70 ağırlık)

    🎯 TRACK (Takip)
       • Hedefi frame merkezinde tutar
       • PID kontrolcü ile yaw/pitch ayarlar
       • Engel varsa kaçar (%40 ağırlık)
       • Hedef takibi öncelikli (%60 ağırlık)

    ⚔️ ATTACK (Saldırı)
       • Hedef < 20m mesafede
       • Hız azaltılır (hassas yaklaşma)
       • Hedef takibi çok öncelikli (%70 ağırlık)
       • Engel kaçış (%30 ağırlık)

    🏠 RETURN (Dönüş)
       • Batarya < 20%
       • Üs waypoint'ine döner
       • Waypoint takibi öncelikli (%60 ağırlık)
       • Engel kaçış (%40 ağırlık)

    🚨 EMERGENCY (Acil Kaçış)
       • Engel < 2m (KRİTİK!)
       • Tüm diğer görevler askıya alınır
       • Sadece engel kaçış (%100 ağırlık)
       • Maksimum sapma açısı (45°)
```

---

## 📈 PERFORMANS GRAFİKLERİ (Konsol Çıktısı)

```
┌─────────────────────────────────────────────────────────────┐
│  PERFORMANS METRİKLERİ - Son 60 saniye                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  FPS (Kare/saniye):                                         │
│  30 ┤                                                        │
│  25 ┤ ████████████████████████████                          │
│  20 ┤ ████████████████████████████████████                  │
│  15 ┤                                                        │
│  10 ┤                                                        │
│   5 ┤                                                        │
│   0 └────────────────────────────────────────────────────   │
│      0s    10s    20s    30s    40s    50s    60s           │
│                                                              │
│  Ortalama: 24.3 FPS | Min: 20.1 | Max: 28.7                │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Hedef Mesafe (metre):                                      │
│  50 ┤                                                        │
│  40 ┤ ██                                                     │
│  30 ┤   ████                                                 │
│  20 ┤       ████████                                         │
│  10 ┤               ████                                     │
│   0 └────────────────────────────────────────────────────   │
│      0s    10s    20s    30s    40s    50s    60s           │
│                                                              │
│  Başlangıç: 45.2m → Saldırı: 18.5m → Kayıp: 0m             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 HEDEF TESPİT DETAYLARI

### Vision Modülü Çıktısı (vision.py)

```python
# YOLODetector.detect() metodunun döndürdüğü veri:

detections = [
    {
        'bbox': [120, 80, 180, 150],      # Sol-üst ve sağ-alt köşe
        'confidence': 0.92,                # %92 güven
        'class_id': 0,                     # Sınıf ID (person)
        'class_name': 'person',            # Sınıf adı
        'center': (150, 115),              # Merkez koordinatları
        'distance': 15.3                   # Tahmini mesafe (metre)
    },
    {
        'bbox': [450, 230, 550, 330],
        'confidence': 0.95,                # %95 güven
        'class_id': 2,                     # ← HEDEF İHA SINIFI!
        'class_name': 'uav',               # İHA
        'center': (500, 280),              # Merkez
        'distance': 35.2                   # 35.2 metre uzakta
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
```

### Target Tracker Filtreleme (target_tracker.py)

```python
# detect_target_uav() metodu sadece İHA'yı seçer:

# Filtreleme kriterleri:
# 1. class_id == TARGET_CLASS_ID (config.py'de 2 olarak ayarlanmış)
# 2. confidence >= MIN_CONFIDENCE (0.7)

# Sonuç:
target = {
    'bbox': [450, 230, 550, 330],
    'confidence': 0.95,
    'class_id': 2,
    'class_name': 'uav',
    'center': (500, 280),      # ← Bu koordinat PID'ye gider
    'distance': 35.2           # ← Bu mesafe mod belirlemeye gider
}
```

### PID Kontrolcü Hesaplama

```python
# Frame boyutu: 640x480
# Frame merkezi: (320, 240)
# Hedef pozisyonu: (500, 280)

# Hata hesaplama:
error_x = 320 - 500 = -180 piksel  # Hedef sağda
error_y = 240 - 280 = -40 piksel   # Hedef aşağıda

# PID çıkışı:
yaw_rate = PID_x.compute(-180) = +0.35 rad/s  # Sağa dön
pitch_rate = PID_y.compute(-40) = +0.12 rad/s  # Yukarı bak

# Pixhawk'a gönderilen komut:
{
    'yaw_rate': +0.35,      # rad/s
    'pitch_rate': +0.12,    # rad/s
    'tracking_active': True
}
```

---

## 📍 WAYPOINT NAVİGASYON GÖRSELİ

```
                      WAYPOINT HARITASI
    
    Kuzey ↑
          │
          │         WP2 (Arama 1)
          │           ●  60m
          │          /│\
          │         / │ \
          │        /  │  \  125.3m (Mevcut mesafe)
          │       /   │   \
          │      /    │    \
          │     /     │     \
          │    /      │      \
          │   /       │       \
          │  /        │        \
          │ /         │         \
          │/          │          \
    ──────●───────────●───────────●──────── Doğu →
         WP1        İHA         WP3
       (Kalkış)   (Mevcut)    (Arama 2)
        50m      Konum: 39.123456, 35.654321
                 İrtifa: 58.2m
                 Heading: 45.2° (KD)
          │
          │         WP4 (Arama 3)
          │           ●  55m
          │
          │
          │         WP5 (Dönüş)
          │           ●  50m
          │
    Güney ↓

    Görev Durumu:
    ✅ WP1 - Kalkış (Tamamlandı)
    🔄 WP2 - Arama Noktası 1 (Gidiliyor - 125.3m kaldı)
    ⏸️  WP3 - Arama Noktası 2 (Beklemede)
    ⏸️  WP4 - Arama Noktası 3 (Beklemede)
    ⏸️  WP5 - Dönüş - İniş (Beklemede)

    Cross-Track Error (CTE): 2.1m (Rotadan sapma)
    Hedef Bearing: 45.2° (Kuzeydoğu)
```

---

## 🎨 RENK VE İKON LEJANTı

```
┌─────────────────────────────────────────────────────────────┐
│  GÖRSEL KODLAMA SİSTEMİ                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  BOUNDING BOX RENKLERİ:                                     │
│  ┌──────────┐                                               │
│  │  Yeşil   │  Normal nesneler (person, car, tree, vb.)    │
│  └──────────┘                                               │
│                                                              │
│  ┏━━━━━━━━━━┓                                               │
│  ┃  Kırmızı ┃  Hedef İHA (TARGET_CLASS_ID)                 │
│  ┗━━━━━━━━━━┛  + Yıldız işareti (★)                        │
│                                                              │
│  ┌──────────┐                                               │
│  │  Turuncu │  Kritik engel (< 2m)                         │
│  │    ⚠️    │  + Uyarı işareti                             │
│  └──────────┘                                               │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  MOD İKONLARI:                                              │
│  🔍  SEARCH    - Arama modu (Mavi)                          │
│  🎯  TRACK     - Takip modu (Yeşil)                         │
│  ⚔️  ATTACK    - Saldırı modu (Turuncu)                     │
│  🏠  RETURN    - Dönüş modu (Sarı)                          │
│  🚨  EMERGENCY - Acil kaçış modu (Kırmızı)                  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DURUM İKONLARI:                                            │
│  ✅  Başarılı / Aktif                                       │
│  ❌  Hata / Pasif                                           │
│  ⏸️  Beklemede                                              │
│  🔄  Değişim / Geçiş                                        │
│  ⚠️  Uyarı                                                  │
│  ⏳  Bekleme (Loiter)                                       │
│  🏁  Tamamlandı                                             │
│  ▶️  Başlat                                                 │
│  ⏹️  Durdur                                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Not:** Gerçek GUI PyQt5 ile oluşturulmuştur ve bu ASCII görseller sadece örnek amaçlıdır.
Sistemi çalıştırdığınızda gerçek, renkli ve interaktif arayüzü göreceksiniz!
