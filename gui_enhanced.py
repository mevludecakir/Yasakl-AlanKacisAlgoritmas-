"""
TEKNOFEST Savaşan İHA - Gelişmiş Yer Kontrol İstasyonu
Enhanced Ground Control Station GUI Module

Bu modül, TEKNOFEST yarışması gereksinimlerine göre tasarlanmış
profesyonel bir yer kontrol istasyonu arayüzü sağlar.

Özellikler:
- Canlı kamera görüntüsü ile hedef İHA takibi
- MAVLink telemetri entegrasyonu (Mission Planner uyumlu)
- Waypoint haritası ve görev takibi
- Uçuş modu göstergeleri (SEARCH/TRACK/ATTACK/RETURN/EMERGENCY)
- Gerçek zamanlı sistem logları
- TEKNOFEST yarışması için tüm kritik veriler

Author: Computer Engineering
Platform: NVIDIA Jetson Nano + Pixhawk
Competition: TEKNOFEST Savaşan İHA
"""

import sys
import cv2
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QGroupBox, QGridLayout,
    QTextEdit, QProgressBar, QFrame, QSplitter, QFileDialog,
    QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor, QBrush
from typing import Optional, List, Dict
import json

from config import GUIConfig


# ============================================================================
# CONSTANTS
# ============================================================================
class Colors:
    """Renk sabitleri."""
    # Mod renkleri
    SEARCH = QColor(33, 150, 243)      # Mavi
    TRACK = QColor(76, 175, 80)        # Yeşil
    ATTACK = QColor(255, 152, 0)       # Turuncu
    RETURN = QColor(255, 193, 7)       # Sarı
    EMERGENCY = QColor(244, 67, 54)    # Kırmızı
    
    # Bounding box renkleri (BGR for OpenCV)
    BBOX_NORMAL = (0, 255, 0)          # Yeşil
    BBOX_TARGET = (0, 0, 255)          # Kırmızı
    BBOX_CRITICAL = (0, 165, 255)      # Turuncu
    
    # UI renkleri
    BG_DARK = QColor(30, 30, 30)
    PANEL_DARK = QColor(45, 45, 45)
    TEXT_WHITE = QColor(255, 255, 255)
    ACCENT = QColor(0, 120, 212)


class Icons:
    """Mod ikonları (emoji)."""
    SEARCH = "🔍"
    TRACK = "🎯"
    ATTACK = "⚔️"
    RETURN = "🏠"
    EMERGENCY = "🚨"


# ============================================================================
# VIDEO THREAD
# ============================================================================
class EnhancedVideoThread(QThread):
    """
    Gelişmiş video streaming thread'i.
    Hedef İHA tespiti ve vurgulama ile.
    """
    
    # Signals
    frame_ready = pyqtSignal(np.ndarray, list, dict)  # (frame, detections, target_info)
    fps_updated = pyqtSignal(float)
    
    def __init__(self, vision_processor, target_tracker=None):
        """
        EnhancedVideoThread başlatıcı.
        
        Args:
            vision_processor: VisionProcessor instance
            target_tracker: TargetTracker instance (opsiyonel)
        """
        super().__init__()
        self.vision_processor = vision_processor
        self.target_tracker = target_tracker
        self.is_running = False
    
    def run(self):
        """Thread ana döngüsü."""
        self.is_running = True
        
        while self.is_running:
            try:
                if not self.vision_processor:
                    self.msleep(100)
                    continue
                
                # Frame ve tespitleri al
                frame, detections = self.vision_processor.get_frame_and_detections()
                
                if frame is not None:
                    # Hedef İHA tespiti
                    target_info = {'detected': False}
                    if self.target_tracker and detections:
                        target = self.target_tracker.detect_target_uav(detections)
                        if target:
                            tracking_cmd = self.target_tracker.calculate_tracking_command(target)
                            target_info = {
                                'detected': True,
                                'bbox': target['bbox'],
                                'center': target['center'],
                                'distance': target['distance'],
                                'confidence': target['confidence'],
                                'tracking_active': tracking_cmd['tracking_active'],
                                'yaw_rate': tracking_cmd.get('yaw_rate', 0.0),
                                'pitch_rate': tracking_cmd.get('pitch_rate', 0.0)
                            }
                    
                    # Signal emit et
                    self.frame_ready.emit(frame, detections, target_info)
                    
                    # FPS güncelle
                    fps = self.vision_processor.get_fps()
                    self.fps_updated.emit(fps)
                
                # Frame rate kontrolü
                self.msleep(GUIConfig.VIDEO_UPDATE_INTERVAL)
                
            except Exception as e:
                print(f"⚠️  EnhancedVideoThread hatası: {e}")
                self.msleep(100)
    
    def stop(self):
        """Thread'i durdur."""
        self.is_running = False
        self.wait()


