"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
İletişim Modülü (Communication Module)

Bu modül, MAVLink protokolü üzerinden Pixhawk uçuş kontrol kartı ile
iletişim kurar. Telemetri verilerini okur ve navigasyon komutlarını gönderir.

Özellikler:
- pymavlink ile Pixhawk bağlantısı
- Heartbeat yönetimi
- Telemetri veri okuma (GPS, attitude, battery, mode)
- Komut gönderme (guided mode, heading adjustment)
- Thread-safe telemetri erişimi

Author: Computer Engineering
Platform: NVIDIA Jetson Nano + Pixhawk
"""

from pymavlink import mavutil
from threading import Lock, Thread
from typing import Optional, Dict
import time
import math

from config import MAVLinkConfig


# ============================================================================
# MAVLINK INTERFACE CLASS
# ============================================================================
class MAVLinkInterface:
    """
    Pixhawk ile MAVLink iletişim sınıfı.
    """
    
    def __init__(self, connection_string: str = None):
        """
        MAVLinkInterface başlatıcı.
        
        Args:
            connection_string: Bağlantı string'i (None ise config'den alınır)
        """
        self.connection_string = connection_string or MAVLinkConfig.CONNECTION_STRING
        self.master = None
        
        # Thread-safe telemetri verileri
        self.telemetry = {
            'connected': False,
            'armed': False,
            'mode': 'UNKNOWN',
            'gps': {'lat': 0.0, 'lon': 0.0, 'alt': 0.0, 'fix': 0},
            'attitude': {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0},
            'velocity': {'vx': 0.0, 'vy': 0.0, 'vz': 0.0},
            'battery': {'voltage': 0.0, 'current': 0.0, 'remaining': 100},
            'heading': 0.0,
            'groundspeed': 0.0,
            'airspeed': 0.0,
            'altitude_rel': 0.0,
            'last_heartbeat': 0.0
        }
        self.telemetry_lock = Lock()
        
        # Telemetri güncelleme thread'i
        self.is_running = False
        self.telemetry_thread = None
        
        # Bağlantı
        self._connect()
        
        print("✅ MAVLinkInterface başlatıldı")
    
    def _connect(self):
        """Pixhawk'a bağlanır."""
        try:
            print(f"🔌 Pixhawk'a bağlanılıyor: {self.connection_string}")
            
            # MAVLink bağlantısı oluştur
            self.master = mavutil.mavlink_connection(
                self.connection_string,
                baud=MAVLinkConfig.BAUD_RATE
            )
            
            # Heartbeat bekle
            print("   Heartbeat bekleniyor...")
            self.master.wait_heartbeat(timeout=MAVLinkConfig.CONNECTION_TIMEOUT)
            
            print(f"✅ Bağlantı kuruldu (System ID: {self.master.target_system}, "
                  f"Component ID: {self.master.target_component})")
            
            with self.telemetry_lock:
                self.telemetry['connected'] = True
                self.telemetry['last_heartbeat'] = time.time()
            
        except Exception as e:
            print(f"❌ Bağlantı hatası: {e}")
            with self.telemetry_lock:
                self.telemetry['connected'] = False
    
    def start_telemetry_updates(self):
        """Telemetri güncelleme thread'ini başlatır."""
        if self.is_running:
            print("⚠️  Telemetri güncellemeleri zaten çalışıyor")
            return
        
        self.is_running = True
        self.telemetry_thread = Thread(target=self._telemetry_loop, daemon=True)
        self.telemetry_thread.start()
        print("▶️  Telemetri güncellemeleri başlatıldı")
    
    def stop_telemetry_updates(self):
        """Telemetri güncelleme thread'ini durdurur."""
        self.is_running = False
        if self.telemetry_thread:
            self.telemetry_thread.join(timeout=2.0)
        print("⏹️  Telemetri güncellemeleri durduruldu")
    
    def _telemetry_loop(self):
        """Telemetri güncelleme döngüsü (thread'de çalışır)."""
        while self.is_running:
            try:
                # MAVLink mesajlarını oku
                msg = self.master.recv_match(blocking=False, timeout=0.1)
                
                if msg:
                    self._process_message(msg)
                
                # Heartbeat gönder
                self._send_heartbeat()
                
                # Güncelleme hızı
                time.sleep(1.0 / MAVLinkConfig.TELEMETRY_UPDATE_RATE)
                
            except Exception as e:
                print(f"⚠️  Telemetri döngüsü hatası: {e}")
                time.sleep(0.1)
    
    def _process_message(self, msg):
        """MAVLink mesajını işler ve telemetri verilerini günceller."""
        msg_type = msg.get_type()
        
        with self.telemetry_lock:
            # HEARTBEAT
            if msg_type == 'HEARTBEAT':
                self.telemetry['last_heartbeat'] = time.time()
                self.telemetry['armed'] = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                
                # Flight mode
                mode_mapping = self.master.mode_mapping()
                if mode_mapping and msg.custom_mode in mode_mapping:
                    self.telemetry['mode'] = mode_mapping[msg.custom_mode]
            
            # GPS
            elif msg_type == 'GPS_RAW_INT':
                self.telemetry['gps']['lat'] = msg.lat / 1e7
                self.telemetry['gps']['lon'] = msg.lon / 1e7
                self.telemetry['gps']['alt'] = msg.alt / 1000.0
                self.telemetry['gps']['fix'] = msg.fix_type
            
            # ATTITUDE
            elif msg_type == 'ATTITUDE':
                self.telemetry['attitude']['roll'] = math.degrees(msg.roll)
                self.telemetry['attitude']['pitch'] = math.degrees(msg.pitch)
                self.telemetry['attitude']['yaw'] = math.degrees(msg.yaw)
                self.telemetry['heading'] = math.degrees(msg.yaw)
            
            # GLOBAL_POSITION_INT
            elif msg_type == 'GLOBAL_POSITION_INT':
                self.telemetry['altitude_rel'] = msg.relative_alt / 1000.0
                self.telemetry['velocity']['vx'] = msg.vx / 100.0
                self.telemetry['velocity']['vy'] = msg.vy / 100.0
                self.telemetry['velocity']['vz'] = msg.vz / 100.0
                self.telemetry['heading'] = msg.hdg / 100.0
            
            # VFR_HUD
            elif msg_type == 'VFR_HUD':
                self.telemetry['groundspeed'] = msg.groundspeed
                self.telemetry['airspeed'] = msg.airspeed
                self.telemetry['heading'] = msg.heading
            
            # BATTERY_STATUS
            elif msg_type == 'SYS_STATUS':
                self.telemetry['battery']['voltage'] = msg.voltage_battery / 1000.0
                self.telemetry['battery']['current'] = msg.current_battery / 100.0
                self.telemetry['battery']['remaining'] = msg.battery_remaining
    
    def _send_heartbeat(self):
        """Heartbeat mesajı gönderir."""
        try:
            self.master.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0, 0, 0
            )
        except Exception as e:
            print(f"⚠️  Heartbeat gönderme hatası: {e}")
    
    def get_telemetry(self) -> Dict:
        """
        Thread-safe şekilde güncel telemetri verilerini döndürür.
        
        Returns:
            Telemetri verileri dict
        """
        with self.telemetry_lock:
            return self.telemetry.copy()
    
    def is_connected(self) -> bool:
        """Bağlantı durumunu kontrol eder."""
        with self.telemetry_lock:
            # Son heartbeat 3 saniyeden eskiyse bağlantı kopmuş sayılır
            if time.time() - self.telemetry['last_heartbeat'] > 3.0:
                self.telemetry['connected'] = False
            return self.telemetry['connected']
    
    def set_mode(self, mode: str) -> bool:
        """
        Uçuş modunu değiştirir.
        
        Args:
            mode: Mod adı (örn: 'GUIDED', 'LOITER', 'RTL')
        
        Returns:
            Başarılı ise True
        """
        try:
            # Mode ID'yi al
            mode_mapping = self.master.mode_mapping()
            if mode not in mode_mapping.values():
                print(f"⚠️  Geçersiz mod: {mode}")
                return False
            
            mode_id = [k for k, v in mode_mapping.items() if v == mode][0]
            
            # Mod değiştirme komutu gönder
            self.master.set_mode(mode_id)
            print(f"✈️  Mod değiştirildi: {mode}")
            return True
            
        except Exception as e:
            print(f"❌ Mod değiştirme hatası: {e}")
            return False
    
    def arm(self) -> bool:
        """İHA'yı arm eder (motorları aktif hale getirir)."""
        try:
            self.master.arducopter_arm()
            print("🔓 İHA arm edildi")
            return True
        except Exception as e:
            print(f"❌ Arm hatası: {e}")
            return False
    
    def disarm(self) -> bool:
        """İHA'yı disarm eder (motorları devre dışı bırakır)."""
        try:
            self.master.arducopter_disarm()
            print("🔒 İHA disarm edildi")
            return True
        except Exception as e:
            print(f"❌ Disarm hatası: {e}")
            return False
    
    def send_heading_command(self, heading: float, speed: float = 1.0):
        """
        Yeni heading (yön) komutu gönderir.
        
        Args:
            heading: Hedef yön (derece, 0-360, 0=Kuzey)
            speed: Hız (m/s)
        """
        try:
            # Heading'i 0-360 arasına normalize et
            heading = heading % 360
            
            # SET_POSITION_TARGET_GLOBAL_INT mesajı
            self.master.mav.set_position_target_global_int_send(
                0,  # time_boot_ms
                self.master.target_system,
                self.master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                0b0000111111000111,  # type_mask (sadece yaw ve velocity kullan)
                0,  # lat
                0,  # lon
                0,  # alt
                speed,  # vx
                0,  # vy
                0,  # vz
                0,  # afx
                0,  # afy
                0,  # afz
                math.radians(heading),  # yaw
                0   # yaw_rate
            )
            
            print(f"🧭 Heading komutu gönderildi: {heading:.1f}°, Hız: {speed:.1f} m/s")
            
        except Exception as e:
            print(f"❌ Heading komutu hatası: {e}")
    
    def send_velocity_command(self, vx: float, vy: float, vz: float):
        """
        Hız komutu gönderir (NED frame).
        
        Args:
            vx: Kuzey yönünde hız (m/s)
            vy: Doğu yönünde hız (m/s)
            vz: Aşağı yönünde hız (m/s, negatif yukarı)
        """
        try:
            self.master.mav.set_position_target_local_ned_send(
                0,  # time_boot_ms
                self.master.target_system,
                self.master.target_component,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                0b0000111111000111,  # type_mask
                0, 0, 0,  # position
                vx, vy, vz,  # velocity
                0, 0, 0,  # acceleration
                0, 0  # yaw, yaw_rate
            )
            
        except Exception as e:
            print(f"❌ Hız komutu hatası: {e}")
    
    def send_goto_command(self, lat: float, lon: float, alt: float):
        """
        GPS koordinatlarına git komutu gönderir.
        
        Args:
            lat: Hedef enlem
            lon: Hedef boylam
            alt: Hedef irtifa (metre, relative)
        """
        try:
            self.master.mav.set_position_target_global_int_send(
                0,  # time_boot_ms
                self.master.target_system,
                self.master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                0b0000111111111000,  # type_mask (sadece position kullan)
                int(lat * 1e7),
                int(lon * 1e7),
                alt,
                0, 0, 0,  # velocity
                0, 0, 0,  # acceleration
                0, 0  # yaw, yaw_rate
            )
            
            print(f"📍 Goto komutu gönderildi: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
            
        except Exception as e:
            print(f"❌ Goto komutu hatası: {e}")
    
    def close(self):
        """Bağlantıyı kapatır."""
        self.stop_telemetry_updates()
        if self.master:
            self.master.close()
        print("🔌 MAVLink bağlantısı kapatıldı")


# ============================================================================
# TEST FONKSİYONU
# ============================================================================
def test_communication_module():
    """Communication modülünü test eder."""
    print("=" * 60)
    print("İLETİŞİM MODÜLÜ TEST")
    print("=" * 60)
    
    try:
        # MAVLinkInterface oluştur
        mav = MAVLinkInterface()
        
        # Telemetri güncellemelerini başlat
        mav.start_telemetry_updates()
        
        print("\n📡 Telemetri verileri izleniyor...")
        print("   (Ctrl+C ile çıkabilirsiniz)\n")
        
        # Test döngüsü
        for i in range(20):
            telemetry = mav.get_telemetry()
            
            print(f"\n{'='*60}")
            print(f"Bağlantı: {'✅ Bağlı' if telemetry['connected'] else '❌ Bağlı Değil'}")
            print(f"Mod: {telemetry['mode']}")
            print(f"Armed: {'✅ Evet' if telemetry['armed'] else '❌ Hayır'}")
            print(f"GPS: {telemetry['gps']['lat']:.6f}, {telemetry['gps']['lon']:.6f}, "
                  f"{telemetry['gps']['alt']:.1f}m (Fix: {telemetry['gps']['fix']})")
            print(f"Heading: {telemetry['heading']:.1f}°")
            print(f"Altitude (Rel): {telemetry['altitude_rel']:.1f}m")
            print(f"Groundspeed: {telemetry['groundspeed']:.1f} m/s")
            print(f"Battery: {telemetry['battery']['voltage']:.1f}V, "
                  f"{telemetry['battery']['remaining']}%")
            
            time.sleep(1)
        
        # Temizlik
        mav.close()
        
        print("\n✅ Test tamamlandı")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test kullanıcı tarafından durduruldu")
        if 'mav' in locals():
            mav.close()
    
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_communication_module()
