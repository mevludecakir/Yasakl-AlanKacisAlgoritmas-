"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
Hibrit Navigasyon Modülü (Hybrid Navigation Module)

TEKNOFEST Savaşan İHA Yarışması için geliştirilmiştir.

Bu modül, engel kaçış, hedef takip ve waypoint navigasyonunu birleştirir.

Özellikler:
- Çoklu navigasyon modu yönetimi
- Öncelik sistemi (Acil > Hedef > Rota)
- Mod geçişleri (SEARCH, TRACK, ATTACK, RETURN)
- Vektör birleştirme ve optimizasyon

Author: Computer Engineering
Platform: NVIDIA Jetson Nano + Pixhawk
Competition: TEKNOFEST Savaşan İHA
"""

import numpy as np
from typing import Dict, Optional, Tuple
from enum import Enum
import time

from config import MissionConfig, TargetTrackingConfig, APFConfig


# ============================================================================
# FLIGHT MODE ENUM
# ============================================================================
class FlightMode(Enum):
    """Uçuş modları."""
    SEARCH = "SEARCH"      # Arama modu
    TRACK = "TRACK"        # Hedef takip modu
    ATTACK = "ATTACK"      # Saldırı modu
    RETURN = "RETURN"      # Dönüş modu
    EMERGENCY = "EMERGENCY"  # Acil durum


# ============================================================================
# HYBRID NAVIGATOR CLASS
# ============================================================================
class HybridNavigator:
    """
    Hibrit navigasyon sınıfı.
    Engel kaçış + Hedef takip + Waypoint navigasyonunu birleştirir.
    """
    
    def __init__(self):
        """HybridNavigator başlatıcı."""
        self.current_mode = FlightMode.SEARCH
        self.previous_mode = FlightMode.SEARCH
        self.mode_change_time = time.time()
        
        # Mod geçiş sayaçları
        self.mode_durations = {mode: 0.0 for mode in FlightMode}
        
        print("✅ HybridNavigator başlatıldı")
    
    def determine_flight_mode(
        self,
        obstacle_data: Dict,
        tracking_data: Dict,
        waypoint_data: Dict,
        telemetry: Dict
    ) -> FlightMode:
        """
        Mevcut duruma göre uçuş modunu belirler.
        
        Öncelik Sırası:
        1. EMERGENCY: Kritik engel (< 2m)
        2. TRACK: Hedef tespit edildi
        3. RETURN: Batarya düşük veya görev tamamlandı
        4. SEARCH: Normal waypoint takibi
        
        Args:
            obstacle_data: Engel kaçış verisi
            tracking_data: Hedef takip verisi
            waypoint_data: Waypoint navigasyon verisi
            telemetry: Telemetri verisi
        
        Returns:
            Belirlenen uçuş modu
        """
        # 1. ÖNCELİK: ACİL DURUM (Kritik engel)
        if obstacle_data.get('critical', False):
            return FlightMode.EMERGENCY
        
        # 2. ÖNCELİK: HEDEF TAKİP
        if tracking_data.get('tracking_active', False):
            # Hedef mesafesi kontrolü
            target_distance = tracking_data.get('target_distance', float('inf'))
            
            if target_distance <= MissionConfig.ATTACK_DISTANCE:
                return FlightMode.ATTACK
            else:
                return FlightMode.TRACK
        
        # 3. ÖNCELİK: DÖNÜŞ
        battery_remaining = telemetry.get('battery', {}).get('remaining', 100)
        mission_completed = waypoint_data.get('mission_completed', False)
        
        if battery_remaining < MissionConfig.RETURN_BATTERY_THRESHOLD or mission_completed:
            return FlightMode.RETURN
        
        # 4. ÖNCELİK: ARAMA (Normal waypoint takibi)
        return FlightMode.SEARCH
    
    def combine_navigation_vectors(
        self,
        obstacle_maneuver: Dict,
        tracking_command: Dict,
        waypoint_nav: Dict,
        current_mode: FlightMode
    ) -> Dict:
        """
        Farklı navigasyon kaynaklarından gelen vektörleri birleştirir.
        
        Args:
            obstacle_maneuver: Engel kaçış manevrası
            tracking_command: Hedef takip komutu
            waypoint_nav: Waypoint navigasyon komutu
            current_mode: Mevcut uçuş modu
        
        Returns:
            Birleştirilmiş navigasyon komutu:
            {
                'heading': float,      # Hedef yön (derece)
                'speed_factor': float, # Hız faktörü (0-1)
                'altitude_change': float, # İrtifa değişimi (metre)
                'priority_source': str # Hangi kaynak öncelikli
            }
        """
        # Mod bazlı ağırlıklar
        weights = self._get_mode_weights(current_mode)
        
        # Engel kaçış vektörü
        obstacle_heading = obstacle_maneuver.get('new_heading', 0.0)
        obstacle_weight = weights['obstacle']
        
        # Hedef takip vektörü
        tracking_yaw_rate = tracking_command.get('yaw_rate', 0.0)
        tracking_weight = weights['tracking']
        
        # Waypoint vektörü
        waypoint_bearing = waypoint_nav.get('target_bearing', 0.0)
        waypoint_weight = weights['waypoint']
        
        # Ağırlıklı ortalama ile birleştir
        if current_mode == FlightMode.EMERGENCY:
            # Acil durumda sadece engel kaçış
            final_heading = obstacle_heading
            speed_factor = obstacle_maneuver.get('speed_factor', 0.5)
            priority_source = 'obstacle_avoidance'
        
        elif current_mode in [FlightMode.TRACK, FlightMode.ATTACK]:
            # Hedef takip modunda: Hedef + Engel kaçış
            # Yaw rate'i heading'e dönüştür (basitleştirilmiş)
            current_heading = obstacle_maneuver.get('current_heading', 0.0)
            tracking_heading_delta = np.degrees(tracking_yaw_rate) * 5  # Yaklaşık dönüşüm
            tracking_heading = (current_heading + tracking_heading_delta) % 360
            
            # Engel varsa engel kaçışı öncelikli
            if obstacle_maneuver.get('action') != 'proceed':
                final_heading = (obstacle_heading * 0.7 + tracking_heading * 0.3) % 360
                priority_source = 'obstacle_avoidance + tracking'
            else:
                final_heading = tracking_heading
                priority_source = 'tracking'
            
            speed_factor = 0.7 if current_mode == FlightMode.TRACK else 0.5
        
        elif current_mode == FlightMode.RETURN:
            # Dönüş modunda: Waypoint + Engel kaçış
            if obstacle_maneuver.get('action') != 'proceed':
                final_heading = (obstacle_heading * 0.6 + waypoint_bearing * 0.4) % 360
                priority_source = 'obstacle_avoidance + waypoint'
            else:
                final_heading = waypoint_bearing
                priority_source = 'waypoint'
            
            speed_factor = 0.8
        
        else:  # SEARCH
            # Arama modunda: Waypoint + Engel kaçış
            if obstacle_maneuver.get('action') != 'proceed':
                final_heading = (obstacle_heading * 0.6 + waypoint_bearing * 0.4) % 360
                priority_source = 'obstacle_avoidance + waypoint'
            else:
                final_heading = waypoint_bearing
                priority_source = 'waypoint'
            
            speed_factor = 0.6
        
        # İrtifa değişimi
        altitude_change = waypoint_nav.get('altitude_error', 0.0)
        
        # Engel varsa irtifa değişimini sınırla
        if obstacle_maneuver.get('action') != 'proceed':
            altitude_change = np.clip(altitude_change, -2.0, 2.0)
        
        return {
            'heading': final_heading,
            'speed_factor': speed_factor,
            'altitude_change': altitude_change,
            'priority_source': priority_source
        }
    
    def _get_mode_weights(self, mode: FlightMode) -> Dict[str, float]:
        """
        Mod bazlı ağırlıkları döndürür.
        
        Args:
            mode: Uçuş modu
        
        Returns:
            Ağırlık dictionary'si
        """
        weights = {
            FlightMode.EMERGENCY: {
                'obstacle': 1.0,
                'tracking': 0.0,
                'waypoint': 0.0
            },
            FlightMode.TRACK: {
                'obstacle': 0.4,
                'tracking': 0.6,
                'waypoint': 0.0
            },
            FlightMode.ATTACK: {
                'obstacle': 0.3,
                'tracking': 0.7,
                'waypoint': 0.0
            },
            FlightMode.RETURN: {
                'obstacle': 0.4,
                'tracking': 0.0,
                'waypoint': 0.6
            },
            FlightMode.SEARCH: {
                'obstacle': 0.3,
                'tracking': 0.0,
                'waypoint': 0.7
            }
        }
        
        return weights.get(mode, {'obstacle': 0.33, 'tracking': 0.33, 'waypoint': 0.34})
    
    def update_mode(self, new_mode: FlightMode):
        """
        Uçuş modunu günceller.
        
        Args:
            new_mode: Yeni uçuş modu
        """
        if new_mode != self.current_mode:
            # Mod değişimi
            self.previous_mode = self.current_mode
            self.current_mode = new_mode
            self.mode_change_time = time.time()
            
            print(f"🔄 Mod Değişimi: {self.previous_mode.value} → {self.current_mode.value}")
    
    def get_mode_icon(self, mode: FlightMode) -> str:
        """
        Mod için emoji ikonu döndürür.
        
        Args:
            mode: Uçuş modu
        
        Returns:
            Emoji ikonu
        """
        icons = {
            FlightMode.SEARCH: "🔍",
            FlightMode.TRACK: "🎯",
            FlightMode.ATTACK: "⚔️",
            FlightMode.RETURN: "🏠",
            FlightMode.EMERGENCY: "🚨"
        }
        
        return icons.get(mode, "❓")
    
    def get_navigation_status(self, mode: FlightMode, nav_data: Dict) -> str:
        """
        Navigasyon durumunu açıklayan metin döndürür.
        
        Args:
            mode: Mevcut uçuş modu
            nav_data: Navigasyon verisi
        
        Returns:
            Durum metni
        """
        icon = self.get_mode_icon(mode)
        
        if mode == FlightMode.EMERGENCY:
            closest_distance = nav_data.get('closest_obstacle', {}).get('distance', 0.0)
            return f"{icon} ACİL KAÇIŞ - Engel: {closest_distance:.1f}m"
        
        elif mode == FlightMode.TRACK:
            target_distance = nav_data.get('target_distance', 0.0)
            return f"{icon} HEDEF TAKİP - Mesafe: {target_distance:.1f}m"
        
        elif mode == FlightMode.ATTACK:
            target_distance = nav_data.get('target_distance', 0.0)
            return f"{icon} SALDIRI MODU - Mesafe: {target_distance:.1f}m"
        
        elif mode == FlightMode.RETURN:
            wp_distance = nav_data.get('distance_to_wp', 0.0)
            return f"{icon} DÖNÜŞ - Üsse: {wp_distance:.1f}m"
        
        else:  # SEARCH
            wp_index = nav_data.get('current_wp_index', 0)
            wp_total = nav_data.get('total_waypoints', 0)
            wp_distance = nav_data.get('distance_to_wp', 0.0)
            return f"{icon} ARAMA - WP{wp_index+1}/{wp_total} ({wp_distance:.1f}m)"


# ============================================================================
# TEST FONKSİYONU
# ============================================================================
def test_hybrid_navigator():
    """Hybrid navigator modülünü test eder."""
    print("=" * 60)
    print("HİBRİT NAVİGATOR MODÜLÜ TEST")
    print("=" * 60)
    
    # HybridNavigator oluştur
    navigator = HybridNavigator()
    
    # Test senaryoları
    print("\n📋 Test Senaryoları:\n")
    
    # Senaryo 1: Normal arama modu
    print("1️⃣  Senaryo: Normal arama modu")
    obstacle_data = {'action': 'proceed', 'critical': False}
    tracking_data = {'tracking_active': False}
    waypoint_data = {'active': True, 'target_bearing': 45.0, 'distance_to_wp': 100.0}
    telemetry = {'battery': {'remaining': 80}}
    
    mode = navigator.determine_flight_mode(obstacle_data, tracking_data, waypoint_data, telemetry)
    navigator.update_mode(mode)
    print(f"   Mod: {mode.value}")
    print(f"   Durum: {navigator.get_navigation_status(mode, waypoint_data)}\n")
    
    # Senaryo 2: Hedef tespit edildi
    print("2️⃣  Senaryo: Hedef tespit edildi")
    tracking_data = {'tracking_active': True, 'target_distance': 50.0}
    
    mode = navigator.determine_flight_mode(obstacle_data, tracking_data, waypoint_data, telemetry)
    navigator.update_mode(mode)
    print(f"   Mod: {mode.value}")
    print(f"   Durum: {navigator.get_navigation_status(mode, {'target_distance': 50.0})}\n")
    
    # Senaryo 3: Kritik engel
    print("3️⃣  Senaryo: Kritik engel tespit edildi")
    obstacle_data = {'action': 'emergency', 'critical': True, 'closest_obstacle': {'distance': 1.5}}
    
    mode = navigator.determine_flight_mode(obstacle_data, tracking_data, waypoint_data, telemetry)
    navigator.update_mode(mode)
    print(f"   Mod: {mode.value}")
    print(f"   Durum: {navigator.get_navigation_status(mode, obstacle_data)}\n")
    
    # Senaryo 4: Batarya düşük - dönüş
    print("4️⃣  Senaryo: Batarya düşük - dönüş modu")
    obstacle_data = {'action': 'proceed', 'critical': False}
    tracking_data = {'tracking_active': False}
    telemetry = {'battery': {'remaining': 15}}
    
    mode = navigator.determine_flight_mode(obstacle_data, tracking_data, waypoint_data, telemetry)
    navigator.update_mode(mode)
    print(f"   Mod: {mode.value}")
    print(f"   Durum: {navigator.get_navigation_status(mode, waypoint_data)}\n")
    
    print("✅ Test tamamlandı")


if __name__ == "__main__":
    test_hybrid_navigator()
