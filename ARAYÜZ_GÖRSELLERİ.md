# 🖼️ Otonom İHA Sistemi - Arayüz Görselleri

## Ana Pencere Görünümü

```
╔══════════════════════════════════════════════════════════════════════════╗
║  Otonom İHA Yer Kontrol İstasyonu                                  ▭ □ ✕ ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  ┌────────────────────────────────────────────────────────────────────┐ ║
║  │ [📹 Video & Tespit] [📡 Telemetri] [🎮 Kontrol]                   │ ║
║  └────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║  ┌─ Video & Tespit Tab ────────────────────────────────────────────────┐║
║  │                                                                      │║
║  │  ┌──────────────────────────────────────────────────────────────┐  │║
║  │  │                                                              │  │║
║  │  │              [CANLI KAMERA GÖRÜNTÜSÜ]                       │  │║
║  │  │                                                              │  │║
║  │  │     ┌─────────────────┐                                     │  │║
║  │  │     │  🟢 person      │  ← Tespit edilen nesne              │  │║
║  │  │     │     0.95        │  ← Güven skoru                      │  │║
║  │  │     │     3.2m        │  ← Tahmini mesafe                   │  │║
║  │  │     └─────────────────┘                                     │  │║
║  │  │                                                              │  │║
║  │  │                        ┌──────────────┐                     │  │║
║  │  │                        │  🟢 chair    │                     │  │║
║  │  │                        │     0.87     │                     │  │║
║  │  │                        │     2.5m     │                     │  │║
║  │  │                        └──────────────┘                     │  │║
║  │  │                                                              │  │║
║  │  └──────────────────────────────────────────────────────────────┘  │║
║  │                                                                      │║
║  │  FPS: 25.3  |  Tespit: 2  |  En Yakın: 2.5m (chair)                │║
║  │                                                                      │║
║  └──────────────────────────────────────────────────────────────────────┘║
║                                                                          ║
║  Durum: ✅ Bağlı | Otonom Mod: Pasif                                    ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Tab 1: 📹 Video & Tespit (Detaylı)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VIDEO & TESPİT                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                                                                   │ │
│  │  640x480 Kamera Görüntüsü                                        │ │
│  │                                                                   │ │
│  │  • Yeşil kutular: Tespit edilen nesneler                         │ │
│  │  • Etiketler: Sınıf adı + Güven skoru                           │ │
│  │  • Mesafe: Tahmini uzaklık (metre)                              │ │
│  │                                                                   │ │
│  │  Örnek Tespit:                                                   │ │
│  │  ┌──────────────┐                                               │ │
│  │  │ person 0.95  │  ← Kişi tespit edildi, %95 güven             │ │
│  │  │    3.2m      │  ← 3.2 metre uzakta                          │ │
│  │  └──────────────┘                                               │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─ Bilgi Paneli ──────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  📊 FPS: 25.3          Anlık kare hızı                          │  │
│  │  🎯 Tespit: 2          Tespit edilen nesne sayısı               │  │
│  │  ⚠️  En Yakın: 2.5m    En yakın engelin mesafesi (chair)        │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

RENK KODLARI:
🟢 Yeşil Kutular: Güvenli tespitler (güven > 0.5)
🟡 Sarı Kutular: Orta güvenli (güven 0.3-0.5)
🔴 Kırmızı Kutular: Kritik mesafe (< 2m)
```

---

## Tab 2: 📡 Telemetri

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           TELEMETRİ                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ GPS Bilgileri ─────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  📍 Konum Bilgileri                                             │  │
│  │                                                                  │  │
│  │  Enlem:     39.123456                                           │  │
│  │  Boylam:    35.654321                                           │  │
│  │  İrtifa:    123.4 m                                             │  │
│  │  Fix:       3 (GPS Kilitli)                                     │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─ Attitude Bilgileri ────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  🧭 Yönelim ve Açı Bilgileri                                    │  │
│  │                                                                  │  │
│  │  Roll:      2.3°    (Sağ/Sol eğim)                              │  │
│  │  Pitch:    -1.5°    (İleri/Geri eğim)                           │  │
│  │  Yaw:      45.2°    (Dönüş açısı)                               │  │
│  │  Heading:  45.2°    (Pusula yönü: KD)                           │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─ Sistem Durumu ─────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  ⚙️  Uçuş Sistemi Durumu                                        │  │
│  │                                                                  │  │
│  │  Mod:       STABILIZE                                           │  │
│  │  Armed:     ❌ Hayır (Motorlar kapalı)                          │  │
│  │  Hız:       0.0 m/s                                             │  │
│  │  Batarya:   12.6V                                               │  │
│  │                                                                  │  │
│  │  Batarya Seviyesi:                                              │  │
│  │  ████████████████████ 100%                                      │  │
│  │  🟢 Tam Dolu                                                    │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

