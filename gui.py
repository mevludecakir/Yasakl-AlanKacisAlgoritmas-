"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
Grafik Kullanıcı Arayüzü (GUI Module)

Bu modül, PyQt5 kullanarak Yer Kontrol İstasyonu (Ground Control Station)
arayüzünü sağlar. Anlık video akışı, tespit edilen nesne kutuları ve
İHA telemetri verilerini gösterir.

Özellikler:
- PyQt5 tabanlı modern arayüz
- QThread ile asenkron video streaming (ana thread'i dondurmaz)
- Bounding box görselleştirmesi
- Telemetri veri paneli
- Kontrol butonları (start/stop, emergency)

Author: Computer Engineering
Platform: NVIDIA Jetson Nano
"""

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QGroupBox, QGridLayout,
    QTextEdit, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
from typing import Optional, List, Dict

from config import GUIConfig


# ============================================================================
# VIDEO THREAD
# ============================================================================
class VideoThread(QThread):
    """
    Asenkron video streaming thread'i.
    Ana GUI thread'ini dondurmadan video frame'lerini işler.
    """
    
    # Signals
    frame_ready = pyqtSignal(np.ndarray, list)  # (frame, detections)
    fps_updated = pyqtSignal(float)  # fps
    
    def __init__(self, vision_processor):
        """
        VideoThread başlatıcı.
        
        Args:
            vision_processor: VisionProcessor instance
        """
        super().__init__()
        self.vision_processor = vision_processor
        self.is_running = False
    
    def run(self):
        """Thread ana döngüsü."""
        self.is_running = True
        
        while self.is_running:
            try:
                # Frame ve tespitleri al
                frame, detections = self.vision_processor.get_frame_and_detections()
                
                if frame is not None:
                    # Signal emit et
                    self.frame_ready.emit(frame, detections)
                    
                    # FPS güncelle
                    fps = self.vision_processor.get_fps()
                    self.fps_updated.emit(fps)
                
                # Frame rate kontrolü
                self.msleep(GUIConfig.VIDEO_UPDATE_INTERVAL)
                
            except Exception as e:
                print(f"⚠️  VideoThread hatası: {e}")
                self.msleep(100)
    
    def stop(self):
        """Thread'i durdur."""
        self.is_running = False
        self.wait()


# ============================================================================
# TELEMETRY THREAD
# ============================================================================
class TelemetryThread(QThread):
    """
    Asenkron telemetri güncelleme thread'i.
    """
    
    # Signal
    telemetry_updated = pyqtSignal(dict)  # telemetry data
    
    def __init__(self, mavlink_interface):
        """
        TelemetryThread başlatıcı.
        
        Args:
            mavlink_interface: MAVLinkInterface instance
        """
        super().__init__()
        self.mavlink_interface = mavlink_interface
        self.is_running = False
    
    def run(self):
        """Thread ana döngüsü."""
        self.is_running = True
        
        while self.is_running:
            try:
                # Telemetri verilerini al
                telemetry = self.mavlink_interface.get_telemetry()
                
                # Signal emit et
                self.telemetry_updated.emit(telemetry)
                
                # Güncelleme hızı
                self.msleep(GUIConfig.TELEMETRY_UPDATE_INTERVAL)
                
            except Exception as e:
                print(f"⚠️  TelemetryThread hatası: {e}")
                self.msleep(100)
    
    def stop(self):
        """Thread'i durdur."""
        self.is_running = False
        self.wait()


# ============================================================================
# GROUND CONTROL STATION
# ============================================================================
class GroundControlStation(QMainWindow):
    """
    Ana Yer Kontrol İstasyonu penceresi.
    """
    
    def __init__(self, vision_processor=None, mavlink_interface=None, navigation=None):
        """
        GroundControlStation başlatıcı.
        
        Args:
            vision_processor: VisionProcessor instance
            mavlink_interface: MAVLinkInterface instance
            navigation: ObstacleAvoidance instance
        """
        super().__init__()
        
        self.vision_processor = vision_processor
        self.mavlink_interface = mavlink_interface
        self.navigation = navigation
        
        # Thread'ler
        self.video_thread = None
        self.telemetry_thread = None
        
        # Durum değişkenleri
        self.autonomous_mode = False
        self.current_detections = []
        self.current_fps = 0.0
        
        # UI oluştur
        self._init_ui()
        
        # Thread'leri başlat
        if self.vision_processor:
            self._start_video_thread()
        if self.mavlink_interface:
            self._start_telemetry_thread()
        
        print("✅ GroundControlStation başlatıldı")
    
    def _init_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        self.setWindowTitle("Otonom İHA Yer Kontrol İstasyonu")
        self.setGeometry(100, 100, GUIConfig.WINDOW_WIDTH, GUIConfig.WINDOW_HEIGHT)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Tab 1: Video ve Tespit
        video_tab = self._create_video_tab()
        tabs.addTab(video_tab, "📹 Video & Tespit")
        
        # Tab 2: Telemetri
        telemetry_tab = self._create_telemetry_tab()
        tabs.addTab(telemetry_tab, "📡 Telemetri")
        
        # Tab 3: Kontrol
        control_tab = self._create_control_tab()
        tabs.addTab(control_tab, "🎮 Kontrol")
        
        # Durum çubuğu
        self.statusBar().showMessage("Sistem Hazır")
    
    def _create_video_tab(self) -> QWidget:
        """Video tab'ını oluşturur."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Video label
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; border: 2px solid #333;")
        self.video_label.setMinimumSize(640, 480)
        layout.addWidget(self.video_label)
        
        # Bilgi paneli
        info_layout = QHBoxLayout()
        layout.addLayout(info_layout)
        
        # FPS
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(self.fps_label)
        
        # Tespit sayısı
        self.detection_count_label = QLabel("Tespit: 0")
        self.detection_count_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(self.detection_count_label)
        
        # En yakın engel
        self.closest_obstacle_label = QLabel("En Yakın: -")
        self.closest_obstacle_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(self.closest_obstacle_label)
        
        info_layout.addStretch()
        
        return tab
    
    def _create_telemetry_tab(self) -> QWidget:
        """Telemetri tab'ını oluşturur."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # GPS Group
        gps_group = QGroupBox("GPS Bilgileri")
        gps_layout = QGridLayout()
        gps_group.setLayout(gps_layout)
        layout.addWidget(gps_group)
        
        self.gps_lat_label = QLabel("Enlem: -")
        self.gps_lon_label = QLabel("Boylam: -")
        self.gps_alt_label = QLabel("İrtifa: -")
        self.gps_fix_label = QLabel("Fix: -")
        
        gps_layout.addWidget(QLabel("📍"), 0, 0)
        gps_layout.addWidget(self.gps_lat_label, 0, 1)
        gps_layout.addWidget(self.gps_lon_label, 1, 1)
        gps_layout.addWidget(self.gps_alt_label, 2, 1)
        gps_layout.addWidget(self.gps_fix_label, 3, 1)
        
        # Attitude Group
        attitude_group = QGroupBox("Attitude Bilgileri")
        attitude_layout = QGridLayout()
        attitude_group.setLayout(attitude_layout)
        layout.addWidget(attitude_group)
        
        self.roll_label = QLabel("Roll: -")
        self.pitch_label = QLabel("Pitch: -")
        self.yaw_label = QLabel("Yaw: -")
        self.heading_label = QLabel("Heading: -")
        
        attitude_layout.addWidget(QLabel("🧭"), 0, 0)
        attitude_layout.addWidget(self.roll_label, 0, 1)
        attitude_layout.addWidget(self.pitch_label, 1, 1)
        attitude_layout.addWidget(self.yaw_label, 2, 1)
        attitude_layout.addWidget(self.heading_label, 3, 1)
        
        # Sistem Durumu Group
        status_group = QGroupBox("Sistem Durumu")
        status_layout = QGridLayout()
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        self.mode_label = QLabel("Mod: -")
        self.armed_label = QLabel("Armed: -")
        self.speed_label = QLabel("Hız: -")
        self.battery_label = QLabel("Batarya: -")
        self.battery_progress = QProgressBar()
        self.battery_progress.setMaximum(100)
        
        status_layout.addWidget(QLabel("⚙️"), 0, 0)
        status_layout.addWidget(self.mode_label, 0, 1)
        status_layout.addWidget(self.armed_label, 1, 1)
        status_layout.addWidget(self.speed_label, 2, 1)
        status_layout.addWidget(self.battery_label, 3, 1)
        status_layout.addWidget(self.battery_progress, 4, 1)
        
        layout.addStretch()
        
        return tab
    
    def _create_control_tab(self) -> QWidget:
        """Kontrol tab'ını oluşturur."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Otonom Mod Kontrolü
        auto_group = QGroupBox("Otonom Mod Kontrolü")
        auto_layout = QVBoxLayout()
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        self.start_button = QPushButton("▶️  Otonom Modu Başlat")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;")
        self.start_button.clicked.connect(self._start_autonomous_mode)
        auto_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹️  Otonom Modu Durdur")
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-size: 16px; padding: 10px;")
        self.stop_button.clicked.connect(self._stop_autonomous_mode)
        self.stop_button.setEnabled(False)
        auto_layout.addWidget(self.stop_button)
        
        # Acil Durum
        emergency_group = QGroupBox("Acil Durum")
        emergency_layout = QVBoxLayout()
        emergency_group.setLayout(emergency_layout)
        layout.addWidget(emergency_group)
        
        self.emergency_button = QPushButton("🚨 ACİL DURDUR")
        self.emergency_button.setStyleSheet("background-color: #FF5722; color: white; font-size: 18px; font-weight: bold; padding: 15px;")
        self.emergency_button.clicked.connect(self._emergency_stop)
        emergency_layout.addWidget(self.emergency_button)
        
        # Sistem Logları
        log_group = QGroupBox("Sistem Logları")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        layout.addStretch()
        
        return tab
    
    def _start_video_thread(self):
        """Video thread'ini başlatır."""
        if self.video_thread is None:
            self.video_thread = VideoThread(self.vision_processor)
            self.video_thread.frame_ready.connect(self._update_video_frame)
            self.video_thread.fps_updated.connect(self._update_fps)
            self.video_thread.start()
    
    def _start_telemetry_thread(self):
        """Telemetri thread'ini başlatır."""
        if self.telemetry_thread is None:
            self.telemetry_thread = TelemetryThread(self.mavlink_interface)
            self.telemetry_thread.telemetry_updated.connect(self._update_telemetry)
            self.telemetry_thread.start()
    
    def _update_video_frame(self, frame: np.ndarray, detections: List[Dict]):
        """Video frame'i günceller (slot)."""
        self.current_detections = detections
        
        # Bounding box'ları çiz
        display_frame = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class_name']} {det['confidence']:.2f}"
            distance_label = f"{det['distance']:.1f}m"
            
            # Bounding box
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), 
                         GUIConfig.BBOX_COLOR, GUIConfig.BBOX_THICKNESS)
            
            # Label arka planı
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 
                                                     GUIConfig.FONT_SCALE, GUIConfig.FONT_THICKNESS)
            cv2.rectangle(display_frame, (x1, y1 - label_h - 10), (x1 + label_w, y1),
                         GUIConfig.TEXT_BG_COLOR, -1)
            
            # Label metni
            cv2.putText(display_frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, GUIConfig.FONT_SCALE,
                       GUIConfig.TEXT_COLOR, GUIConfig.FONT_THICKNESS)
            
            # Mesafe
            cv2.putText(display_frame, distance_label, (x1, y2 + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, GUIConfig.FONT_SCALE,
                       GUIConfig.TEXT_COLOR, GUIConfig.FONT_THICKNESS)
        
        # QImage'e dönüştür
        height, width, channel = display_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(display_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
        # QPixmap'e dönüştür ve göster
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)
        
        # Tespit sayısını güncelle
        self.detection_count_label.setText(f"Tespit: {len(detections)}")
        
        # En yakın engeli güncelle
        if detections:
            closest = min(detections, key=lambda d: d['distance'])
            self.closest_obstacle_label.setText(f"En Yakın: {closest['distance']:.1f}m ({closest['class_name']})")
        else:
            self.closest_obstacle_label.setText("En Yakın: -")
    
    def _update_fps(self, fps: float):
        """FPS değerini günceller (slot)."""
        self.current_fps = fps
        self.fps_label.setText(f"FPS: {fps:.1f}")
    
    def _update_telemetry(self, telemetry: Dict):
        """Telemetri verilerini günceller (slot)."""
        # GPS
        self.gps_lat_label.setText(f"Enlem: {telemetry['gps']['lat']:.6f}")
        self.gps_lon_label.setText(f"Boylam: {telemetry['gps']['lon']:.6f}")
        self.gps_alt_label.setText(f"İrtifa: {telemetry['gps']['alt']:.1f} m")
        self.gps_fix_label.setText(f"Fix: {telemetry['gps']['fix']}")
        
        # Attitude
        self.roll_label.setText(f"Roll: {telemetry['attitude']['roll']:.1f}°")
        self.pitch_label.setText(f"Pitch: {telemetry['attitude']['pitch']:.1f}°")
        self.yaw_label.setText(f"Yaw: {telemetry['attitude']['yaw']:.1f}°")
        self.heading_label.setText(f"Heading: {telemetry['heading']:.1f}°")
        
        # Sistem Durumu
        self.mode_label.setText(f"Mod: {telemetry['mode']}")
        self.armed_label.setText(f"Armed: {'✅ Evet' if telemetry['armed'] else '❌ Hayır'}")
        self.speed_label.setText(f"Hız: {telemetry['groundspeed']:.1f} m/s")
        self.battery_label.setText(f"Batarya: {telemetry['battery']['voltage']:.1f}V")
        self.battery_progress.setValue(int(telemetry['battery']['remaining']))
        
        # Bağlantı durumu
        if telemetry['connected']:
            self.statusBar().showMessage("✅ Bağlı | Otonom Mod: " + ("Aktif" if self.autonomous_mode else "Pasif"))
        else:
            self.statusBar().showMessage("❌ Bağlantı Yok")
    
    def _start_autonomous_mode(self):
        """Otonom modu başlatır."""
        self.autonomous_mode = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self._log("▶️  Otonom mod başlatıldı")
        print("▶️  Otonom mod başlatıldı")
    
    def _stop_autonomous_mode(self):
        """Otonom modu durdurur."""
        self.autonomous_mode = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._log("⏹️  Otonom mod durduruldu")
        print("⏹️  Otonom mod durduruldu")
    
    def _emergency_stop(self):
        """Acil durdurma."""
        self.autonomous_mode = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._log("🚨 ACİL DURDURMA!")
        print("🚨 ACİL DURDURMA!")
        
        # MAVLink'e disarm komutu gönder
        if self.mavlink_interface:
            self.mavlink_interface.disarm()
    
    def _log(self, message: str):
        """Log mesajı ekler."""
        self.log_text.append(message)
    
    def is_autonomous_mode_active(self) -> bool:
        """Otonom mod durumunu döndürür."""
        return self.autonomous_mode
    
    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yapar."""
        print("🔌 GUI kapatılıyor...")
        
        # Thread'leri durdur
        if self.video_thread:
            self.video_thread.stop()
        if self.telemetry_thread:
            self.telemetry_thread.stop()
        
        event.accept()


# ============================================================================
# TEST FONKSİYONU
# ============================================================================
def test_gui_module():
    """GUI modülünü test eder."""
    print("=" * 60)
    print("GUI MODÜLÜ TEST")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Simülasyon için dummy veriler
    window = GroundControlStation()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_gui_module()
