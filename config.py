"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
Konfigürasyon Modülü

Bu modül, sistemin tüm parametrelerini merkezi bir konumda tutar.
Kamera ayarları, YOLO model parametreleri, APF algoritma sabitleri,
MAVLink bağlantı bilgileri ve GUI günceleme hızları burada tanımlanır.

Author: Computer Engineering
Platform: NVIDIA Jetson Nano
"""

import os

# ============================================================================
# KAMERA AYARLARI
# ============================================================================
class CameraConfig:
    """Kamera ve görüntü işleme parametreleri"""
    
    # Kamera kaynağı (0: USB kamera, 'nvarguscamerasrc': CSI kamera)
    CAMERA_SOURCE = 0
    
    # Görüntü çözünürlüğü
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    
    # FPS (Saniyedeki kare sayısı)
    FPS = 30
    
    # CSI kamera için GStreamer pipeline (Jetson Nano CSI kamera kullanıyorsanız)
    CSI_PIPELINE = (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, "
        "format=(string)NV12, framerate=(fraction)30/1 ! "
        "nvvidconv flip-method=0 ! "
        "video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
    )


# ============================================================================
# YOLO MODEL AYARLARI
# ============================================================================
class YOLOConfig:
    """YOLOv11 model ve tespit parametreleri"""
    
    # Model dosya yolu
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "yolov11.pt")
    
    # TensorRT optimizasyonu için engine dosyası
    TENSORRT_ENGINE_PATH = os.path.join(os.path.dirname(__file__), "models", "yolov11.engine")
    
    # Güven eşiği (0.0 - 1.0 arası, düşük değer daha fazla tespit)
    CONFIDENCE_THRESHOLD = 0.5
    
    # NMS (Non-Maximum Suppression) eşiği
    NMS_THRESHOLD = 0.4
    
    # Maksimum tespit sayısı
    MAX_DETECTIONS = 100
    
    # TensorRT kullan (Jetson Nano için önerilir)
    USE_TENSORRT = True
    
    # CUDA cihaz ID
    DEVICE = 0  # GPU 0
    
    # Tespit edilecek sınıflar (None: tüm sınıflar, liste: belirli sınıflar)
    # Örnek: [0, 1, 2] sadece ilk 3 sınıfı tespit eder
    DETECT_CLASSES = None
    
    # Görüntü boyutu (model girişi için)
    INPUT_SIZE = 640


# ============================================================================
# ARTIFICIAL POTENTIAL FIELDS (APF) AYARLARI
# ============================================================================
class NavigationConfig:
    """Yapay Potansiyel Alanlar algoritma parametreleri"""
    
    # Çekici kuvvet kazancı (hedef noktaya çekim)
    K_ATTRACTIVE = 1.0
    
    # İtici kuvvet kazancı (engellerden kaçış)
    K_REPULSIVE = 50.0
    
    # Güvenli mesafe (metre) - Bu mesafenin altında itici kuvvet aktif olur
    SAFE_DISTANCE = 5.0
    
    # Kritik mesafe (metre) - Bu mesafenin altında acil kaçış manevrası
    CRITICAL_DISTANCE = 2.0
    
    # Maksimum sapma açısı (derece) - Engelden kaçış için maksimum yön değişikliği
    MAX_DEVIATION_ANGLE = 45.0
    
    # Minimum sapma açısı (derece) - Algılama hassasiyeti
    MIN_DEVIATION_ANGLE = 5.0
    
    # Engel etki alanı genişliği (piksel) - Bounding box genişletme faktörü
    OBSTACLE_INFLUENCE_FACTOR = 1.5
    
    # Hız azaltma faktörü (engele yaklaşırken)
    SPEED_REDUCTION_FACTOR = 0.5
    
    # Hedef konum (varsayılan, GPS koordinatları)
    DEFAULT_GOAL_LAT = 0.0
    DEFAULT_GOAL_LON = 0.0
    DEFAULT_GOAL_ALT = 10.0  # metre


# ============================================================================
# HEDEF TAKİP AYARLARI (TEKNOFEST)
# ============================================================================
class TargetTrackingConfig:
    """Hedef İHA takip parametreleri"""
    
    # Hedef sınıf ID (YOLO model sınıfı)
    TARGET_CLASS_ID = 2  # İHA sınıfı (modelinize göre ayarlayın)
    
    # Minimum güven skoru
    MIN_CONFIDENCE = 0.7
    
    # PID kontrolcü parametreleri (Yaw - X ekseni)
    PID_KP = 0.5
    PID_KI = 0.1
    PID_KD = 0.2
    
    # PID kontrolcü parametreleri (Pitch - Y ekseni)
    PID_KP_PITCH = 0.3
    PID_KI_PITCH = 0.05
    PID_KD_PITCH = 0.15
    
    # Maksimum yaw açısal hızı (rad/s)
    MAX_YAW_RATE = 0.5
    
    # Maksimum pitch açısal hızı (rad/s)
    MAX_PITCH_RATE = 0.3
    
    # Maksimum takip mesafesi (metre)
    MAX_TRACKING_DISTANCE = 100.0
    
    # İdeal takip mesafesi (metre)
    IDEAL_TRACKING_DISTANCE = 25.0
    
    # Hedef kaybolma zaman aşımı (saniye)
    TARGET_LOST_TIMEOUT = 3.0
    
    # Hedef geçmişi uzunluğu (hız tahmini için)
    HISTORY_LENGTH = 10


# ============================================================================
# WAYPOINT NAVİGASYON AYARLARI (TEKNOFEST)
# ============================================================================
class WaypointConfig:
    """GPS waypoint navigasyon parametreleri"""
    
    # Waypoint yarıçapı (metre) - Bu mesafenin içinde waypoint'e ulaşıldı sayılır
    WAYPOINT_RADIUS = 5.0
    
    # İrtifa toleransı (metre)
    ALTITUDE_TOLERANCE = 3.0
    
    # Maksimum rota sapması (metre)
    MAX_ROUTE_DEVIATION = 10.0
    
    # Varsayılan loiter süresi (saniye)
    DEFAULT_LOITER_TIME = 5.0
    
    # Waypoint geçiş hızı (m/s)
    WAYPOINT_TRANSITION_SPEED = 5.0


# ============================================================================
# GÖREV PLANLAMA AYARLARI (TEKNOFEST)
# ============================================================================
class MissionConfig:
    """Görev ve uçuş modu parametreleri"""
    
    # Uçuş modları
    FLIGHT_MODES = ['SEARCH', 'TRACK', 'ATTACK', 'RETURN', 'EMERGENCY']
    
    # Arama irtifası (metre)
    SEARCH_ALTITUDE = 50.0
    
    # Saldırı mesafesi (metre) - Bu mesafenin altında saldırı modu
    ATTACK_DISTANCE = 20.0
    
    # Dönüş batarya eşiği (%)
    RETURN_BATTERY_THRESHOLD = 20
    
    # Arama deseni tipi ('grid', 'spiral', 'random')
    SEARCH_PATTERN = 'grid'
    
    # Arama deseni boyutu (metre)
    SEARCH_AREA_SIZE = 200.0
    
    # Üs konumu (GPS koordinatları)
    HOME_LAT = 0.0
    HOME_LON = 0.0
    HOME_ALT = 0.0


# APF konfigürasyonu için alias (geriye dönük uyumluluk)
APFConfig = NavigationConfig


# ============================================================================
# MAVLINK BAĞLANTI AYARLARI
# ============================================================================
class MAVLinkConfig:
    """Pixhawk iletişim parametreleri"""
    
    # Seri port bağlantısı
    CONNECTION_STRING = "/dev/ttyACM0"  # Linux/Jetson
    # Windows için: "COM3"
    # UDP için: "udp:127.0.0.1:14550"
    
    # Baud rate
    BAUD_RATE = 57600
    
    # Bağlantı zaman aşımı (saniye)
    CONNECTION_TIMEOUT = 10
    
    # Heartbeat gönderme aralığı (saniye)
    HEARTBEAT_INTERVAL = 1.0
    
    # Telemetri güncelleme hızı (Hz)
    TELEMETRY_UPDATE_RATE = 10
    
    # Komut gönderme zaman aşımı (saniye)
    COMMAND_TIMEOUT = 5
    
    # Sistem ID
    SYSTEM_ID = 1
    
    # Component ID
    COMPONENT_ID = 1
    
    # Otomatik mod için flight mode
    AUTO_MODE = "GUIDED"


# ============================================================================
# GUI AYARLARI
# ============================================================================
class GUIConfig:
    """PyQt5 arayüz parametreleri"""
    
    # Pencere boyutları
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    
    # Video güncelleme hızı (ms)
    VIDEO_UPDATE_INTERVAL = 33  # ~30 FPS
    
    # Telemetri güncelleme hızı (ms)
    TELEMETRY_UPDATE_INTERVAL = 100  # 10 Hz
    
    # Bounding box rengi (BGR formatı)
    BBOX_COLOR = (0, 255, 0)  # Yeşil
    
    # Bounding box kalınlığı (piksel)
    BBOX_THICKNESS = 2
    
    # Metin rengi (BGR formatı)
    TEXT_COLOR = (255, 255, 255)  # Beyaz
    
    # Metin arka plan rengi (BGR formatı)
    TEXT_BG_COLOR = (0, 0, 0)  # Siyah
    
    # Font ölçeği
    FONT_SCALE = 0.5
    
    # Font kalınlığı
    FONT_THICKNESS = 1
    
    # FPS göster
    SHOW_FPS = True
    
    # Tespit sayısını göster
    SHOW_DETECTION_COUNT = True


# ============================================================================
# LOGLAMA AYARLARI
# ============================================================================
class LogConfig:
    """Sistem loglama parametreleri"""
    
    # Log dizini
    LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
    
    # Log dosya formatı
    LOG_FILE_FORMAT = "uav_system_{time:YYYY-MM-DD}.log"
    
    # Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_LEVEL = "INFO"
    
    # Konsola log yazdır
    LOG_TO_CONSOLE = True
    
    # Dosyaya log yazdır
    LOG_TO_FILE = True
    
    # Log rotasyonu (MB)
    LOG_ROTATION = "10 MB"
    
    # Log saklama süresi (gün)
    LOG_RETENTION = "7 days"


# ============================================================================
# SİSTEM AYARLARI
# ============================================================================
class SystemConfig:
    """Genel sistem parametreleri"""
    
    # Ana döngü frekansı (Hz)
    MAIN_LOOP_FREQUENCY = 20
    
    # Otonom mod aktif
    AUTONOMOUS_MODE_ENABLED = True
    
    # Acil durum durdurma aktif
    EMERGENCY_STOP_ENABLED = True
    
    # Simülasyon modu (gerçek donanım olmadan test için)
    SIMULATION_MODE = False
    
    # Performans metrikleri toplama
    COLLECT_PERFORMANCE_METRICS = True
    
    # Hata sonrası yeniden başlatma denemesi
    MAX_RESTART_ATTEMPTS = 3


# ============================================================================
# KONFİGÜRASYON DOĞRULAMA
# ============================================================================
def validate_config():
    """
    Konfigürasyon parametrelerinin geçerliliğini kontrol eder.
    
    Returns:
        bool: Konfigürasyon geçerliyse True, değilse False
    """
    errors = []
    
    # YOLO model dosyası kontrolü
    if not SystemConfig.SIMULATION_MODE:
        if not os.path.exists(YOLOConfig.MODEL_PATH):
            errors.append(f"YOLO model dosyası bulunamadı: {YOLOConfig.MODEL_PATH}")
    
    # Log dizini kontrolü
    if not os.path.exists(LogConfig.LOG_DIR):
        try:
            os.makedirs(LogConfig.LOG_DIR)
        except Exception as e:
            errors.append(f"Log dizini oluşturulamadı: {e}")
    
    # Parametre aralık kontrolleri
    if not (0.0 <= YOLOConfig.CONFIDENCE_THRESHOLD <= 1.0):
        errors.append("YOLO güven eşiği 0.0-1.0 arasında olmalıdır")
    
    if NavigationConfig.CRITICAL_DISTANCE >= NavigationConfig.SAFE_DISTANCE:
        errors.append("Kritik mesafe, güvenli mesafeden küçük olmalıdır")
    
    if NavigationConfig.MAX_DEVIATION_ANGLE <= NavigationConfig.MIN_DEVIATION_ANGLE:
        errors.append("Maksimum sapma açısı, minimum sapma açısından büyük olmalıdır")
    
    # Hata varsa yazdır
    if errors:
        print("⚠️  Konfigürasyon Hataları:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Konfigürasyon doğrulandı")
    return True


if __name__ == "__main__":
    # Konfigürasyon test
    print("=" * 60)
    print("OTONOM İHA SİSTEMİ - KONFİGÜRASYON TEST")
    print("=" * 60)
    validate_config()