DURUM GÖSTERGELERİ:
✅ Bağlı      - MAVLink bağlantısı aktif
❌ Bağlı Değil - Bağlantı yok
🟢 Tam Dolu   - Batarya > 80%
🟡 Orta       - Batarya 40-80%
🔴 Düşük      - Batarya < 40%
```

---

## Tab 3: 🎮 Kontrol

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            KONTROL                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ Otonom Mod Kontrolü ──────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  ┌────────────────────────────────────────────────────────────┐ │   │
│  │  │                                                            │ │   │
│  │  │         ▶️  OTONOM MODU BAŞLAT                            │ │   │
│  │  │                                                            │ │   │
│  │  └────────────────────────────────────────────────────────────┘ │   │
│  │  🟢 Yeşil - Başlatmak için tıklayın                            │   │
│  │                                                                  │   │
│  │  ┌────────────────────────────────────────────────────────────┐ │   │
│  │  │                                                            │ │   │
│  │  │         ⏹️  OTONOM MODU DURDUR                            │ │   │
│  │  │                                                            │ │   │
│  │  └────────────────────────────────────────────────────────────┘ │   │
│  │  🔴 Kırmızı - Durdurmak için tıklayın (Pasif)                  │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─ Acil Durum ────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  ┌────────────────────────────────────────────────────────────┐ │   │
│  │  │                                                            │ │   │
│  │  │         🚨  ACİL DURDUR  🚨                               │ │   │
│  │  │                                                            │ │   │
│  │  └────────────────────────────────────────────────────────────┘ │   │
│  │  🟠 Turuncu - Her zaman aktif, motorları durdurur              │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─ Sistem Logları ────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  ▶️  Otonom mod başlatıldı                                     │   │
│  │  🎯 ⚠️  KAÇIŞ: SAĞ 15.3°                                       │   │
│  │  🎯 ⚠️  KAÇIŞ: SOL 12.7°                                       │   │
│  │  🎯 ✅ NORMAL İLERLEME                                         │   │
│  │  🚨 KRİTİK DURUM: En yakın engel 1.8m                          │   │
│  │  🎯 🚨 ACİL KAÇIŞ MODU                                         │   │
│  │  ⏹️  Otonom mod durduruldu                                     │   │
│  │                                                                  │   │
│  │  [Otomatik kaydırma - En son 50 log]                           │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

BUTON DURMLARI:
🟢 Yeşil  - Başlatma butonu (Aktif)
🔴 Kırmızı - Durdurma butonu (Otonom mod aktifken)
🟠 Turuncu - Acil durdur (Her zaman aktif)
⚪ Gri    - Pasif buton
```

---

## Gerçek Zamanlı Çalışma Örneği

### Senaryo: Engel Tespit ve Kaçış

```
┌─ T = 0s ────────────────────────────────────────────────────────────────┐
│ [Video Tab]                                                             │
│ ┌─────────────────────────────────┐                                     │
│ │  Kamera görüntüsü               │                                     │
│ │  (Engel yok)                    │                                     │
│ │                                 │                                     │
│ └─────────────────────────────────┘                                     │
│ FPS: 24.5 | Tespit: 0 | En Yakın: -                                    │
│                                                                         │
│ [Kontrol Tab - Loglar]                                                  │
│ ▶️  Otonom mod başlatıldı                                              │
│ 🎯 ✅ NORMAL İLERLEME                                                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─ T = 2s ────────────────────────────────────────────────────────────────┐
│ [Video Tab]                                                             │
│ ┌─────────────────────────────────┐                                     │
│ │  Kamera görüntüsü               │                                     │
│ │    🟢[person]                   │  ← Sol tarafta kişi tespit edildi   │
│ │       0.92                      │                                     │
│ │       3.5m                      │                                     │
│ └─────────────────────────────────┘                                     │
│ FPS: 25.1 | Tespit: 1 | En Yakın: 3.5m (person)                        │
│                                                                         │
│ [Kontrol Tab - Loglar]                                                  │
│ ▶️  Otonom mod başlatıldı                                              │
│ 🎯 ⚠️  KAÇIŞ: SAĞ 18.5°                                                │
│     └─ Engel solda, sağa dönülüyor                                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─ T = 4s ────────────────────────────────────────────────────────────────┐
│ [Video Tab]                                                             │
│ ┌─────────────────────────────────┐                                     │
│ │  Kamera görüntüsü               │                                     │
│ │  🔴[person]                     │  ← KRİTİK MESAFE!                   │
│ │     0.95                        │                                     │
│ │     1.5m                        │  ← 1.5m çok yakın!                  │
│ └─────────────────────────────────┘                                     │
│ FPS: 24.8 | Tespit: 1 | En Yakın: 1.5m (person) ⚠️                     │
│                                                                         │
│ [Kontrol Tab - Loglar]                                                  │
│ ▶️  Otonom mod başlatıldı                                              │
│ 🎯 ⚠️  KAÇIŞ: SAĞ 18.5°                                                │
│ 🚨 KRİTİK DURUM: En yakın engel 1.5m                                   │
│ 🎯 🚨 ACİL KAÇIŞ MODU                                                  │
│     └─ Hız azaltıldı, maksimum sapma uygulandı                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ T = 6s ────────────────────────────────────────────────────────────────┐
│ [Video Tab]                                                             │
│ ┌─────────────────────────────────┐                                     │
│ │  Kamera görüntüsü               │                                     │
│ │                  🟢[person]     │  ← Engel sağda, uzaklaşıyor         │
│ │                     0.88        │                                     │
│ │                     4.2m        │                                     │
│ └─────────────────────────────────┘                                     │
│ FPS: 25.3 | Tespit: 1 | En Yakın: 4.2m (person)                        │
│                                                                         │
│ [Kontrol Tab - Loglar]                                                  │
│ 🎯 ⚠️  KAÇIŞ: SAĞ 18.5°                                                │
│ 🚨 KRİTİK DURUM: En yakın engel 1.5m                                   │
│ 🎯 🚨 ACİL KAÇIŞ MODU                                                  │
│ 🎯 ⚠️  KAÇIŞ: SOL 8.2°                                                 │
│     └─ Engel sağda, hafif sola dönülüyor                               │
└─────────────────────────────────────────────────────────────────────────┘

┌─ T = 8s ────────────────────────────────────────────────────────────────┐
│ [Video Tab]                                                             │
│ ┌─────────────────────────────────┐                                     │
│ │  Kamera görüntüsü               │                                     │
│ │  (Engel görüş alanı dışında)    │                                     │
│ │                                 │                                     │
│ └─────────────────────────────────┘                                     │
│ FPS: 24.9 | Tespit: 0 | En Yakın: -                                    │
│                                                                         │
│ [Kontrol Tab - Loglar]                                                  │
│ 🎯 🚨 ACİL KAÇIŞ MODU                                                  │
│ 🎯 ⚠️  KAÇIŞ: SOL 8.2°                                                 │
│ 🎯 ✅ NORMAL İLERLEME                                                  │
│     └─ Engel geçildi, normal moda dönüldü                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Konsol Çıktısı (Terminal)

```
============================================================
OTONOM İHA SİSTEMİ BAŞLATILIYOR
============================================================
2026-02-07 19:35:00 | INFO     | 📋 Konfigürasyon doğrulanıyor...
2026-02-07 19:35:00 | INFO     | ✅ Konfigürasyon doğrulandı
2026-02-07 19:35:00 | INFO     | 📷 Vision modülü başlatılıyor...
📦 YOLO modeli yükleniyor: models/yolov11.pt
🚀 TensorRT optimizasyonu uygulanıyor...
   TensorRT engine oluşturuluyor (bu işlem birkaç dakika sürebilir)...
   ✅ TensorRT engine kaydedildi: models/yolov11.engine
