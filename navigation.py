"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
Navigasyon Modülü (Navigation Module)

Bu modül, Artificial Potential Fields (Yapay Potansiyel Alanlar) algoritmasını
kullanarak tespit edilen engellerden kaçış manevrası üretir.

Algoritma Prensibi:
- Hedef nokta çekici kuvvet (attractive force) oluşturur
- Engeller itici kuvvet (repulsive force) oluşturur
- Sonuç vektör, İHA'nın yeni yönünü belirler

Özellikler:
- APF algoritması implementasyonu
- Dinamik engel kaçış hesaplaması
- Güvenli mesafe yönetimi
- Heading (yön) ayarlama komutları

Author: Computer Engineering
Platform: NVIDIA Jetson Nano
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import math

from config import NavigationConfig, CameraConfig


# ============================================================================
# OBSTACLE AVOIDANCE CLASS
# ============================================================================
class ObstacleAvoidance:
    """
    Artificial Potential Fields algoritması ile engel kaçış sınıfı.
    """
    
    def __init__(self):
        """ObstacleAvoidance başlatıcı."""
        # APF parametreleri
        self.k_attractive = NavigationConfig.K_ATTRACTIVE
        self.k_repulsive = NavigationConfig.K_REPULSIVE
        self.safe_distance = NavigationConfig.SAFE_DISTANCE
        self.critical_distance = NavigationConfig.CRITICAL_DISTANCE
        
        # Sapma limitleri
        self.max_deviation = NavigationConfig.MAX_DEVIATION_ANGLE
        self.min_deviation = NavigationConfig.MIN_DEVIATION_ANGLE
        
        # Hedef konum (GPS koordinatları)
        self.goal_position = {
            'lat': NavigationConfig.DEFAULT_GOAL_LAT,
            'lon': NavigationConfig.DEFAULT_GOAL_LON,
            'alt': NavigationConfig.DEFAULT_GOAL_ALT
        }
        
        # Kamera parametreleri
        self.frame_width = CameraConfig.FRAME_WIDTH
        self.frame_height = CameraConfig.FRAME_HEIGHT
        self.frame_center_x = self.frame_width / 2
        self.frame_center_y = self.frame_height / 2
        
        print("✅ ObstacleAvoidance başlatıldı")
    
    def set_goal(self, lat: float, lon: float, alt: float):
        """
        Hedef konumu ayarlar.
        
        Args:
            lat: Hedef enlem (latitude)
            lon: Hedef boylam (longitude)
            alt: Hedef irtifa (altitude, metre)
        """
        self.goal_position = {'lat': lat, 'lon': lon, 'alt': alt}
        print(f"🎯 Hedef konum güncellendi: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
    
    def calculate_avoidance_maneuver(
        self,
        detections: List[Dict],
        current_heading: float = 0.0,
        current_position: Optional[Dict] = None
    ) -> Dict:
        """
        Tespit edilen engellere göre kaçış manevrası hesaplar.
        
        Args:
            detections: Vision modülünden gelen tespit listesi
            current_heading: Mevcut yön açısı (derece, 0=Kuzey, saat yönünde)
            current_position: Mevcut GPS konumu {'lat', 'lon', 'alt'}
        
        Returns:
            Kaçış manevrası bilgileri:
            {
                'action': str,              # 'avoid', 'proceed', 'emergency_stop'
                'heading_adjustment': float, # Yön değişikliği (derece, ±)
                'new_heading': float,       # Yeni hedef yön (derece)
                'speed_factor': float,      # Hız çarpanı (0.0-1.0)
                'closest_obstacle': Dict,   # En yakın engel bilgisi
                'force_vector': tuple,      # Sonuç kuvvet vektörü (fx, fy)
                'critical': bool            # Kritik durum bayrağı
            }
        """
        # Engel yoksa normal ilerleme
        if not detections:
            return {
                'action': 'proceed',
                'heading_adjustment': 0.0,
                'new_heading': current_heading,
                'speed_factor': 1.0,
                'closest_obstacle': None,
                'force_vector': (0.0, 0.0),
                'critical': False
            }
        
        # En yakın engeli bul
        closest_obstacle = min(detections, key=lambda d: d['distance'])
        min_distance = closest_obstacle['distance']
        
        # Kritik mesafe kontrolü
        if min_distance < self.critical_distance:
            # ACİL DURUM: Çok yakın engel
            return self._emergency_avoidance(closest_obstacle, current_heading)
        
        # APF kuvvetlerini hesapla
        repulsive_force = self._calculate_repulsive_forces(detections)
        attractive_force = self._calculate_attractive_force(current_position)
        
        # Toplam kuvvet vektörü
        total_force_x = repulsive_force[0] + attractive_force[0]
        total_force_y = repulsive_force[1] + attractive_force[1]
        
        # Kuvvet vektöründen yön açısı hesapla
        force_angle = math.degrees(math.atan2(total_force_x, total_force_y))
        
        # Heading ayarlaması hesapla
        heading_adjustment = self._normalize_angle(force_angle)
        
        # Limitleri uygula
        heading_adjustment = np.clip(
            heading_adjustment,
            -self.max_deviation,
            self.max_deviation
        )
        
        # Yeni heading
        new_heading = self._normalize_angle(current_heading + heading_adjustment)
        
        # Hız faktörü (engele yaklaştıkça yavaşla)
        speed_factor = self._calculate_speed_factor(min_distance)
        
        # Aksiyon belirle
        action = 'avoid' if abs(heading_adjustment) > self.min_deviation else 'proceed'
        
        return {
            'action': action,
            'heading_adjustment': heading_adjustment,
            'new_heading': new_heading,
            'speed_factor': speed_factor,
            'closest_obstacle': closest_obstacle,
            'force_vector': (total_force_x, total_force_y),
            'critical': False
        }
    
    def _calculate_repulsive_forces(self, detections: List[Dict]) -> Tuple[float, float]:
        """
        Tüm engellerden gelen itici kuvvetleri hesaplar.
        
        APF Formülü:
        F_rep = K_rep * (1/d - 1/d_safe)² * (1/d²) * direction_vector
        
        Args:
            detections: Tespit edilen engeller
        
        Returns:
            (force_x, force_y) tuple
        """
        total_fx = 0.0
        total_fy = 0.0
        
        for obstacle in detections:
            distance = obstacle['distance']
            
            # Sadece güvenli mesafe içindeki engeller etki eder
            if distance > self.safe_distance:
                continue
            
            # Engelin ekrandaki konumu
            cx, cy = obstacle['center']
            
            # Ekran merkezinden engele doğru vektör
            dx = cx - self.frame_center_x
            dy = cy - self.frame_center_y
            
            # Normalize et
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                dx /= magnitude
                dy /= magnitude
            
            # İtici kuvvet büyüklüğü
            # F_rep = K_rep * (1/d - 1/d_safe)² * (1/d²)
            if distance > 0:
                force_magnitude = self.k_repulsive * \
                                ((1.0 / distance) - (1.0 / self.safe_distance))**2 * \
                                (1.0 / distance**2)
            else:
                force_magnitude = self.k_repulsive * 1000  # Çok büyük kuvvet
            
            # Kuvvet vektörü (engelden uzaklaşma yönünde)
            # Ekranda sağda ise sağa, solda ise sola kaç
            total_fx -= dx * force_magnitude  # Ters yön (kaçış)
            total_fy -= dy * force_magnitude
        
        return (total_fx, total_fy)
    
    def _calculate_attractive_force(self, current_position: Optional[Dict]) -> Tuple[float, float]:
        """
        Hedef noktadan gelen çekici kuvveti hesaplar.
        
        APF Formülü:
        F_att = K_att * distance_to_goal * direction_to_goal
        
        Args:
            current_position: Mevcut GPS konumu (None ise çekici kuvvet yok)
        
        Returns:
            (force_x, force_y) tuple
        """
        # GPS konumu yoksa çekici kuvvet yok (sadece kaçış modu)
        if current_position is None:
            return (0.0, 0.0)
        
        # Hedef ile mevcut konum arasındaki fark
        dlat = self.goal_position['lat'] - current_position['lat']
        dlon = self.goal_position['lon'] - current_position['lon']
        
        # Mesafe hesapla (basitleştirilmiş, gerçekte haversine kullanılmalı)
        distance = math.sqrt(dlat**2 + dlon**2)
        
        if distance > 0:
            # Normalize edilmiş yön vektörü
            dir_x = dlon / distance
            dir_y = dlat / distance
            
            # Çekici kuvvet
            force_magnitude = self.k_attractive * distance
            
            return (dir_x * force_magnitude, dir_y * force_magnitude)
        else:
            return (0.0, 0.0)
    
    def _emergency_avoidance(self, obstacle: Dict, current_heading: float) -> Dict:
        """
        Kritik mesafedeki engel için acil kaçış manevrası.
        
        Args:
            obstacle: En yakın engel
            current_heading: Mevcut yön
        
        Returns:
            Acil kaçış komutu
        """
        # Engelin ekrandaki konumuna göre kaçış yönü belirle
        cx, cy = obstacle['center']
        
        # Ekran merkezine göre konum
        if cx < self.frame_center_x:
            # Engel solda -> Sağa kaç
            heading_adjustment = self.max_deviation
        else:
            # Engel sağda -> Sola kaç
            heading_adjustment = -self.max_deviation
        
        new_heading = self._normalize_angle(current_heading + heading_adjustment)
        
        print(f"🚨 ACİL KAÇIŞ! Engel mesafesi: {obstacle['distance']:.2f}m")
        
        return {
            'action': 'emergency_stop',
            'heading_adjustment': heading_adjustment,
            'new_heading': new_heading,
            'speed_factor': NavigationConfig.SPEED_REDUCTION_FACTOR,
            'closest_obstacle': obstacle,
            'force_vector': (0.0, 0.0),
            'critical': True
        }
    
    def _calculate_speed_factor(self, distance: float) -> float:
        """
        Engele olan mesafeye göre hız faktörü hesaplar.
        
        Args:
            distance: Engele mesafe (metre)
        
        Returns:
            Hız faktörü (0.0-1.0)
        """
        if distance < self.critical_distance:
            return NavigationConfig.SPEED_REDUCTION_FACTOR
        elif distance < self.safe_distance:
            # Lineer interpolasyon
            factor = (distance - self.critical_distance) / \
                    (self.safe_distance - self.critical_distance)
            return NavigationConfig.SPEED_REDUCTION_FACTOR + \
                   (1.0 - NavigationConfig.SPEED_REDUCTION_FACTOR) * factor
        else:
            return 1.0
    
    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """
        Açıyı -180 ile +180 derece arasına normalize eder.
        
        Args:
            angle: Açı (derece)
        
        Returns:
            Normalize edilmiş açı
        """
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle
    
    def get_navigation_status(self, maneuver: Dict) -> str:
        """
        Navigasyon durumunu açıklayan metin döndürür.
        
        Args:
            maneuver: calculate_avoidance_maneuver() çıktısı
        
        Returns:
            Durum metni
        """
        action = maneuver['action']
        
        if action == 'emergency_stop':
            return "🚨 ACİL KAÇIŞ MODU"
        elif action == 'avoid':
            direction = "SAĞ" if maneuver['heading_adjustment'] > 0 else "SOL"
            return f"⚠️  KAÇIŞ: {direction} {abs(maneuver['heading_adjustment']):.1f}°"
        else:
            return "✅ NORMAL İLERLEME"


# ============================================================================
# TEST FONKSİYONU
# ============================================================================
def test_navigation_module():
    """Navigation modülünü test eder."""
    print("=" * 60)
    print("NAVİGASYON MODÜLÜ TEST")
    print("=" * 60)
    
    # ObstacleAvoidance oluştur
    nav = ObstacleAvoidance()
    
    # Test senaryoları
    print("\n📋 Test Senaryoları:\n")
    
    # Senaryo 1: Engel yok
    print("1️⃣  Senaryo: Engel yok")
    maneuver = nav.calculate_avoidance_maneuver([], current_heading=0.0)
    print(f"   Aksiyon: {maneuver['action']}")
    print(f"   Durum: {nav.get_navigation_status(maneuver)}\n")
    
    # Senaryo 2: Solda uzak engel
    print("2️⃣  Senaryo: Solda uzak engel (4m)")
    detections = [{
        'bbox': [100, 200, 200, 400],
        'confidence': 0.95,
        'class_id': 0,
        'class_name': 'obstacle',
        'center': (150, 300),
        'distance': 4.0
    }]
    maneuver = nav.calculate_avoidance_maneuver(detections, current_heading=0.0)
    print(f"   Aksiyon: {maneuver['action']}")
    print(f"   Heading ayarı: {maneuver['heading_adjustment']:.2f}°")
    print(f"   Hız faktörü: {maneuver['speed_factor']:.2f}")
    print(f"   Durum: {nav.get_navigation_status(maneuver)}\n")
    
    # Senaryo 3: Sağda yakın engel
    print("3️⃣  Senaryo: Sağda yakın engel (3m)")
    detections = [{
        'bbox': [400, 200, 500, 400],
        'confidence': 0.90,
        'class_id': 0,
        'class_name': 'obstacle',
        'center': (450, 300),
        'distance': 3.0
    }]
    maneuver = nav.calculate_avoidance_maneuver(detections, current_heading=0.0)
    print(f"   Aksiyon: {maneuver['action']}")
    print(f"   Heading ayarı: {maneuver['heading_adjustment']:.2f}°")
    print(f"   Hız faktörü: {maneuver['speed_factor']:.2f}")
    print(f"   Durum: {nav.get_navigation_status(maneuver)}\n")
    
    # Senaryo 4: Kritik mesafede engel
    print("4️⃣  Senaryo: Kritik mesafede engel (1.5m)")
    detections = [{
        'bbox': [250, 200, 350, 400],
        'confidence': 0.98,
        'class_id': 0,
        'class_name': 'obstacle',
        'center': (300, 300),
        'distance': 1.5
    }]
    maneuver = nav.calculate_avoidance_maneuver(detections, current_heading=0.0)
    print(f"   Aksiyon: {maneuver['action']}")
    print(f"   Heading ayarı: {maneuver['heading_adjustment']:.2f}°")
    print(f"   Hız faktörü: {maneuver['speed_factor']:.2f}")
    print(f"   Kritik: {maneuver['critical']}")
    print(f"   Durum: {nav.get_navigation_status(maneuver)}\n")
    
    # Senaryo 5: Çoklu engel
    print("5️⃣  Senaryo: Çoklu engel")
    detections = [
        {'bbox': [100, 200, 200, 400], 'confidence': 0.95, 'class_id': 0,
         'class_name': 'obstacle', 'center': (150, 300), 'distance': 4.5},
        {'bbox': [400, 150, 500, 350], 'confidence': 0.90, 'class_id': 0,
         'class_name': 'obstacle', 'center': (450, 250), 'distance': 3.5}
    ]
    maneuver = nav.calculate_avoidance_maneuver(detections, current_heading=0.0)
    print(f"   Aksiyon: {maneuver['action']}")
    print(f"   Heading ayarı: {maneuver['heading_adjustment']:.2f}°")
    print(f"   En yakın engel: {maneuver['closest_obstacle']['distance']:.2f}m")
    print(f"   Durum: {nav.get_navigation_status(maneuver)}\n")
    
    print("✅ Test tamamlandı")


if __name__ == "__main__":
    test_navigation_module()
