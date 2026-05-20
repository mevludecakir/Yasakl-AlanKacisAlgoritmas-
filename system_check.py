"""
Sistem Sağlık Kontrolü (System Health Check)

Bu script, sistem başlatılmadan önce tüm gereksinimlerin karşılandığını doğrular.

Kontroller:
- Python sürümü
- Gerekli paketler
- Kamera erişimi
- YOLO model dosyası
- MAVLink portu (opsiyonel)
- Konfigürasyon geçerliliği
- Klasör yapısı

Kullanım:
    python3 system_check.py
"""

import sys
import os
import subprocess
from pathlib import Path


class Colors:
    """Terminal renk kodları."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Başlık yazdır."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_check(name, status, message=""):
    """Kontrol sonucunu yazdır."""
    if status:
        icon = f"{Colors.GREEN}✅{Colors.RESET}"
        status_text = f"{Colors.GREEN}OK{Colors.RESET}"
    else:
        icon = f"{Colors.RED}❌{Colors.RESET}"
        status_text = f"{Colors.RED}FAIL{Colors.RESET}"
    
    print(f"{icon} {name:.<50} {status_text}")
    if message:
        print(f"   {Colors.YELLOW}→ {message}{Colors.RESET}")


def check_python_version():
    """Python sürümünü kontrol et."""
    version = sys.version_info
    required = (3, 8)
    
    if version >= required:
        print_check(
            "Python Sürümü",
            True,
            f"Python {version.major}.{version.minor}.{version.micro}"
        )
        return True
    else:
        print_check(
            "Python Sürümü",
            False,
            f"Python {version.major}.{version.minor} (>= 3.8 gerekli)"
        )
        return False


def check_packages():
    """Gerekli paketleri kontrol et."""
    required_packages = [
        'cv2',
        'numpy',
        'torch',
        'ultralytics',
        'pymavlink',
        'PyQt5',
        'loguru'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if not missing:
        print_check("Gerekli Paketler", True, f"{len(required_packages)} paket yüklü")
        return True
    else:
        print_check(
            "Gerekli Paketler",
            False,
            f"Eksik: {', '.join(missing)}"
        )
        print(f"   {Colors.YELLOW}→ Yüklemek için: pip3 install {' '.join(missing)}{Colors.RESET}")
        return False


def check_camera():
    """Kamera erişimini kontrol et."""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print_check("Kamera Erişimi", True, "Kamera ID 0 çalışıyor")
                return True
        
        print_check("Kamera Erişimi", False, "Kamera açılamadı")
        print(f"   {Colors.YELLOW}→ Kontrol: ls /dev/video*{Colors.RESET}")
        return False
    except Exception as e:
        print_check("Kamera Erişimi", False, str(e))
        return False


def check_yolo_model():
    """YOLO model dosyasını kontrol et."""
    model_path = Path("models/yolov11.pt")
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print_check("YOLO Modeli", True, f"{size_mb:.1f} MB")
        return True
    else:
        print_check("YOLO Modeli", False, "models/yolov11.pt bulunamadı")
        print(f"   {Colors.YELLOW}→ İndirmek için:{Colors.RESET}")
        print(f"   {Colors.YELLOW}   wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov11n.pt -O models/yolov11.pt{Colors.RESET}")
        return False


def check_mavlink_port():
    """MAVLink portunu kontrol et (opsiyonel)."""
    ports = ["/dev/ttyACM0", "/dev/ttyUSB0", "COM3", "COM4"]
    
    for port in ports:
        if os.path.exists(port):
            print_check("MAVLink Portu", True, f"{port} mevcut")
            return True
    
    print_check("MAVLink Portu", False, "Port bulunamadı (Simülasyon için sorun değil)")
    return False  # Opsiyonel, False dönse de devam edilebilir


def check_config():
    """Konfigürasyon dosyasını kontrol et."""
    try:
        from config import validate_config
        if validate_config():
            print_check("Konfigürasyon", True, "config.py geçerli")
            return True
        else:
            print_check("Konfigürasyon", False, "config.py doğrulama başarısız")
            return False
    except Exception as e:
        print_check("Konfigürasyon", False, str(e))
        return False


def check_directories():
    """Gerekli klasörleri kontrol et."""
    required_dirs = ["models", "missions", "logs"]
    missing = []
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing.append(dir_name)
            Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    if not missing:
        print_check("Klasör Yapısı", True, "Tüm klasörler mevcut")
        return True
    else:
        print_check("Klasör Yapısı", True, f"Oluşturuldu: {', '.join(missing)}")
        return True


def check_mission_files():
    """Örnek görev dosyasını kontrol et."""
    mission_path = Path("missions/example_mission.json")
    
    if mission_path.exists():
        print_check("Örnek Görev", True, "example_mission.json mevcut")
        return True
    else:
        print_check("Örnek Görev", False, "example_mission.json bulunamadı")
        return False


def main():
    """Ana kontrol fonksiyonu."""
    print_header("SİSTEM SAĞLIK KONTROLÜ")
    
    results = {}
    
    # Kritik kontroller
    print(f"\n{Colors.BOLD}📋 KRİTİK KONTROLLER{Colors.RESET}")
    results['python'] = check_python_version()
    results['packages'] = check_packages()
    results['yolo'] = check_yolo_model()
    results['config'] = check_config()
    results['dirs'] = check_directories()
    
    # Donanım kontrolleri
    print(f"\n{Colors.BOLD}🔧 DONANIM KONTROLLER İ{Colors.RESET}")
    results['camera'] = check_camera()
    results['mavlink'] = check_mavlink_port()  # Opsiyonel
    
    # Opsiyonel kontroller
    print(f"\n{Colors.BOLD}📁 OPSİYONEL KONTROLLER{Colors.RESET}")
    results['mission'] = check_mission_files()
    
    # Özet
    print_header("SONUÇ")
    
    critical_checks = ['python', 'packages', 'yolo', 'config', 'dirs', 'camera']
    critical_passed = sum(results[k] for k in critical_checks)
    critical_total = len(critical_checks)
    
    optional_checks = ['mavlink', 'mission']
    optional_passed = sum(results.get(k, False) for k in optional_checks)
    optional_total = len(optional_checks)
    
    print(f"Kritik Kontroller: {critical_passed}/{critical_total}")
    print(f"Opsiyonel Kontroller: {optional_passed}/{optional_total}")
    
    if critical_passed == critical_total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ SİSTEM HAZIR!{Colors.RESET}")
        print(f"{Colors.GREEN}Sistemi başlatmak için: python3 main.py{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SİSTEM HAZIR DEĞİL!{Colors.RESET}")
        print(f"{Colors.RED}Lütfen yukarıdaki hataları düzeltin.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