✅ Model yükleme tamamlandı
📷 USB kamera başlatılıyor (ID: 0)...
✅ Kamera başarıyla başlatıldı
✅ VisionProcessor başlatıldı
▶️  Görüntü işleme başlatıldı
2026-02-07 19:35:05 | INFO     | 🧭 Navigation modülü başlatılıyor...
✅ ObstacleAvoidance başlatıldı
2026-02-07 19:35:05 | INFO     | 📡 Communication modülü başlatılıyor...
2026-02-07 19:35:05 | WARNING  | ⚠️  Simülasyon modu: Communication modülü devre dışı
2026-02-07 19:35:05 | INFO     | 🖥️  GUI modülü başlatılıyor...
✅ GroundControlStation başlatıldı
2026-02-07 19:35:06 | INFO     | ✅ Tüm modüller başarıyla başlatıldı
2026-02-07 19:35:06 | INFO     | ▶️  Ana sistem döngüsü başlatıldı
2026-02-07 19:35:06 | INFO     |    Döngü frekansı: 20 Hz

[GUI penceresi açıldı - Kullanıcı etkileşimi bekleniyor]

2026-02-07 19:36:10 | INFO     | ▶️  Otonom mod başlatıldı
2026-02-07 19:36:15 | INFO     | 🎯 ⚠️  KAÇIŞ: SAĞ 18.5°
2026-02-07 19:36:20 | WARNING  | 🚨 KRİTİK DURUM: En yakın engel 1.5m
2026-02-07 19:36:20 | INFO     | 🎯 🚨 ACİL KAÇIŞ MODU
2026-02-07 19:36:25 | INFO     | 🎯 ⚠️  KAÇIŞ: SOL 8.2°
2026-02-07 19:36:30 | INFO     | 🎯 ✅ NORMAL İLERLEME
```

---

## Başarı Göstergeleri

✅ **Sistem doğru çalışıyor**:
- GUI penceresi açılıyor
- Video akışı geliyor (FPS > 15)
- Engeller tespit ediliyor (yeşil kutular)
- Loglar düzgün yazılıyor
- Otonom mod başlatılabiliyor

❌ **Sorun var**:
- GUI açılmıyor → PyQt5 kurulu değil
- Video gelmiyor → Kamera bağlı değil
- FPS < 10 → Çözünürlük çok yüksek
- Tespit yok → Model yüklenmemiş

---

**Not**: Gerçek görsel oluşturma servisi şu anda meşgul olduğu için ASCII art çizimleri kullandım. Sistem çalıştığında gerçek PyQt5 arayüzü bu çizimlere çok benzer şekilde görünecektir.
