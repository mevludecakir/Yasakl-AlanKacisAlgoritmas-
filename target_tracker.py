"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
Hedef Takip Modülü (Target Tracker Module)

TEKNOFEST Savaşan İHA Yarışması için geliştirilmiştir.

Bu modül, tespit edilen hedef İHA'yı takip eder ve kamera frame'i içinde tutar.

Özellikler:
- Hedef İHA tespiti ve filtreleme
- PID kontrolü ile frame merkezleme
- Kalman filtresi ile pozisyon tahmini
- Hedef hız ve yön tahmini
- Hedef kaybolma durumu yönetimi

Author: Computer Engineering
Platform: NVIDIA Jetson Nano + Pixhawk
Competition: TEKNOFEST Savaşan İHA
"""

import numpy as np
from typing import Optional, Dict, Tuple
from collections import deque
import time

from config import TargetTrackingConfig, CameraConfig


# ============================================================================
# PID CONTROLLER CLASS
# ============================================================================
class PIDController:
    """
    PID kontrolcü sınıfı.
    Hedefi frame merkezinde tutmak için kullanılır.
    """
    
    def __init__(self, kp: float, ki: float, kd: float, output_limits: Tuple[float, float] = (-1.0, 1.0)):
        """
        PID Controller başlatıcı.
        
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            output_limits: Çıkış limitleri (min, max)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
    
    def compute(self, error: float) -> float:
        """
        PID çıkışını hesaplar.
        
        Args:
            error: Hata değeri (setpoint - measurement)
        
        Returns:
            Kontrol çıkışı
        """
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0.0:
            dt = 0.01  # Minimum zaman adımı
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        # Derivative term
        derivative = (error - self.last_error) / dt
        d_term = self.kd * derivative
        
        # Toplam çıkış
        output = p_term + i_term + d_term
        
        # Limitleri uygula
        output = np.clip(output, self.output_limits[0], self.output_limits[1])
        
        # Güncelle
        self.last_error = error
        self.last_time = current_time
        
        return output
    
    def reset(self):
        """PID durumunu sıfırla."""
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()


# ============================================================================
# KALMAN FILTER CLASS
# ============================================================================
class KalmanFilter:
    """
    Kalman filtresi - Hedef pozisyon tahmini için.
    """
    
    def __init__(self, process_variance: float = 1e-5, measurement_variance: float = 1e-2):
        """
        Kalman Filter başlatıcı.
        
        Args:
            process_variance: Süreç gürültüsü varyansı
            measurement_variance: Ölçüm gürültüsü varyansı
        """
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        
        # Durum: [x, vx, y, vy]
        self.state = np.zeros(4)
        
        # Kovaryans matrisi
        self.covariance = np.eye(4) * 1000
        
        # Süreç modeli (constant velocity)
        self.dt = 0.05  # 20 Hz
        self.F = np.array([
            [1, self.dt, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, self.dt],
            [0, 0, 0, 1]
        ])
        
        # Ölçüm modeli
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0]
        ])
        
        # Süreç gürültüsü
        self.Q = np.eye(4) * self.process_variance
        
        # Ölçüm gürültüsü
        self.R = np.eye(2) * self.measurement_variance
    
    def predict(self):
        """Bir sonraki durumu tahmin et."""
        # State prediction
        self.state = self.F @ self.state
        
        # Covariance prediction
        self.covariance = self.F @ self.covariance @ self.F.T + self.Q
    
    def update(self, measurement: np.ndarray):
        """
        Ölçüm ile güncelle.
        
        Args:
            measurement: [x, y] ölçümü
        """
        # Innovation
        y = measurement - (self.H @ self.state)
        
        # Innovation covariance
        S = self.H @ self.covariance @ self.H.T + self.R
        
        # Kalman gain
        K = self.covariance @ self.H.T @ np.linalg.inv(S)
        
        # State update
        self.state = self.state + K @ y
        
        # Covariance update
        self.covariance = (np.eye(4) - K @ self.H) @ self.covariance
    
    def get_position(self) -> Tuple[float, float]:
        """Tahmini pozisyonu döndür."""
        return self.state[0], self.state[2]
    
    def get_velocity(self) -> Tuple[float, float]:
        """Tahmini hızı döndür."""
        return self.state[1], self.state[3]