# ============================================================================
# TELEMETRY THREAD
# ============================================================================
class EnhancedTelemetryThread(QThread):
    """
    Gelişmiş telemetri thread'i.
    Hybrid navigator ve waypoint navigator verilerini de içerir.
    """
    
    # Signal
    telemetry_updated = pyqtSignal(dict)
    
    def __init__(self, mavlink_interface=None, hybrid_navigator=None, waypoint_navigator=None):
        """
        EnhancedTelemetryThread başlatıcı.
        
        Args:
            mavlink_interface: MAVLinkInterface instance
            hybrid_navigator: HybridNavigator instance
            waypoint_navigator: WaypointNavigator instance
        """
        super().__init__()
        self.mavlink_interface = mavlink_interface
        self.hybrid_navigator = hybrid_navigator
        self.waypoint_navigator = waypoint_navigator
        self.is_running = False
    
    def run(self):
        """Thread ana döngüsü."""
        self.is_running = True
        
        while self.is_running:
            try:
                # Telemetri verilerini topla
                data = {}
                
                # MAVLink telemetri
                if self.mavlink_interface:
                    data['mavlink'] = self.mavlink_interface.get_telemetry()
                else:
                    # Dummy data
                    data['mavlink'] = {
                        'connected': False,
                        'gps': {'lat': 0.0, 'lon': 0.0, 'alt': 0.0, 'fix': 0},
                        'attitude': {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0},
                        'heading': 0.0,
                        'groundspeed': 0.0,
                        'battery': {'voltage': 0.0, 'current': 0.0, 'remaining': 0},
                        'mode': 'UNKNOWN',
                        'armed': False
                    }
                
                # Hybrid navigator (flight mode)
                if self.hybrid_navigator:
                    data['flight_mode'] = self.hybrid_navigator.current_mode.value if self.hybrid_navigator.current_mode else 'SEARCH'
                else:
                    data['flight_mode'] = 'SEARCH'
                
                # Waypoint navigator
                if self.waypoint_navigator:
                    current_pos = {
                        'lat': data['mavlink']['gps']['lat'],
                        'lon': data['mavlink']['gps']['lon'],
                        'alt': data['mavlink']['gps']['alt']
                    }
                    data['waypoint'] = self.waypoint_navigator.update_navigation(current_pos)
                else:
                    data['waypoint'] = {
                        'active': False,
                        'current_wp_index': 0,
                        'total_waypoints': 0,
                        'distance_to_wp': 0.0,
                        'mission_completed': False
                    }
                
                # Signal emit et
                self.telemetry_updated.emit(data)
                
                # Güncelleme hızı
                self.msleep(GUIConfig.TELEMETRY_UPDATE_INTERVAL)
                
            except Exception as e:
                print(f"⚠️  EnhancedTelemetryThread hatası: {e}")
                self.msleep(100)
    
    def stop(self):
        """Thread'i durdur."""
        self.is_running = False
        self.wait()


