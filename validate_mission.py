"""
Görev Dosyası Validatörü (Mission File Validator)

Bu script, JSON görev dosyalarının geçerliliğini kontrol eder.

Validasyonlar:
- JSON formatı
- Gerekli alanlar
- Koordinat aralıkları
- İrtifa değerleri
- Loiter süreleri
- Waypoint sayısı

Kullanım:
    python3 validate_mission.py missions/my_mission.json
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple


class Colors:
    """Terminal renk kodları."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_error(message: str):
    """Hata mesajı yazdır."""
    print(f"{Colors.RED}❌ HATA: {message}{Colors.RESET}")


def print_warning(message: str):
    """Uyarı mesajı yazdır."""
    print(f"{Colors.YELLOW}⚠️  UYARI: {message}{Colors.RESET}")


def print_success(message: str):
    """Başarı mesajı yazdır."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_info(message: str):
    """Bilgi mesajı yazdır."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


def validate_json_format(file_path: Path) -> Tuple[bool, Dict]:
    """JSON formatını doğrula."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print_success("JSON formatı geçerli")
        return True, data
    except json.JSONDecodeError as e:
        print_error(f"JSON parse hatası: {e}")
        return False, {}
    except FileNotFoundError:
        print_error(f"Dosya bulunamadı: {file_path}")
        return False, {}
    except Exception as e:
        print_error(f"Dosya okuma hatası: {e}")
        return False, {}


def validate_required_fields(data: Dict) -> bool:
    """Gerekli alanları kontrol et."""
    required_fields = ['mission_name', 'waypoints']
    
    for field in required_fields:
        if field not in data:
            print_error(f"Gerekli alan eksik: '{field}'")
            return False
    
    print_success("Tüm gerekli alanlar mevcut")
    return True


def validate_waypoint(wp: Dict, index: int) -> bool:
    """Tek bir waypoint'i doğrula."""
    errors = []
    
    # Gerekli alanlar
    required = ['lat', 'lon', 'alt']
    for field in required:
        if field not in wp:
            errors.append(f"WP{index}: '{field}' alanı eksik")
    
    if errors:
        for error in errors:
            print_error(error)
        return False
    
    # Koordinat aralıkları
    lat = wp['lat']
    lon = wp['lon']
    alt = wp['alt']
    
    if not (-90 <= lat <= 90):
        print_error(f"WP{index}: Enlem geçersiz ({lat}°). Aralık: -90 ile 90 arası")
        return False
    
    if not (-180 <= lon <= 180):
        print_error(f"WP{index}: Boylam geçersiz ({lon}°). Aralık: -180 ile 180 arası")
        return False
    
    if not (0 <= alt <= 500):
        print_warning(f"WP{index}: İrtifa ({alt}m) olağandışı. Önerilen: 0-500m arası")
    
    # Loiter süresi (opsiyonel)
    if 'loiter_time' in wp:
        loiter = wp['loiter_time']
        if loiter < 0:
            print_error(f"WP{index}: Loiter süresi negatif olamaz ({loiter}s)")
            return False
        elif loiter > 300:
            print_warning(f"WP{index}: Loiter süresi çok uzun ({loiter}s)")
    
    return True


def validate_waypoints(waypoints: List[Dict]) -> bool:
    """Tüm waypoint'leri doğrula."""
    if not waypoints:
        print_error("Waypoint listesi boş")
        return False
    
    if len(waypoints) < 2:
        print_warning("En az 2 waypoint önerilir")
    
    if len(waypoints) > 50:
        print_warning(f"Çok fazla waypoint ({len(waypoints)}). Performans sorunları olabilir")
    
    print_info(f"Toplam {len(waypoints)} waypoint kontrol ediliyor...")
    
    all_valid = True
    for i, wp in enumerate(waypoints, 1):
        if not validate_waypoint(wp, i):
            all_valid = False
    
    if all_valid:
        print_success(f"Tüm {len(waypoints)} waypoint geçerli")
    
    return all_valid


def validate_mission_logic(waypoints: List[Dict]) -> bool:
    """Görev mantığını kontrol et."""
    warnings = []
    
    # İlk ve son waypoint mesafesi
    if len(waypoints) >= 2:
        first = waypoints[0]
        last = waypoints[-1]
        
        # Basit mesafe hesaplama (yaklaşık)
        lat_diff = abs(first['lat'] - last['lat'])
        lon_diff = abs(first['lon'] - last['lon'])
        
        if lat_diff < 0.0001 and lon_diff < 0.0001:
            print_info("İlk ve son waypoint aynı (kapalı döngü)")
        else:
            print_info("İlk ve son waypoint farklı (açık rota)")
    
    # İrtifa değişimleri
    altitudes = [wp['alt'] for wp in waypoints]
    max_alt = max(altitudes)
    min_alt = min(altitudes)
    
    if max_alt - min_alt > 100:
        print_warning(f"Büyük irtifa değişimi: {min_alt}m - {max_alt}m")
    
    return True


def validate_mission_file(file_path: str) -> bool:
    """Görev dosyasını tamamen doğrula."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}GÖREV DOSYASI VALİDASYONU{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    path = Path(file_path)
    print_info(f"Dosya: {path.name}")
    
    # 1. JSON formatı
    print(f"\n{Colors.BOLD}1. JSON Formatı{Colors.RESET}")
    valid, data = validate_json_format(path)
    if not valid:
        return False
    
    # 2. Gerekli alanlar
    print(f"\n{Colors.BOLD}2. Gerekli Alanlar{Colors.RESET}")
    if not validate_required_fields(data):
        return False
    
    # 3. Görev adı
    print(f"\n{Colors.BOLD}3. Görev Bilgileri{Colors.RESET}")
    print_info(f"Görev Adı: {data['mission_name']}")
    
    # 4. Waypoint'ler
    print(f"\n{Colors.BOLD}4. Waypoint Validasyonu{Colors.RESET}")
    if not validate_waypoints(data['waypoints']):
        return False
    
    # 5. Görev mantığı
    print(f"\n{Colors.BOLD}5. Görev Mantığı{Colors.RESET}")
    validate_mission_logic(data['waypoints'])
    
    # Özet
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}✅ GÖREV DOSYASI GEÇERLİ!{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    return True


def main():
    """Ana fonksiyon."""
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Kullanım: python3 validate_mission.py <mission_file.json>{Colors.RESET}")
        print(f"{Colors.YELLOW}Örnek: python3 validate_mission.py missions/example_mission.json{Colors.RESET}")
        return 1
    
    mission_file = sys.argv[1]
    
    try:
        if validate_mission_file(mission_file):
            print(f"{Colors.GREEN}Görev dosyası sisteme yüklenmeye hazır!{Colors.RESET}\n")
            return 0
        else:
            print(f"{Colors.RED}Görev dosyası geçersiz. Lütfen hataları düzeltin.{Colors.RESET}\n")
            return 1
    except Exception as e:
        print_error(f"Beklenmeyen hata: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
