"""
Otonom İHA Engelden Kaçış ve Karar Destek Sistemi
Görüntü İşleme Modülü (Vision Module)

Bu modül, YOLOv11 kullanarak gerçek zamanlı nesne tespiti yapar.
NVIDIA Jetson Nano GPU'sunu (CUDA) verimli kullanmak için TensorRT
optimizasyonu sağlar.

Özellikler:
- YOLOv11 model yükleme ve inference
- TensorRT optimizasyonu (Jetson Nano için)
- OpenCV kamera arayüzü (CSI ve USB desteği)
- Bounding box çıkarma ve engel pozisyon hesaplama
- Thread-safe frame erişimi

Author: Computer Engineering
Platform: NVIDIA Jetson Nano
"""

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from threading import Lock, Thread
from typing import List, Tuple, Optional, Dict
import time
import os

from config import CameraConfig, YOLOConfig, SystemConfig


# ============================================================================
# YOLO DETECTOR CLASS
# ============================================================================
class YOLODetector:
    """
    YOLOv11 tabanlı nesne tespit sınıfı.
    TensorRT optimizasyonu ile Jetson Nano GPU'sunda hızlandırılmış inference.
    """
    
    def __init__(self, model_path: str = None, use_tensorrt: bool = None):
        """
        YOLODetector başlatıcı.
        
        Args:
            model_path: YOLO model dosya yolu (.pt formatı)
            use_tensorrt: TensorRT optimizasyonu kullan (None ise config'den alınır)
        """
        self.model_path = model_path or YOLOConfig.MODEL_PATH
        self.use_tensorrt = use_tensorrt if use_tensorrt is not None else YOLOConfig.USE_TENSORRT
        self.model = None
        self.device = f"cuda:{YOLOConfig.DEVICE}" if torch.cuda.is_available() else "cpu"
        
        # Model yükleme
        self._load_model()
        
        print(f"✅ YOLODetector başlatıldı (Device: {self.device})")
    
    def _load_model(self):
        """YOLO modelini yükler ve gerekirse TensorRT'ye dönüştürür."""
        try:
            # Model dosyası kontrolü
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model dosyası bulunamadı: {self.model_path}")
            
            print(f"📦 YOLO modeli yükleniyor: {self.model_path}")
            
            # YOLO modelini yükle
            self.model = YOLO(self.model_path)
            
            # TensorRT optimizasyonu
            if self.use_tensorrt and torch.cuda.is_available():
                print("🚀 TensorRT optimizasyonu uygulanıyor...")
                try:
                    # TensorRT export (ilk çalıştırmada engine oluşturur)
                    engine_path = YOLOConfig.TENSORRT_ENGINE_PATH
                    
                    if not os.path.exists(engine_path):
                        print("   TensorRT engine oluşturuluyor (bu işlem birkaç dakika sürebilir)...")
                        self.model.export(format='engine', device=YOLOConfig.DEVICE)
                        print(f"   ✅ TensorRT engine kaydedildi: {engine_path}")
                    else:
                        print(f"   ✅ Mevcut TensorRT engine kullanılıyor: {engine_path}")
                        # Engine'i yükle
                        self.model = YOLO(engine_path)
                
                except Exception as e:
                    print(f"   ⚠️  TensorRT optimizasyonu başarısız, standart model kullanılıyor: {e}")
            
            # Modeli GPU'ya taşı
            if torch.cuda.is_available():
                self.model.to(self.device)
            
            print("✅ Model yükleme tamamlandı")
            
        except Exception as e:
            raise RuntimeError(f"Model yükleme hatası: {e}")
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Verilen frame'de nesne tespiti yapar.
        
        Args:
            frame: BGR formatında OpenCV görüntüsü
        
        Returns:
            Tespit edilen nesnelerin listesi. Her nesne bir dict:
            {
                'bbox': [x1, y1, x2, y2],  # Bounding box koordinatları
                'confidence': float,        # Güven skoru (0-1)
                'class_id': int,           # Sınıf ID
                'class_name': str,         # Sınıf adı
                'center': (cx, cy),        # Merkez koordinatları
                'distance': float          # Tahmini mesafe (piksel bazlı)
            }
        """
        if self.model is None:
            return []
        
        try:
            # YOLO inference
            results = self.model.predict(
                source=frame,
                conf=YOLOConfig.CONFIDENCE_THRESHOLD,
                iou=YOLOConfig.NMS_THRESHOLD,
                max_det=YOLOConfig.MAX_DETECTIONS,
                classes=YOLOConfig.DETECT_CLASSES,
                verbose=False,
                device=self.device
            )
            
            # Sonuçları işle
            detections = []
            
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                
                for i in range(len(boxes)):
                    # Bounding box koordinatları (xyxy formatı)
                    bbox = boxes.xyxy[i].cpu().numpy()
                    x1, y1, x2, y2 = map(int, bbox)
                    
                    # Güven skoru
                    confidence = float(boxes.conf[i].cpu().numpy())
                    
                    # Sınıf bilgisi
                    class_id = int(boxes.cls[i].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    # Merkez koordinatları
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    
                    # Tahmini mesafe (bounding box yüksekliğine göre basit hesaplama)
                    # Gerçek uygulamada kamera kalibrasyonu gerekir
                    bbox_height = y2 - y1
                    estimated_distance = self._estimate_distance(bbox_height)
                    
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'class_id': class_id,
                        'class_name': class_name,
                        'center': (cx, cy),
                        'distance': estimated_distance
                    })
            
            return detections
        
        except Exception as e:
            print(f"⚠️  Tespit hatası: {e}")
            return []
    
    def _estimate_distance(self, bbox_height: int) -> float:
        """
        Bounding box yüksekliğinden tahmini mesafe hesaplar.
        
        Not: Bu basit bir yaklaşımdır. Gerçek uygulamada kamera kalibrasyonu
        ve nesne boyutu bilgisi kullanılmalıdır.
        
        Args:
            bbox_height: Bounding box yüksekliği (piksel)
        
        Returns:
            Tahmini mesafe (metre)
        """
        # Basit ters orantı formülü: mesafe ~ 1 / bbox_height
        # Kalibrasyon sabiti (örnek değer, gerçek değer kamera ve nesneye göre değişir)
        CALIBRATION_CONSTANT = 5000.0
        
        if bbox_height > 0:
            distance = CALIBRATION_CONSTANT / bbox_height
            return max(0.5, min(distance, 50.0))  # 0.5m - 50m arası sınırla
        else:
            return 50.0  # Varsayılan uzak mesafe


# ============================================================================
# VISION PROCESSOR CLASS
# ============================================================================
class VisionProcessor:
    """
    Kamera arayüzü ve görüntü işleme pipeline'ı.
    Thread-safe frame erişimi ve sürekli tespit sağlar.
    """
    
    def __init__(self, camera_source=None):
        """
        VisionProcessor başlatıcı.
        
        Args:
            camera_source: Kamera kaynağı (None ise config'den alınır)
        """
        self.camera_source = camera_source if camera_source is not None else CameraConfig.CAMERA_SOURCE
        self.cap = None
        self.detector = None
        
        # Thread-safe değişkenler
        self.current_frame = None
        self.current_detections = []
        self.frame_lock = Lock()
        
        # İşlem durumu
        self.is_running = False
        self.processing_thread = None
        
        # Performans metrikleri
        self.fps = 0.0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        # Başlatma
        self._initialize_camera()
        self._initialize_detector()
        
        print("✅ VisionProcessor başlatıldı")
    
    def _initialize_camera(self):
        """Kamera bağlantısını başlatır."""
        try:
            # CSI kamera kontrolü
            if isinstance(self.camera_source, str) and 'nvarguscamerasrc' in self.camera_source:
                print("📷 CSI kamera başlatılıyor...")
                self.cap = cv2.VideoCapture(CameraConfig.CSI_PIPELINE, cv2.CAP_GSTREAMER)
            else:
                print(f"📷 USB kamera başlatılıyor (ID: {self.camera_source})...")
                self.cap = cv2.VideoCapture(self.camera_source)
                
                # Kamera ayarları
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CameraConfig.FRAME_WIDTH)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CameraConfig.FRAME_HEIGHT)
                self.cap.set(cv2.CAP_PROP_FPS, CameraConfig.FPS)
            
            if not self.cap.isOpened():
                raise RuntimeError("Kamera açılamadı")
            
            print("✅ Kamera başarıyla başlatıldı")
            
        except Exception as e:
            raise RuntimeError(f"Kamera başlatma hatası: {e}")
    
    def _initialize_detector(self):
        """YOLO detector'ı başlatır."""
        try:
            if not SystemConfig.SIMULATION_MODE:
                self.detector = YOLODetector()
            else:
                print("⚠️  Simülasyon modu: YOLO detector devre dışı")
                self.detector = None
        except Exception as e:
            print(f"⚠️  Detector başlatma hatası: {e}")
            self.detector = None
    
    def start(self):
        """Görüntü işleme thread'ini başlatır."""
        if self.is_running:
            print("⚠️  VisionProcessor zaten çalışıyor")
            return
        
        self.is_running = True
        self.processing_thread = Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        print("▶️  Görüntü işleme başlatıldı")
    
    def stop(self):
        """Görüntü işleme thread'ini durdurur."""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
        print("⏹️  Görüntü işleme durduruldu")
    
    def _processing_loop(self):
        """Ana görüntü işleme döngüsü (thread'de çalışır)."""
        while self.is_running:
            try:
                # Frame yakala
                ret, frame = self.cap.read()
                if not ret:
                    print("⚠️  Frame okunamadı")
                    time.sleep(0.1)
                    continue
                
                # Tespit yap
                detections = []
                if self.detector is not None:
                    detections = self.detector.detect(frame)
                
                # Thread-safe güncelleme
                with self.frame_lock:
                    self.current_frame = frame.copy()
                    self.current_detections = detections
                
                # FPS hesapla
                self._update_fps()
                
            except Exception as e:
                print(f"⚠️  İşleme döngüsü hatası: {e}")
                time.sleep(0.1)
    
    def _update_fps(self):
        """FPS metriğini günceller."""
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_fps_time
        
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def get_frame_and_detections(self) -> Tuple[Optional[np.ndarray], List[Dict]]:
        """
        Thread-safe şekilde güncel frame ve tespitleri döndürür.
        
        Returns:
            (frame, detections) tuple
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy(), self.current_detections.copy()
            else:
                return None, []
    
    def get_fps(self) -> float:
        """Güncel FPS değerini döndürür."""
        return self.fps
    
    def release(self):
        """Kaynakları serbest bırakır."""
        self.stop()
        if self.cap:
            self.cap.release()
        print("🔌 VisionProcessor kaynakları serbest bırakıldı")


# ============================================================================
# TEST FONKSİYONU
# ============================================================================
def test_vision_module():
    """Vision modülünü test eder."""
    print("=" * 60)
    print("VİSİON MODÜLÜ TEST")
    print("=" * 60)
    
    try:
        # VisionProcessor oluştur
        processor = VisionProcessor()
        processor.start()
        
        print("\n📹 Kamera görüntüsü test ediliyor...")
        print("   (ESC tuşuna basarak çıkabilirsiniz)\n")
        
        # Test döngüsü
        while True:
            frame, detections = processor.get_frame_and_detections()
            
            if frame is not None:
                # Tespitleri çiz
                display_frame = frame.copy()
                
                for det in detections:
                    x1, y1, x2, y2 = det['bbox']
                    label = f"{det['class_name']} {det['confidence']:.2f} ({det['distance']:.1f}m)"
                    
                    # Bounding box
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Label
                    cv2.putText(display_frame, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # FPS göster
                fps_text = f"FPS: {processor.get_fps():.1f} | Detections: {len(detections)}"
                cv2.putText(display_frame, fps_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Göster
                cv2.imshow("Vision Test", display_frame)
                
                # ESC tuşu kontrolü
                if cv2.waitKey(1) & 0xFF == 27:
                    break
        
        # Temizlik
        cv2.destroyAllWindows()
        processor.release()
        
        print("\n✅ Test tamamlandı")
        
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_vision_module()