# ============================================================================
# CAMERA WIDGET
# ============================================================================
class CameraWidget(QLabel):
    """
    Gelişmiş kamera görüntüleme widget'ı.
    Hedef İHA vurgulama, crosshair, ve overlay bilgileri ile.
    """
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: black; border: 2px solid #333;")
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Veri
        self.current_frame = None
        self.detections = []
        self.target_info = {'detected': False}
        self.fps = 0.0
    
    def update_frame(self, frame: np.ndarray, detections: List[Dict], target_info: Dict):
        """Frame'i günceller ve çizer."""
        self.current_frame = frame.copy()
        self.detections = detections
        self.target_info = target_info
        
        # Bounding box'ları çiz
        self._draw_detections()
        
        # Crosshair çiz
        self._draw_crosshair()
        
        # Overlay bilgileri
        self._draw_overlay()
        
        # QPixmap'e dönüştür ve göster
        self._display_frame()
    
    def update_fps(self, fps: float):
        """FPS'i günceller."""
        self.fps = fps
    
    def _draw_detections(self):
        """Tespitleri çizer."""
        if self.current_frame is None:
            return
        
        for det in self.detections:
            x1, y1, x2, y2 = det['bbox']
            
            # Hedef İHA mı kontrol et
            is_target = False
            if self.target_info['detected']:
                if det['bbox'] == self.target_info['bbox']:
                    is_target = True
            
            # Renk seç
            if is_target:
                color = Colors.BBOX_TARGET
                thickness = 3
            elif det['distance'] < 2.0:  # Kritik engel
                color = Colors.BBOX_CRITICAL
                thickness = 3
            else:
                color = Colors.BBOX_NORMAL
                thickness = 2
            
            # Bounding box
            cv2.rectangle(self.current_frame, (x1, y1), (x2, y2), color, thickness)
            
            # Label
            label = f"{det['class_name']} {det['confidence']:.2f}"
            if is_target:
                label = f"★ {label} ★"  # Yıldız ekle
            
            # Label arka planı
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(self.current_frame, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
            
            # Label metni
            cv2.putText(self.current_frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Mesafe
            distance_label = f"{det['distance']:.1f}m"
            cv2.putText(self.current_frame, distance_label, (x1, y2 + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def _draw_crosshair(self):
        """Frame merkezinde crosshair çizer."""
        if self.current_frame is None:
            return
        
        h, w = self.current_frame.shape[:2]
        cx, cy = w // 2, h // 2
        
        # Crosshair çizgileri
        line_len = 20
        color = (255, 255, 255)
        thickness = 2
        
        # Yatay
        cv2.line(self.current_frame, (cx - line_len, cy), (cx + line_len, cy), color, thickness)
        # Dikey
        cv2.line(self.current_frame, (cx, cy - line_len), (cx, cy + line_len), color, thickness)
        # Merkez nokta
        cv2.circle(self.current_frame, (cx, cy), 3, color, -1)
    
    def _draw_overlay(self):
        """Overlay bilgilerini çizer."""
        if self.current_frame is None:
            return
        
        # FPS ve tespit sayısı
        info_text = f"FPS: {self.fps:.1f} | Tespit: {len(self.detections)}"
        cv2.putText(self.current_frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Hedef bilgisi (varsa)
        if self.target_info['detected']:
            target_text = f"HEDEF: {self.target_info['distance']:.1f}m"
            cv2.putText(self.current_frame, target_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def _display_frame(self):
        """Frame'i QLabel'da gösterir."""
        if self.current_frame is None:
            return
        
        # BGR -> RGB
        rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        
        # QImage'e dönüştür
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # QPixmap'e dönüştür ve ölçeklendir
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled_pixmap)


# ============================================================================
# STATUS PANEL
# ============================================================================
class StatusPanel(QWidget):
    """
    Sağ taraftaki durum paneli.
    Mod, hedef, GPS, batarya, waypoint bilgilerini gösterir.
    """
    
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(350)
        self.setMinimumWidth(300)
        
        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Mod göstergesi
        self.mode_indicator = self._create_mode_indicator()
        layout.addWidget(self.mode_indicator)
        
        # Hedef bilgileri
        self.target_group = self._create_target_group()
        layout.addWidget(self.target_group)
        
        # GPS ve navigasyon
        self.gps_group = self._create_gps_group()
        layout.addWidget(self.gps_group)
        
        # Batarya
        self.battery_group = self._create_battery_group()
        layout.addWidget(self.battery_group)
        
        # Waypoint bilgileri
        self.waypoint_group = self._create_waypoint_group()
        layout.addWidget(self.waypoint_group)
        
        layout.addStretch()
    
    def _create_mode_indicator(self) -> QGroupBox:
        """Uçuş modu göstergesi oluşturur."""
        group = QGroupBox("🎯 UÇUŞ MODU")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        self.mode_label = QLabel("SEARCH 🔍")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet("""
            QLabel {
                background-color: #2196F3;
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.mode_label)
        
        self.mode_desc_label = QLabel("Waypoint takibi")
        self.mode_desc_label.setAlignment(Qt.AlignCenter)
        self.mode_desc_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.mode_desc_label)
        
        return group
    
    def _create_target_group(self) -> QGroupBox:
        """Hedef bilgileri grubu oluşturur."""
        group = QGroupBox("🎯 HEDEF İHA")
        layout = QGridLayout()
        group.setLayout(layout)
        
        self.target_status_label = QLabel("Durum:")
        self.target_status_value = QLabel("Tespit Edilmedi")
        self.target_status_value.setStyleSheet("color: gray;")
        
        self.target_distance_label = QLabel("Mesafe:")
        self.target_distance_value = QLabel("-")
        
        self.target_position_label = QLabel("Pozisyon:")
        self.target_position_value = QLabel("-")
        
        self.target_lock_label = QLabel("Kilitlenme:")
        self.target_lock_value = QLabel("-")
        
        layout.addWidget(self.target_status_label, 0, 0)
        layout.addWidget(self.target_status_value, 0, 1)
        layout.addWidget(self.target_distance_label, 1, 0)
        layout.addWidget(self.target_distance_value, 1, 1)
        layout.addWidget(self.target_position_label, 2, 0)
        layout.addWidget(self.target_position_value, 2, 1)
        layout.addWidget(self.target_lock_label, 3, 0)
        layout.addWidget(self.target_lock_value, 3, 1)
        
        return group
    
    def _create_gps_group(self) -> QGroupBox:
        """GPS ve navigasyon grubu oluşturur."""
        group = QGroupBox("📍 GPS & NAVİGASYON")
        layout = QGridLayout()
        group.setLayout(layout)
        
        self.gps_lat_label = QLabel("Enlem:")
        self.gps_lat_value = QLabel("-")
        
        self.gps_lon_label = QLabel("Boylam:")
        self.gps_lon_value = QLabel("-")
        
        self.gps_alt_label = QLabel("İrtifa:")
        self.gps_alt_value = QLabel("-")
        
        self.gps_speed_label = QLabel("Hız:")
        self.gps_speed_value = QLabel("-")
        
        self.gps_heading_label = QLabel("Heading:")
        self.gps_heading_value = QLabel("-")
        
        layout.addWidget(self.gps_lat_label, 0, 0)
        layout.addWidget(self.gps_lat_value, 0, 1)
        layout.addWidget(self.gps_lon_label, 1, 0)
        layout.addWidget(self.gps_lon_value, 1, 1)
        layout.addWidget(self.gps_alt_label, 2, 0)
        layout.addWidget(self.gps_alt_value, 2, 1)
        layout.addWidget(self.gps_speed_label, 3, 0)
        layout.addWidget(self.gps_speed_value, 3, 1)
        layout.addWidget(self.gps_heading_label, 4, 0)
        layout.addWidget(self.gps_heading_value, 4, 1)
        
        return group
    
    def _create_battery_group(self) -> QGroupBox:
        """Batarya grubu oluşturur."""
        group = QGroupBox("🔋 BATARYA")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Voltaj
        voltage_layout = QHBoxLayout()
        self.battery_voltage_label = QLabel("Voltaj:")
        self.battery_voltage_value = QLabel("-")
        voltage_layout.addWidget(self.battery_voltage_label)
        voltage_layout.addWidget(self.battery_voltage_value)
        voltage_layout.addStretch()
        layout.addLayout(voltage_layout)
        
        # Progress bar
        self.battery_progress = QProgressBar()
        self.battery_progress.setMaximum(100)
        self.battery_progress.setValue(0)
        self.battery_progress.setTextVisible(True)
        self.battery_progress.setFormat("%p%")
        layout.addWidget(self.battery_progress)
        
        return group
    
    def _create_waypoint_group(self) -> QGroupBox:
        """Waypoint bilgileri grubu oluşturur."""
        group = QGroupBox("📍 WAYPOINT")
        layout = QGridLayout()
        group.setLayout(layout)
        
        self.wp_current_label = QLabel("Aktif WP:")
        self.wp_current_value = QLabel("-")
        
        self.wp_distance_label = QLabel("Mesafe:")
        self.wp_distance_value = QLabel("-")
        
        self.wp_progress_label = QLabel("İlerleme:")
        self.wp_progress_bar = QProgressBar()
        self.wp_progress_bar.setMaximum(100)
        self.wp_progress_bar.setValue(0)
        
        layout.addWidget(self.wp_current_label, 0, 0)
        layout.addWidget(self.wp_current_value, 0, 1)
        layout.addWidget(self.wp_distance_label, 1, 0)
        layout.addWidget(self.wp_distance_value, 1, 1)
        layout.addWidget(self.wp_progress_label, 2, 0)
        layout.addWidget(self.wp_progress_bar, 2, 1)
        
        return group
    
    def update_mode(self, mode: str):
        """Uçuş modunu günceller."""
        mode_configs = {
            'SEARCH': (Icons.SEARCH, Colors.SEARCH, "Waypoint takibi"),
            'TRACK': (Icons.TRACK, Colors.TRACK, "Hedef takip modu"),
            'ATTACK': (Icons.ATTACK, Colors.ATTACK, "Saldırı modu"),
            'RETURN': (Icons.RETURN, Colors.RETURN, "Üsse dönüş"),
            'EMERGENCY': (Icons.EMERGENCY, Colors.EMERGENCY, "Acil kaçış!")
        }
        
        if mode in mode_configs:
            icon, color, desc = mode_configs[mode]
            self.mode_label.setText(f"{mode} {icon}")
            self.mode_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {color.name()};
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    padding: 15px;
                    border-radius: 5px;
                }}
            """)
            self.mode_desc_label.setText(desc)
    
    def update_target(self, target_info: Dict):
        """Hedef bilgilerini günceller."""
        if target_info.get('detected', False):
            self.target_status_value.setText("✅ Tespit Edildi")
            self.target_status_value.setStyleSheet("color: green; font-weight: bold;")
            self.target_distance_value.setText(f"{target_info.get('distance', 0):.1f} m")
            cx, cy = target_info.get('center', (0, 0))
            self.target_position_value.setText(f"({cx}, {cy})")
            # Kilitlenme süresi hesaplanabilir (şimdilik statik)
            self.target_lock_value.setText("Aktif")
        else:
            self.target_status_value.setText("❌ Tespit Edilmedi")
            self.target_status_value.setStyleSheet("color: gray;")
            self.target_distance_value.setText("-")
            self.target_position_value.setText("-")
            self.target_lock_value.setText("-")
    
    def update_gps(self, gps_data: Dict):
        """GPS bilgilerini günceller."""
        self.gps_lat_value.setText(f"{gps_data.get('lat', 0):.6f}°")
        self.gps_lon_value.setText(f"{gps_data.get('lon', 0):.6f}°")
        self.gps_alt_value.setText(f"{gps_data.get('alt', 0):.1f} m")
    
    def update_navigation(self, nav_data: Dict):
        """Navigasyon bilgilerini günceller."""
        self.gps_speed_value.setText(f"{nav_data.get('groundspeed', 0):.1f} m/s")
        self.gps_heading_value.setText(f"{nav_data.get('heading', 0):.1f}°")
    
    def update_battery(self, battery_data: Dict):
        """Batarya bilgilerini günceller."""
        voltage = battery_data.get('voltage', 0)
        remaining = battery_data.get('remaining', 0)
        
        self.battery_voltage_value.setText(f"{voltage:.1f} V")
        self.battery_progress.setValue(int(remaining))
        
        # Renk kodlama
        if remaining > 50:
            color = "green"
        elif remaining > 20:
            color = "orange"
        else:
            color = "red"
        
        self.battery_progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
    
    def update_waypoint(self, wp_data: Dict):
        """Waypoint bilgilerini günceller."""
        if wp_data.get('active', False):
            current = wp_data.get('current_wp_index', 0)
            total = wp_data.get('total_waypoints', 0)
            distance = wp_data.get('distance_to_wp', 0)
            
            self.wp_current_value.setText(f"{current + 1}/{total}")
            self.wp_distance_value.setText(f"{distance:.1f} m")
            
            # İlerleme yüzdesi
            if total > 0:
                progress = int((current / total) * 100)
                self.wp_progress_bar.setValue(progress)
        else:
            self.wp_current_value.setText("-")
            self.wp_distance_value.setText("-")
            self.wp_progress_bar.setValue(0)


# ============================================================================
# WAYPOINT MAP WIDGET
# ============================================================================
class WaypointMapWidget(QWidget):
    """
    Waypoint haritası widget'ı.
    Basit 2D harita gösterimi.
    """
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 250)
        self.waypoints = []
        self.current_wp_index = 0
        self.uav_position = None
    
    def update_waypoints(self, waypoints: List[Dict]):
        """Waypoint listesini günceller."""
        self.waypoints = waypoints
        self.update()
    
    def update_current_wp(self, index: int):
        """Aktif waypoint'i günceller."""
        self.current_wp_index = index
        self.update()
    
    def update_uav_position(self, lat: float, lon: float):
        """İHA pozisyonunu günceller."""
        self.uav_position = (lat, lon)
        self.update()
    
    def paintEvent(self, event):
        """Haritayı çizer."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # Başlık
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(10, 20, "Waypoint Haritası")
        
        if not self.waypoints:
            painter.drawText(self.rect(), Qt.AlignCenter, "Görev yüklenmedi")
            return
        
        # Waypoint'leri normalize et (harita alanına sığdır)
        margin = 40
        map_width = self.width() - 2 * margin
        map_height = self.height() - 2 * margin - 30
        
        # Min/max koordinatları bul
        lats = [wp['lat'] for wp in self.waypoints]
        lons = [wp['lon'] for wp in self.waypoints]
        
        if self.uav_position:
            lats.append(self.uav_position[0])
            lons.append(self.uav_position[1])
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Koordinat dönüşüm fonksiyonu
        def to_screen(lat, lon):
            if max_lat == min_lat:
                x = margin + map_width / 2
            else:
                x = margin + ((lon - min_lon) / (max_lon - min_lon)) * map_width
            
            if max_lat == min_lat:
                y = margin + 30 + map_height / 2
            else:
                y = margin + 30 + ((max_lat - lat) / (max_lat - min_lat)) * map_height
            
            return int(x), int(y)
        
        # Rota çizgisi
        painter.setPen(QPen(QColor(100, 100, 100), 2, Qt.DashLine))
        for i in range(len(self.waypoints) - 1):
            x1, y1 = to_screen(self.waypoints[i]['lat'], self.waypoints[i]['lon'])
            x2, y2 = to_screen(self.waypoints[i + 1]['lat'], self.waypoints[i + 1]['lon'])
            painter.drawLine(x1, y1, x2, y2)
        
        # Waypoint'ler
        for i, wp in enumerate(self.waypoints):
            x, y = to_screen(wp['lat'], wp['lon'])
            
            # Renk seç
            if i < self.current_wp_index:
                color = QColor(76, 175, 80)  # Yeşil (tamamlandı)
            elif i == self.current_wp_index:
                color = QColor(255, 152, 0)  # Turuncu (aktif)
            else:
                color = QColor(158, 158, 158)  # Gri (beklemede)
            
            # Waypoint çiz
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(x - 8, y - 8, 16, 16)
            
            # Numara
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.drawText(x - 4, y + 4, str(i + 1))
        
        # İHA pozisyonu
        if self.uav_position:
            x, y = to_screen(self.uav_position[0], self.uav_position[1])
            
            # İHA ikonu (üçgen)
            painter.setBrush(QBrush(QColor(33, 150, 243)))
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            points = [
                (x, y - 10),
                (x - 8, y + 8),
                (x + 8, y + 8)
            ]
            from PyQt5.QtCore import QPoint
            painter.drawPolygon(*[QPoint(px, py) for px, py in points])


# ============================================================================
# MAIN WINDOW
# ============================================================================
class TEKNOFESTGroundStation(QMainWindow):
    """
    TEKNOFEST Savaşan İHA - Ana Yer Kontrol İstasyonu.
    """
    
    def __init__(self, vision_processor=None, mavlink_interface=None, 
                 target_tracker=None, waypoint_navigator=None, hybrid_navigator=None):
        """
        TEKNOFESTGroundStation başlatıcı.
        
        Args:
            vision_processor: VisionProcessor instance
            mavlink_interface: MAVLinkInterface instance
            target_tracker: TargetTracker instance
            waypoint_navigator: WaypointNavigator instance
            hybrid_navigator: HybridNavigator instance
        """
        super().__init__()
        
        # Modüller
        self.vision_processor = vision_processor
        self.mavlink_interface = mavlink_interface
        self.target_tracker = target_tracker
        self.waypoint_navigator = waypoint_navigator
        self.hybrid_navigator = hybrid_navigator
        
        # Thread'ler
        self.video_thread = None
        self.telemetry_thread = None
        
        # Durum
        self.autonomous_mode = False
        self.target_lock_start_time = None
        
        # UI oluştur
        self._init_ui()
        
        # Thread'leri başlat
        self._start_threads()
        
        print("✅ TEKNOFESTGroundStation başlatıldı")
    
    def _init_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        self.setWindowTitle("🚁 TEKNOFEST Savaşan İHA - Yer Kontrol İstasyonu")
        self.setGeometry(50, 50, 1400, 900)
        
        # Merkezi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout (yatay)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Sol panel (kamera + alt bölüm)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Kamera widget
        self.camera_widget = CameraWidget()
        left_layout.addWidget(self.camera_widget, stretch=3)
        
        # Alt bölüm (waypoint haritası + kontrol)
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # Waypoint haritası
        self.waypoint_map = WaypointMapWidget()
        bottom_splitter.addWidget(self.waypoint_map)
        
        # Kontrol paneli
        control_panel = self._create_control_panel()
        bottom_splitter.addWidget(control_panel)
        
        bottom_splitter.setSizes([400, 400])
        left_layout.addWidget(bottom_splitter, stretch=1)
        
        # Sağ panel (durum)
        self.status_panel = StatusPanel()
        
        # Ana splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.status_panel)
        main_splitter.setSizes([1000, 350])
        
        main_layout.addWidget(main_splitter)
        
        # Sistem logları (alt)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        left_layout.addWidget(self.log_text)
        
        # Durum çubuğu
        self.statusBar().showMessage("Sistem Hazır")
    
    def _create_control_panel(self) -> QWidget:
        """Kontrol panelini oluşturur."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Otonom mod kontrolü
        auto_group = QGroupBox("⚙️ OTONOM MOD")
        auto_layout = QVBoxLayout()
        auto_group.setLayout(auto_layout)
        
        self.start_button = QPushButton("▶️ Otonom Modu Başlat")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self._start_autonomous_mode)
        auto_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹️ Otonom Modu Durdur")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.stop_button.clicked.connect(self._stop_autonomous_mode)
        self.stop_button.setEnabled(False)
        auto_layout.addWidget(self.stop_button)
        
        layout.addWidget(auto_group)
        
        # Acil durum
        emergency_group = QGroupBox("🚨 ACİL DURUM")
        emergency_layout = QVBoxLayout()
        emergency_group.setLayout(emergency_layout)
        
        self.emergency_button = QPushButton("🚨 ACİL DURDUR")
        self.emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
        """)
        self.emergency_button.clicked.connect(self._emergency_stop)
        emergency_layout.addWidget(self.emergency_button)
        
        layout.addWidget(emergency_group)
        
        # Görev yönetimi
        mission_group = QGroupBox("📁 GÖREV")
        mission_layout = QVBoxLayout()
        mission_group.setLayout(mission_layout)
        
        self.load_mission_button = QPushButton("📂 Görev Yükle")
        self.load_mission_button.clicked.connect(self._load_mission)
        mission_layout.addWidget(self.load_mission_button)
        
        self.return_home_button = QPushButton("🏠 Üsse Dön")
        self.return_home_button.clicked.connect(self._return_home)
        mission_layout.addWidget(self.return_home_button)
        
        layout.addWidget(mission_group)
        
        layout.addStretch()
        
        return panel
    
    def _start_threads(self):
        """Thread'leri başlatır."""
        # Video thread
        if self.vision_processor:
            self.video_thread = EnhancedVideoThread(self.vision_processor, self.target_tracker)
            self.video_thread.frame_ready.connect(self._update_video)
            self.video_thread.fps_updated.connect(self._update_fps)
            self.video_thread.start()
        
        # Telemetri thread
        self.telemetry_thread = EnhancedTelemetryThread(
            self.mavlink_interface,
            self.hybrid_navigator,
            self.waypoint_navigator
        )
        self.telemetry_thread.telemetry_updated.connect(self._update_telemetry)
        self.telemetry_thread.start()
    
    def _update_video(self, frame: np.ndarray, detections: List[Dict], target_info: Dict):
        """Video frame'i günceller."""
        self.camera_widget.update_frame(frame, detections, target_info)
        self.status_panel.update_target(target_info)
    
    def _update_fps(self, fps: float):
        """FPS'i günceller."""
        self.camera_widget.update_fps(fps)
    
    def _update_telemetry(self, data: Dict):
        """Telemetri verilerini günceller."""
        # Mod
        flight_mode = data.get('flight_mode', 'SEARCH')
        self.status_panel.update_mode(flight_mode)
        
        # GPS
        mavlink_data = data.get('mavlink', {})
        self.status_panel.update_gps(mavlink_data.get('gps', {}))
        self.status_panel.update_navigation(mavlink_data)
        self.status_panel.update_battery(mavlink_data.get('battery', {}))
        
        # Waypoint
        wp_data = data.get('waypoint', {})
        self.status_panel.update_waypoint(wp_data)
        
        # Waypoint haritası
        if self.waypoint_navigator and self.waypoint_navigator.waypoints:
            self.waypoint_map.update_waypoints([
                {'lat': wp.lat, 'lon': wp.lon} for wp in self.waypoint_navigator.waypoints
            ])
            self.waypoint_map.update_current_wp(wp_data.get('current_wp_index', 0))
        
        # İHA pozisyonu
        gps = mavlink_data.get('gps', {})
        if gps.get('lat') and gps.get('lon'):
            self.waypoint_map.update_uav_position(gps['lat'], gps['lon'])
        
        # Durum çubuğu
        connected = mavlink_data.get('connected', False)
        status_text = f"{'✅ Bağlı' if connected else '❌ Bağlantı Yok'} | "
        status_text += f"Mod: {flight_mode} | "
        status_text += f"Otonom: {'Aktif' if self.autonomous_mode else 'Pasif'}"
        self.statusBar().showMessage(status_text)
    
    def _start_autonomous_mode(self):
        """Otonom modu başlatır."""
        self.autonomous_mode = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self._log("▶️ Otonom mod başlatıldı")
    
    def _stop_autonomous_mode(self):
        """Otonom modu durdurur."""
        self.autonomous_mode = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._log("⏹️ Otonom mod durduruldu")
    
    def _emergency_stop(self):
        """Acil durdurma."""
        self.autonomous_mode = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._log("🚨 ACİL DURDURMA!")
        
        if self.mavlink_interface:
            self.mavlink_interface.disarm()
    
    def _load_mission(self):
        """Görev dosyası yükler."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Görev Dosyası Seç",
            "missions/",
            "JSON Files (*.json)"
        )
        
        if file_path and self.waypoint_navigator:
            try:
                self.waypoint_navigator.load_mission_from_file(file_path)
                self.waypoint_navigator.start_mission()
                self._log(f"📁 Görev yüklendi: {file_path}")
            except Exception as e:
                self._log(f"❌ Görev yükleme hatası: {e}")
    
    def _return_home(self):
        """Üsse dönüş komutu."""
        self._log("🏠 Üsse dönüş komutu verildi")
        # Hybrid navigator'a RETURN modu ayarlanabilir
    
    def _log(self, message: str):
        """Log mesajı ekler."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def is_autonomous_mode_active(self) -> bool:
        """Otonom mod durumunu döndürür."""
        return self.autonomous_mode
    
    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yapar."""
        print("🔌 TEKNOFEST GUI kapatılıyor...")
        
        if self.video_thread:
            self.video_thread.stop()
        if self.telemetry_thread:
            self.telemetry_thread.stop()
        
        event.accept()


# ============================================================================
# TEST FONKSİYONU
# ============================================================================
def test_gui():
    """GUI'yi test eder."""
    print("=" * 60)
    print("TEKNOFEST GROUND STATION TEST")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    window = TEKNOFESTGroundStation()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_gui()