# ============================================================================
# TARGET TRACKER CLASS
# ============================================================================
class TargetTracker:
    """
    Hedef İHA takip sınıfı.
    """
    
    def __init__(self):
        """TargetTracker başlatıcı."""
        # PID kontrolcüler (X ve Y ekseni için)
        self.pid_x = PIDController(
            kp=TargetTrackingConfig.PID_KP,
            ki=TargetTrackingConfig.PID_KI,
            kd=TargetTrackingConfig.PID_KD,
            output_limits=(-TargetTrackingConfig.MAX_YAW_RATE, TargetTrackingConfig.MAX_YAW_RATE)
        )
        
        self.pid_y = PIDController(
            kp=TargetTrackingConfig.PID_KP_PITCH,
            ki=TargetTrackingConfig.PID_KI_PITCH,
            kd=TargetTrackingConfig.PID_KD_PITCH,
            output_limits=(-TargetTrackingConfig.MAX_PITCH_RATE, TargetTrackingConfig.MAX_PITCH_RATE)
        )
        
        # Kalman filtresi
        self.kalman = KalmanFilter()
        
        # Frame merkezi
        self.frame_center_x = CameraConfig.FRAME_WIDTH / 2
        self.frame_center_y = CameraConfig.FRAME_HEIGHT / 2
        
        # Hedef durumu
        self.target_detected = False
        self.target_lost_time = None
        self.last_target_position = None
        
        # Hedef geçmişi (hız tahmini için)
        self.target_history = deque(maxlen=TargetTrackingConfig.HISTORY_LENGTH)
        
        print("✅ TargetTracker başlatıldı")
    
    def detect_target_uav(self, detections: list) -> Optional[Dict]:
        """
        Tespit edilen nesneler arasından hedef İHA'yı bulur.
        
        Args:
            detections: Vision modülünden gelen tespit listesi
        
        Returns:
            Hedef İHA bilgisi veya None
        """
        # İHA sınıfı tespitlerini filtrele
        uav_detections = [
            det for det in detections
            if det['class_id'] == TargetTrackingConfig.TARGET_CLASS_ID and
               det['confidence'] >= TargetTrackingConfig.MIN_CONFIDENCE
        ]
        
        if not uav_detections:
            return None
        
        # En yakın İHA'yı seç (en büyük bounding box = en yakın)
        target = max(uav_detections, key=lambda d: (d['bbox'][2] - d['bbox'][0]) * (d['bbox'][3] - d['bbox'][1]))
        
        return target
    
    def update_target_state(self, target: Optional[Dict]):
        """
        Hedef durumunu günceller.
        
        Args:
            target: Hedef İHA bilgisi
        """
        if target is not None:
            # Hedef tespit edildi
            self.target_detected = True
            self.target_lost_time = None
            
            # Hedef merkez koordinatları
            cx, cy = target['center']
            
            # Kalman filtresi güncelle
            measurement = np.array([cx, cy])
            self.kalman.predict()
            self.kalman.update(measurement)
            
            # Geçmişe ekle
            self.target_history.append({
                'position': (cx, cy),
                'distance': target['distance'],
                'timestamp': time.time()
            })
            
            self.last_target_position = (cx, cy)
        
        else:
            # Hedef kaybedildi
            if self.target_detected:
                if self.target_lost_time is None:
                    self.target_lost_time = time.time()
                
                # Kayıp süresi kontrolü
                lost_duration = time.time() - self.target_lost_time
                
                if lost_duration > TargetTrackingConfig.TARGET_LOST_TIMEOUT:
                    # Hedef tamamen kaybedildi
                    self.target_detected = False
                    self.pid_x.reset()
                    self.pid_y.reset()
                    self.target_history.clear()
                    print("⚠️  Hedef kaybedildi")
                else:
                    # Kalman filtresi ile tahmin et
                    self.kalman.predict()
    
    def calculate_tracking_command(self, target: Optional[Dict]) -> Dict:
        """
        Hedef takip komutu hesaplar.
        
        Args:
            target: Hedef İHA bilgisi
        
        Returns:
            Takip komutu:
            {
                'tracking_active': bool,
                'yaw_rate': float,      # Yaw açısal hızı (rad/s)
                'pitch_rate': float,    # Pitch açısal hızı (rad/s)
                'target_bearing': float, # Hedef yönü (derece)
                'target_distance': float, # Hedef mesafe (metre)
                'target_velocity': tuple, # Hedef hız (vx, vy)
                'predicted_position': tuple # Tahmini pozisyon
            }
        """
        # Hedef durumunu güncelle
        self.update_target_state(target)
        
        if not self.target_detected:
            return {
                'tracking_active': False,
                'yaw_rate': 0.0,
                'pitch_rate': 0.0,
                'target_bearing': 0.0,
                'target_distance': 0.0,
                'target_velocity': (0.0, 0.0),
                'predicted_position': (0.0, 0.0)
            }
        
        # Tahmini pozisyon (Kalman)
        pred_x, pred_y = self.kalman.get_position()
        
        # Hata hesapla (frame merkezi - hedef pozisyonu)
        error_x = self.frame_center_x - pred_x
        error_y = self.frame_center_y - pred_y
        
        # PID kontrolü
        yaw_rate = self.pid_x.compute(error_x)
        pitch_rate = self.pid_y.compute(error_y)
        
        # Hedef yönü (frame merkezine göre)
        target_bearing = np.degrees(np.arctan2(pred_x - self.frame_center_x, self.frame_center_y - pred_y))
        
        # Hedef mesafe
        target_distance = target['distance'] if target else 0.0
        
        # Hedef hızı
        target_velocity = self.kalman.get_velocity()
        
        return {
            'tracking_active': True,
            'yaw_rate': yaw_rate,
            'pitch_rate': pitch_rate,
            'target_bearing': target_bearing,
            'target_distance': target_distance,
            'target_velocity': target_velocity,
            'predicted_position': (pred_x, pred_y)
        }
    
    def estimate_intercept_point(self, current_position: Dict, current_velocity: float) -> Optional[Tuple[float, float]]:
        """
        Hedefi kesmek için optimal nokta tahmini.
        
        Args:
            current_position: Mevcut GPS konumu {'lat', 'lon', 'alt'}
            current_velocity: Mevcut hız (m/s)
        
        Returns:
            Kesişme noktası (lat, lon) veya None
        """
        if not self.target_detected or len(self.target_history) < 2:
            return None
        
        # Hedef hız vektörü
        vx, vy = self.kalman.get_velocity()
        target_speed = np.sqrt(vx**2 + vy**2)
        
        if target_speed < 0.1:  # Hedef duruyorsa
            return None
        
        # Basit kesişme noktası tahmini
        # (Gerçek uygulamada daha karmaşık hesaplamalar gerekir)
        
        return None  # Şimdilik None döndür
    
    def get_tracking_status(self) -> str:
        """
        Takip durumunu açıklayan metin döndürür.
        
        Returns:
            Durum metni
        """
        if not self.target_detected:
            return "❌ Hedef Tespit Edilmedi"
        
        if self.target_lost_time is not None:
            lost_duration = time.time() - self.target_lost_time
            return f"⚠️  Hedef Kaybedildi ({lost_duration:.1f}s)"
        
        return "🎯 Hedef Kilitli"


