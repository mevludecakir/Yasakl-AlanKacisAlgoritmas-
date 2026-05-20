"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
Waypoint Navigasyon Modülü (Waypoint Navigator Module)

TEKNOFEST Savaşan İHA Yarışması için geliştirilmiştir.

Bu modül, GPS waypoint'ler üzerinden otonom rota takibi yapar.

Özellikler:
- GPS waypoint yönetimi
- Waypoint sırası ve geçiş mantığı
- Rota sapma kontrolü (cross-track error)
- Dinamik rota planlaması
- Loiter (bekleme) modu

Author: Computer Engineering
Platform: NVIDIA Jetson Nano + Pixhawk
Competition: TEKNOFEST Savaşan İHA
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import time
import json

from config import WaypointConfig


# ============================================================================
# WAYPOINT CLASS
# ============================================================================
class Waypoint:
    """Tek bir waypoint'i temsil eder."""
    
    def __init__(self, lat: float, lon: float, alt: float, name: str = "", loiter_time: float = 0.0):
        """
        Waypoint başlatıcı.
        
        Args:
            lat: Enlem (derece)
            lon: Boylam (derece)
            alt: İrtifa (metre)
            name: Waypoint adı
            loiter_time: Bu noktada bekleme süresi (saniye)
        """
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.name = name
        self.loiter_time = loiter_time
        self.reached = False
        self.reached_time = None
    
    def to_dict(self) -> Dict:
        """Waypoint'i dictionary'e dönüştürür."""
        return {
            'lat': self.lat,
            'lon': self.lon,
            'alt': self.alt,
            'name': self.name,
            'loiter_time': self.loiter_time,
            'reached': self.reached
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Waypoint':
        """Dictionary'den waypoint oluşturur."""
        return Waypoint(
            lat=data['lat'],
            lon=data['lon'],
            alt=data['alt'],
            name=data.get('name', ''),
            loiter_time=data.get('loiter_time', 0.0)
        )
    
    def __repr__(self):
        return f"WP({self.name}: {self.lat:.6f}, {self.lon:.6f}, {self.alt:.1f}m)"


# ============================================================================
# WAYPOINT NAVIGATOR CLASS
# ============================================================================
class WaypointNavigator:
    """
    GPS waypoint navigasyon sınıfı.
    """
    
    def __init__(self):
        """WaypointNavigator başlatıcı."""
        self.waypoints: List[Waypoint] = []
        self.current_waypoint_index = 0
        self.mission_active = False
        self.mission_completed = False
        
        print("✅ WaypointNavigator başlatıldı")
    
    def load_mission_from_file(self, filepath: str) -> bool:
        """
        Görev dosyasından waypoint'leri yükler.
        
        Args:
            filepath: JSON görev dosyası yolu
        
        Returns:
            Başarılı ise True
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.waypoints = [Waypoint.from_dict(wp) for wp in data['waypoints']]
            self.current_waypoint_index = 0
            self.mission_active = False
            self.mission_completed = False
            
            print(f"✅ Görev yüklendi: {len(self.waypoints)} waypoint")
            for i, wp in enumerate(self.waypoints):
                print(f"   WP{i+1}: {wp}")
            
            return True
        
        except Exception as e:
            print(f"❌ Görev yükleme hatası: {e}")
            return False
    
    def load_mission_from_list(self, waypoints: List[Dict]):
        """
        Liste'den waypoint'leri yükler.
        
        Args:
            waypoints: Waypoint dictionary listesi
        """
        self.waypoints = [Waypoint.from_dict(wp) for wp in waypoints]
        self.current_waypoint_index = 0
        self.mission_active = False
        self.mission_completed = False
        
        print(f"✅ Görev yüklendi: {len(self.waypoints)} waypoint")
    
    def start_mission(self):
        """Görevi başlatır."""
        if not self.waypoints:
            print("⚠️  Waypoint yok, görev başlatılamadı")
            return False
        
        self.mission_active = True
        self.mission_completed = False
        self.current_waypoint_index = 0
        
        # Tüm waypoint'leri sıfırla
        for wp in self.waypoints:
            wp.reached = False
            wp.reached_time = None
        
        print(f"▶️  Görev başlatıldı - İlk hedef: {self.waypoints[0]}")
        return True
    
    def stop_mission(self):
        """Görevi durdurur."""
        self.mission_active = False
        print("⏹️  Görev durduruldu")
    
    def get_current_waypoint(self) -> Optional[Waypoint]:
        """
        Mevcut waypoint'i döndürür.
        
        Returns:
            Mevcut waypoint veya None
        """
        if not self.mission_active or self.mission_completed:
            return None
        
        if 0 <= self.current_waypoint_index < len(self.waypoints):
            return self.waypoints[self.current_waypoint_index]
        
        return None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        İki GPS koordinatı arasındaki mesafeyi hesaplar (Haversine formülü).
        
        Args:
            lat1, lon1: İlk nokta (derece)
            lat2, lon2: İkinci nokta (derece)
        
        Returns:
            Mesafe (metre)
        """
        R = 6371000  # Dünya yarıçapı (metre)
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        distance = R * c
        return distance
    
    def calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        İki GPS koordinatı arasındaki yönü hesaplar.
        
        Args:
            lat1, lon1: İlk nokta (derece)
            lat2, lon2: İkinci nokta (derece)
        
        Returns:
            Yön (derece, 0-360, kuzey=0)
        """
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlon = np.radians(lon2 - lon1)
        
        y = np.sin(dlon) * np.cos(lat2_rad)
        x = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(dlon)
        
        bearing = np.degrees(np.arctan2(y, x))
        bearing = (bearing + 360) % 360  # 0-360 aralığına normalize et
        
        return bearing
    
    def calculate_cross_track_error(self, current_pos: Dict, prev_wp: Waypoint, next_wp: Waypoint) -> float:
        """
        Rota sapmasını (cross-track error) hesaplar.
        
        Args:
            current_pos: Mevcut konum {'lat', 'lon'}
            prev_wp: Önceki waypoint
            next_wp: Sonraki waypoint
        
        Returns:
            Cross-track error (metre, pozitif=sağda, negatif=solda)
        """
        R = 6371000  # Dünya yarıçapı (metre)
        
        # Koordinatları radyana çevir
        lat1 = np.radians(prev_wp.lat)
        lon1 = np.radians(prev_wp.lon)
        lat2 = np.radians(next_wp.lat)
        lon2 = np.radians(next_wp.lon)
        lat3 = np.radians(current_pos['lat'])
        lon3 = np.radians(current_pos['lon'])
        
        # Mesafeler
        d13 = self.calculate_distance(prev_wp.lat, prev_wp.lon, current_pos['lat'], current_pos['lon']) / R
        
        # Yönler
        bearing_13 = np.radians(self.calculate_bearing(prev_wp.lat, prev_wp.lon, current_pos['lat'], current_pos['lon']))
        bearing_12 = np.radians(self.calculate_bearing(prev_wp.lat, prev_wp.lon, next_wp.lat, next_wp.lon))
        
        # Cross-track error
        cte = np.arcsin(np.sin(d13) * np.sin(bearing_13 - bearing_12)) * R
        
        return cte
    
    def check_waypoint_reached(self, current_pos: Dict) -> bool:
        """
        Mevcut waypoint'e ulaşıldı mı kontrol eder.
        
        Args:
            current_pos: Mevcut konum {'lat', 'lon', 'alt'}
        
        Returns:
            Ulaşıldı ise True
        """
        current_wp = self.get_current_waypoint()
        
        if current_wp is None:
            return False
        
        # Mesafe hesapla
        distance = self.calculate_distance(
            current_pos['lat'], current_pos['lon'],
            current_wp.lat, current_wp.lon
        )
        
        # İrtifa farkı
        alt_diff = abs(current_pos['alt'] - current_wp.alt)
        
        # Waypoint yarıçapı içinde mi?
        if distance <= WaypointConfig.WAYPOINT_RADIUS and alt_diff <= WaypointConfig.ALTITUDE_TOLERANCE:
            if not current_wp.reached:
                current_wp.reached = True
                current_wp.reached_time = time.time()
                print(f"✅ Waypoint {self.current_waypoint_index + 1} ulaşıldı: {current_wp.name}")
            
            return True
        
        return False
    
    def update_navigation(self, current_pos: Dict) -> Dict:
        """
        Navigasyon durumunu günceller ve komutları hesaplar.
        
        Args:
            current_pos: Mevcut konum {'lat', 'lon', 'alt'}
        
        Returns:
            Navigasyon komutu:
            {
                'active': bool,
                'target_bearing': float,  # Hedef yön (derece)
                'distance_to_wp': float,  # Waypoint'e mesafe (metre)
                'cross_track_error': float,  # Rota sapması (metre)
                'altitude_error': float,  # İrtifa hatası (metre)
                'current_wp_index': int,
                'total_waypoints': int,
                'mission_completed': bool,
                'loitering': bool  # Bekleme modunda mı?
            }
        """
        if not self.mission_active or self.mission_completed:
            return {
                'active': False,
                'target_bearing': 0.0,
                'distance_to_wp': 0.0,
                'cross_track_error': 0.0,
                'altitude_error': 0.0,
                'current_wp_index': 0,
                'total_waypoints': len(self.waypoints),
                'mission_completed': self.mission_completed,
                'loitering': False
            }
        
        current_wp = self.get_current_waypoint()
        
        if current_wp is None:
            return {'active': False}
        
        # Waypoint'e ulaşıldı mı kontrol et
        reached = self.check_waypoint_reached(current_pos)
        
        # Loiter kontrolü
        loitering = False
        if reached and current_wp.loiter_time > 0:
            elapsed = time.time() - current_wp.reached_time
            if elapsed < current_wp.loiter_time:
                loitering = True
                print(f"⏳ Loiter: {elapsed:.1f}/{current_wp.loiter_time}s")
            else:
                # Loiter tamamlandı, sonraki waypoint'e geç
                self._advance_to_next_waypoint()
                current_wp = self.get_current_waypoint()
        elif reached and current_wp.loiter_time == 0:
            # Loiter yok, direkt sonraki waypoint'e geç
            self._advance_to_next_waypoint()
            current_wp = self.get_current_waypoint()
        
        if current_wp is None:
            # Görev tamamlandı
            self.mission_completed = True
            print("🏁 Görev tamamlandı!")
            return {
                'active': False,
                'mission_completed': True
            }
        
        # Mesafe ve yön hesapla
        distance = self.calculate_distance(
            current_pos['lat'], current_pos['lon'],
            current_wp.lat, current_wp.lon
        )
        
        bearing = self.calculate_bearing(
            current_pos['lat'], current_pos['lon'],
            current_wp.lat, current_wp.lon
        )
        
        # Cross-track error (rota sapması)
        cte = 0.0
        if self.current_waypoint_index > 0:
            prev_wp = self.waypoints[self.current_waypoint_index - 1]
            cte = self.calculate_cross_track_error(current_pos, prev_wp, current_wp)
        
        # İrtifa hatası
        alt_error = current_wp.alt - current_pos['alt']
        
        return {
            'active': True,
            'target_bearing': bearing,
            'distance_to_wp': distance,
            'cross_track_error': cte,
            'altitude_error': alt_error,
            'current_wp_index': self.current_waypoint_index,
            'total_waypoints': len(self.waypoints),
            'mission_completed': False,
            'loitering': loitering
        }
    
    def _advance_to_next_waypoint(self):
        """Sonraki waypoint'e geçer."""
        self.current_waypoint_index += 1
        
        if self.current_waypoint_index < len(self.waypoints):
            next_wp = self.waypoints[self.current_waypoint_index]
            print(f"➡️  Sonraki waypoint: WP{self.current_waypoint_index + 1} - {next_wp.name}")
        else:
            print("🏁 Tüm waypoint'ler tamamlandı")
    
    def get_navigation_status(self, nav_data: Dict) -> str:
        """
        Navigasyon durumunu açıklayan metin döndürür.
        
        Args:
            nav_data: update_navigation() çıktısı
        
        Returns:
            Durum metni
        """
        if not nav_data['active']:
            if nav_data.get('mission_completed', False):
                return "🏁 Görev Tamamlandı"
            return "⏸️  Navigasyon Pasif"
        
        if nav_data['loitering']:
            return f"⏳ Loiter - WP{nav_data['current_wp_index'] + 1}"
        
        return (f"🧭 WP{nav_data['current_wp_index'] + 1}/{nav_data['total_waypoints']} - "
                f"{nav_data['distance_to_wp']:.1f}m - {nav_data['target_bearing']:.0f}°")


# ============================================================================
# TEST FONKSİYONU
# ============================================================================
def test_waypoint_navigator():
    """Waypoint navigator modülünü test eder."""
    print("=" * 60)
    print("WAYPOINT NAVİGATOR MODÜLÜ TEST")
    print("=" * 60)
    
    # WaypointNavigator oluştur
    navigator = WaypointNavigator()
    
    # Test waypoint'leri
    test_waypoints = [
        {'lat': 39.123000, 'lon': 35.456000, 'alt': 50.0, 'name': 'Başlangıç', 'loiter_time': 0.0},
        {'lat': 39.124000, 'lon': 35.457000, 'alt': 60.0, 'name': 'Arama Noktası 1', 'loiter_time': 5.0},
        {'lat': 39.125000, 'lon': 35.458000, 'alt': 55.0, 'name': 'Arama Noktası 2', 'loiter_time': 0.0},
        {'lat': 39.123500, 'lon': 35.456500, 'alt': 50.0, 'name': 'Dönüş', 'loiter_time': 0.0},
    ]
    
    navigator.load_mission_from_list(test_waypoints)
    navigator.start_mission()
    
    # Test senaryoları
    print("\n📋 Test Senaryoları:\n")
    
    # Senaryo 1: Başlangıç noktası
    print("1️⃣  Senaryo: Başlangıç noktasından WP1'e gidiş")
    current_pos = {'lat': 39.123000, 'lon': 35.456000, 'alt': 50.0}
    nav_data = navigator.update_navigation(current_pos)
    print(f"   Durum: {navigator.get_navigation_status(nav_data)}")
    print(f"   Hedef Yön: {nav_data['target_bearing']:.1f}°")
    print(f"   Mesafe: {nav_data['distance_to_wp']:.1f}m\n")
    
    # Senaryo 2: WP1'e yaklaşma
    print("2️⃣  Senaryo: WP1'e yaklaşma")
    current_pos = {'lat': 39.123900, 'lon': 35.456900, 'alt': 58.0}
    nav_data = navigator.update_navigation(current_pos)
    print(f"   Durum: {navigator.get_navigation_status(nav_data)}")
    print(f"   Mesafe: {nav_data['distance_to_wp']:.1f}m")
    print(f"   İrtifa Hatası: {nav_data['altitude_error']:.1f}m\n")
    
    # Senaryo 3: WP1'e ulaşma
    print("3️⃣  Senaryo: WP1'e ulaşma")
    current_pos = {'lat': 39.124000, 'lon': 35.457000, 'alt': 60.0}
    nav_data = navigator.update_navigation(current_pos)
    print(f"   Durum: {navigator.get_navigation_status(nav_data)}")
    print(f"   Waypoint Ulaşıldı: {nav_data['loitering']}\n")
    
    print("✅ Test tamamlandı")


if __name__ == "__main__":
    test_waypoint_navigator()
