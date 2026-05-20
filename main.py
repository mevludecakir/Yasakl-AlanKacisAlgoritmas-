"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
Ana Orkestrasyon Modülü (Main Module)

Bu modül, tüm sistem bileşenlerini entegre eder ve ana kontrol döngüsünü yönetir.

Sistem Akışı:
1. Tüm modülleri başlat (vision, navigation, communication, GUI)
2. Ana kontrol döngüsü:
   - Kameradan frame al ve engelleri tespit et (vision)
   - Kaçış manevrası hesapla (navigation)
   - Komutları Pixhawk'a gönder (communication)
   - GUI'yi güncelle
3. Hata yönetimi ve graceful shutdown

Author: Computer Engineering
Platform: NVIDIA Jetson Nano + Pixhawk
"""

import sys
import time
import signal
from loguru import logger
from PyQt5.QtWidgets import QApplication

from config import (
    SystemConfig, LogConfig, validate_config
)
from vision import VisionProcessor
from navigation import ObstacleAvoidance
from communication import MAVLinkInterface
# TEKNOFEST Gelişmiş GUI
from gui_enhanced import TEKNOFESTGroundStation

# TEKNOFEST modülleri
from target_tracker import TargetTracker
from waypoint_navigator import WaypointNavigator
from hybrid_navigation import HybridNavigator, FlightMode


# ============================================================================
# MAIN SYSTEM CLASS
# ============================================================================
class UAVAutonomousSystem:
    """
    Ana sistem sınıfı - tüm modülleri entegre eder.
    """
    
    def __init__(self):
        """UAVAutonomousSystem başlatıcı."""
        self.vision = None
        self.navigation = None
        self.communication = None
        self.gui = None
        self.app = None
        
        # TEKNOFEST modülleri
        self.target_tracker = None
        self.waypoint_navigator = None
        self.hybrid_navigator = None
        
        self.is_running = False
        self.restart_attempts = 0
        
        # Logging konfigürasyonu
        self._setup_logging()
        
        logger.info("=" * 60)
        logger.info("OTONOM İHA SİSTEMİ BAŞLATILIYOR")
        logger.info("=" * 60)
    
    def _setup_logging(self):
        """Logging sistemini yapılandırır."""
        # Mevcut logger'ları temizle
        logger.remove()
        
        # Konsol logging
        if LogConfig.LOG_TO_CONSOLE:
            logger.add(
                sys.stderr,
                level=LogConfig.LOG_LEVEL,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
            )
        
        # Dosya logging
        if LogConfig.LOG_TO_FILE:
            import os
            os.makedirs(LogConfig.LOG_DIR, exist_ok=True)
            
            log_file = os.path.join(LogConfig.LOG_DIR, LogConfig.LOG_FILE_FORMAT)
            logger.add(
                log_file,
                level=LogConfig.LOG_LEVEL,
                rotation=LogConfig.LOG_ROTATION,
                retention=LogConfig.LOG_RETENTION,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
            )
    
    def initialize(self) -> bool:
        """
        Tüm sistem modüllerini başlatır.
        
        Returns:
            Başarılı ise True
        """
        try:
            # Konfigürasyon doğrulama
            logger.info("📋 Konfigürasyon doğrulanıyor...")
            if not validate_config():
                logger.error("❌ Konfigürasyon doğrulama başarısız")
                return False
            
            # Vision modülü
            logger.info("📷 Vision modülü başlatılıyor...")
            if not SystemConfig.SIMULATION_MODE:
                self.vision = VisionProcessor()
                self.vision.start()
            else:
                logger.warning("⚠️  Simülasyon modu: Vision modülü devre dışı")
            
            # Navigation modülü
            logger.info("🧭 Navigation modülü başlatılıyor...")
            self.navigation = ObstacleAvoidance()
            
            # TEKNOFEST modülleri
            logger.info("🎯 TEKNOFEST modülleri başlatılıyor...")
            self.target_tracker = TargetTracker()
            self.waypoint_navigator = WaypointNavigator()
            self.hybrid_navigator = HybridNavigator()
            
            # Communication modülü
            logger.info("📡 Communication modülü başlatılıyor...")
            if not SystemConfig.SIMULATION_MODE:
                try:
                    self.communication = MAVLinkInterface()
                    self.communication.start_telemetry_updates()
                except Exception as e:
                    logger.warning(f"⚠️  MAVLink bağlantısı kurulamadı: {e}")
                    logger.warning("   Sistem MAVLink olmadan devam edecek")
                    self.communication = None
            else:
                logger.warning("⚠️  Simülasyon modu: Communication modülü devre dışı")
            
            # GUI modülü (TEKNOFEST Gelişmiş GUI)
            logger.info("🖥️  GUI modülü başlatılıyor...")
            try:
                self.app = QApplication(sys.argv)
                self.gui = TEKNOFESTGroundStation(
                    vision_processor=self.vision,
                    mavlink_interface=self.communication,
                    target_tracker=self.target_tracker,
                    waypoint_navigator=self.waypoint_navigator,
                    hybrid_navigator=self.hybrid_navigator
                )
                logger.info("✅ TEKNOFEST GroundControlStation başlatıldı")
            except Exception as e:
                logger.error(f"❌ GUI başlatma hatası: {e}")
                raise # Re-raise the exception to stop initialization
            self.gui.show()
            
            logger.info("✅ Tüm modüller başarıyla başlatıldı")
            return True
            
        except Exception as e:
            logger.error(f"❌ Başlatma hatası: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def run(self):
        """
        Ana sistem döngüsünü çalıştırır.
        """
        try:
            self.is_running = True
            
            logger.info("▶️  Ana sistem döngüsü başlatıldı")
            logger.info(f"   Döngü frekansı: {SystemConfig.MAIN_LOOP_FREQUENCY} Hz")
            
            # Ana döngü (GUI event loop ile entegre)
            # QTimer ile periyodik kontrol döngüsü
            from PyQt5.QtCore import QTimer
            
            self.control_timer = QTimer()
            self.control_timer.timeout.connect(self._control_loop_iteration)
            self.control_timer.start(int(1000 / SystemConfig.MAIN_LOOP_FREQUENCY))
            
            # GUI event loop'u başlat
            sys.exit(self.app.exec_())
            
        except KeyboardInterrupt:
            logger.info("\n⏹️  Kullanıcı tarafından durduruldu (Ctrl+C)")
            self.shutdown()
        
        except Exception as e:
            logger.error(f"❌ Ana döngü hatası: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Yeniden başlatma denemesi
            if SystemConfig.MAX_RESTART_ATTEMPTS > 0 and \
               self.restart_attempts < SystemConfig.MAX_RESTART_ATTEMPTS:
                self.restart_attempts += 1
                logger.warning(f"🔄 Yeniden başlatma denemesi {self.restart_attempts}/{SystemConfig.MAX_RESTART_ATTEMPTS}")
                time.sleep(2)
                self.run()
            else:
                self.shutdown()
    
    def _control_loop_iteration(self):
        """
        Ana kontrol döngüsünün bir iterasyonu (TEKNOFEST Hibrit Navigasyon).
        QTimer tarafından periyodik olarak çağrılır.
        """
        try:
            # Otonom mod kontrolü
            if not self.gui or not self.gui.is_autonomous_mode_active():
                return
            
            # 1. Vision: Frame al ve tespitler yap
            detections = []
            if self.vision:
                frame, detections = self.vision.get_frame_and_detections()
            
            # 2. Telemetri al
            telemetry = {'battery': {'remaining': 100}, 'heading': 0.0, 'gps': {'lat': 0.0, 'lon': 0.0, 'alt': 0.0}}
            current_heading = 0.0
            current_position = {'lat': 0.0, 'lon': 0.0, 'alt': 0.0}
            
            if self.communication:
                telemetry = self.communication.get_telemetry()
                current_heading = telemetry['heading']
                current_position = {
                    'lat': telemetry['gps']['lat'],
                    'lon': telemetry['gps']['lon'],
                    'alt': telemetry['gps']['alt']
                }
            
            # 3. Hedef İHA Tespiti ve Takip
            target = None
            tracking_command = {'tracking_active': False, 'yaw_rate': 0.0, 'pitch_rate': 0.0, 'target_distance': 0.0}
            
            if self.target_tracker and detections:
                target = self.target_tracker.detect_target_uav(detections)
                tracking_command = self.target_tracker.calculate_tracking_command(target)
            
            # 4. Waypoint Navigasyon
            waypoint_nav = {'active': False, 'target_bearing': 0.0, 'distance_to_wp': 0.0, 'mission_completed': False}
            
            if self.waypoint_navigator:
                waypoint_nav = self.waypoint_navigator.update_navigation(current_position)
            
            # 5. Hibrit Navigasyon - Mod Yönetimi ve Komut Hesaplama
            if self.hybrid_navigator:
                # Hedef tespit durumuna göre otomatik mod güncelleme
                from hybrid_navigation import FlightMode
                
                if target and tracking_command['tracking_active']:
                    # Hedef tespit edildi
                    target_distance = tracking_command.get('target_distance', 0.0)
                    
                    if target_distance < 20.0:  # 20m'den yakın - saldırı modu
                        self.hybrid_navigator.set_mode(FlightMode.ATTACK)
                    else:  # Uzaktan takip
                        self.hybrid_navigator.set_mode(FlightMode.TRACK)
                else:
                    # Hedef yok
                    if waypoint_nav.get('mission_completed', False):
                        self.hybrid_navigator.set_mode(FlightMode.RETURN)
                    else:
                        self.hybrid_navigator.set_mode(FlightMode.SEARCH)
                
                # Hibrit navigasyon komutu hesapla
                hybrid_command = self.hybrid_navigator.calculate_hybrid_command(
                    waypoint_nav=waypoint_nav,
                    tracking_command=tracking_command,
                    avoidance_command={'active': False, 'yaw_rate': 0.0},  # APF şimdilik pasif
                    current_heading=current_heading
                )
                
                # 6. Komutları Pixhawk'a Gönder
                if self.communication and hybrid_command:
                    self.communication.send_velocity_command(
                        vx=0.0,  # İleri hız (m/s)
                        vy=0.0,  # Yan hız (m/s)
                        vz=0.0,  # Dikey hız (m/s)
                        yaw_rate=hybrid_command.get('yaw_rate', 0.0)
                    )
                
                # 7. Durum Logları
                current_mode = self.hybrid_navigator.current_mode
                if current_mode:
                    logger.debug(f"Mod: {current_mode.value} | Yaw: {hybrid_command.get('yaw_rate', 0.0):.2f}")
            
            # 8. Batarya kontrolü
            if telemetry['battery']['remaining'] < 20:
                logger.warning(f"⚠️  Düşük batarya: {telemetry['battery']['remaining']}%")
                from hybrid_navigation import FlightMode
                if self.hybrid_navigator:
                    self.hybrid_navigator.set_mode(FlightMode.EMERGENCY)
            
            # Performans metrikleri
            if SystemConfig.COLLECT_PERFORMANCE_METRICS:
                if self.vision:
                    fps = self.vision.get_fps()
                    if fps < 10:
                        logger.warning(f"⚠️  Düşük FPS: {fps:.1f}")
        
        except Exception as e:
            logger.error(f"⚠️  Kontrol döngüsü iterasyon hatası: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def shutdown(self):
        """
        Sistemi güvenli şekilde kapatır.
        """
        logger.info("🔌 Sistem kapatılıyor...")
        
        self.is_running = False
        
        # Modülleri kapat
        if self.vision:
            self.vision.release()
        
        if self.communication:
            self.communication.close()
        
        logger.info("✅ Sistem güvenli şekilde kapatıldı")


# ============================================================================
# SIGNAL HANDLER
# ============================================================================
def signal_handler(sig, frame):
    """Ctrl+C ve diğer sinyalleri yakalar."""
    logger.info("\n⏹️  Sinyal alındı, sistem kapatılıyor...")
    sys.exit(0)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main():
    """
    Ana giriş noktası.
    """
    # Signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Sistem oluştur
    system = UAVAutonomousSystem()
    
    # Başlat
    if system.initialize():
        # Çalıştır
        system.run()
    else:
        logger.error("❌ Sistem başlatılamadı")
        sys.exit(1)


if __name__ == "__main__":
    main()