# ============================================================================
# TEST FONKSİYONU
# ============================================================================
def test_target_tracker():
    """Target tracker modülünü test eder."""
    print("=" * 60)
    print("HEDEF TAKİP MODÜLÜ TEST")
    print("=" * 60)
    
    # TargetTracker oluştur
    tracker = TargetTracker()
    
    # Test senaryoları
    print("\n📋 Test Senaryoları:\n")
    
    # Senaryo 1: Hedef yok
    print("1️⃣  Senaryo: Hedef tespit edilmedi")
    detections = []
    command = tracker.calculate_tracking_command(None)
    print(f"   Tracking Active: {command['tracking_active']}")
    print(f"   Durum: {tracker.get_tracking_status()}\n")
    
    # Senaryo 2: Hedef frame merkezinde
    print("2️⃣  Senaryo: Hedef frame merkezinde")
    detections = [{
        'bbox': [310, 230, 330, 250],
        'confidence': 0.95,
        'class_id': TargetTrackingConfig.TARGET_CLASS_ID,
        'class_name': 'uav',
        'center': (320, 240),
        'distance': 25.0
    }]
    target = tracker.detect_target_uav(detections)
    command = tracker.calculate_tracking_command(target)
    print(f"   Tracking Active: {command['tracking_active']}")
    print(f"   Yaw Rate: {command['yaw_rate']:.4f} rad/s")
    print(f"   Target Distance: {command['target_distance']:.1f}m")
    print(f"   Durum: {tracker.get_tracking_status()}\n")
    
    # Senaryo 3: Hedef sağda
    print("3️⃣  Senaryo: Hedef frame sağında")
    detections = [{
        'bbox': [500, 230, 550, 280],
        'confidence': 0.92,
        'class_id': TargetTrackingConfig.TARGET_CLASS_ID,
        'class_name': 'uav',
        'center': (525, 255),
        'distance': 30.0
    }]
    target = tracker.detect_target_uav(detections)
    command = tracker.calculate_tracking_command(target)
    print(f"   Tracking Active: {command['tracking_active']}")
    print(f"   Yaw Rate: {command['yaw_rate']:.4f} rad/s (Sağa dön)")
    print(f"   Target Bearing: {command['target_bearing']:.1f}°")
    print(f"   Durum: {tracker.get_tracking_status()}\n")
    
    # Senaryo 4: Hedef kaybedildi
    print("4️⃣  Senaryo: Hedef kaybedildi")
    for i in range(3):
        command = tracker.calculate_tracking_command(None)
        print(f"   t={i}s: {tracker.get_tracking_status()}")
        time.sleep(1)
    
    print("\n✅ Test tamamlandı")


if __name__ == "__main__":
    test_target_tracker()
