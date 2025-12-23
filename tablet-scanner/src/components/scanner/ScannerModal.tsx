/**
 * Scanner Modal Component
 *
 * 전체화면 투명 오버레이 스캐너
 * - 반투명 배경
 * - 중앙 스캔 영역
 * - 애니메이션 효과
 * - 스캔 성공 시 자동 닫힘
 */
import { useEffect, useState, useRef, useCallback } from 'react';
import { X, Zap, Camera } from 'lucide-react';
import { Html5Qrcode, Html5QrcodeScannerState } from 'html5-qrcode';
import { cn } from '@/lib/cn';
import { ScannerOverlay } from './ScannerOverlay';

type ScanStatus = 'idle' | 'scanning' | 'success' | 'error' | 'processing';

interface ScannerModalProps {
  /** 모달 열림 상태 */
  isOpen: boolean;
  /** 닫기 콜백 */
  onClose: () => void;
  /** 스캔 성공 콜백 */
  onScan: (decodedText: string) => void;
  /** 스캔 에러 콜백 */
  onError?: (error: string) => void;
  /** 스캔 성공 후 자동 닫힘 지연 (ms) */
  autoCloseDelay?: number;
  /** 타이틀 */
  title?: string;
}

export const ScannerModal: React.FC<ScannerModalProps> = ({
  isOpen,
  onClose,
  onScan,
  onError,
  autoCloseDelay = 500,
  title = 'QR 코드 스캔',
}) => {
  const [scanStatus, setScanStatus] = useState<ScanStatus>('idle');
  const [isInitializing, setIsInitializing] = useState(false);

  // Use refs to avoid stale closures
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const lastScannedRef = useRef<string>('');
  const isCleaningUpRef = useRef(false);
  const onScanRef = useRef(onScan);
  const onCloseRef = useRef(onClose);

  // Keep refs updated
  useEffect(() => {
    onScanRef.current = onScan;
    onCloseRef.current = onClose;
  }, [onScan, onClose]);

  // Cleanup function
  const cleanupScanner = useCallback(async () => {
    if (isCleaningUpRef.current) return;
    isCleaningUpRef.current = true;

    const scanner = scannerRef.current;
    if (scanner) {
      try {
        const state = scanner.getState();
        if (state === Html5QrcodeScannerState.SCANNING) {
          await scanner.stop();
        }
      } catch (err) {
        console.warn('Scanner stop warning:', err);
      }

      try {
        scanner.clear();
      } catch (err) {
        console.warn('Scanner clear warning:', err);
      }

      scannerRef.current = null;
    }

    isCleaningUpRef.current = false;
  }, []);

  // Handle successful scan
  const handleScanSuccess = useCallback((decodedText: string) => {
    // Prevent duplicate scans
    if (decodedText === lastScannedRef.current) return;

    lastScannedRef.current = decodedText;
    setScanStatus('success');

    // Vibrate for feedback
    if (navigator.vibrate) {
      navigator.vibrate([50, 30, 50]);
    }

    // Call parent handler
    onScanRef.current(decodedText);

    // Auto close after delay
    setTimeout(() => {
      onCloseRef.current();
    }, autoCloseDelay);
  }, [autoCloseDelay]);

  // Initialize scanner when modal opens
  useEffect(() => {
    if (!isOpen) {
      // Cleanup when closing
      cleanupScanner();
      setScanStatus('idle');
      lastScannedRef.current = '';
      return;
    }

    // Start scanner
    const initScanner = async () => {
      // Wait a bit for DOM to be ready
      await new Promise(resolve => setTimeout(resolve, 100));

      const element = document.getElementById('scanner-modal-reader');
      if (!element) {
        console.error('Scanner element not found');
        setScanStatus('error');
        onError?.('스캐너 요소를 찾을 수 없습니다');
        return;
      }

      setIsInitializing(true);
      setScanStatus('scanning');

      try {
        const html5Qrcode = new Html5Qrcode('scanner-modal-reader');
        scannerRef.current = html5Qrcode;

        const cameras = await Html5Qrcode.getCameras();
        if (cameras.length === 0) {
          throw new Error('카메라를 찾을 수 없습니다');
        }

        // Prefer back camera
        const backCamera = cameras.find(
          (c) =>
            c.label.toLowerCase().includes('back') ||
            c.label.toLowerCase().includes('rear') ||
            c.label.toLowerCase().includes('환경')
        );
        const cameraId = backCamera?.id || cameras[0].id;

        await html5Qrcode.start(
          cameraId,
          {
            fps: 10,
            qrbox: (viewfinderWidth: number, viewfinderHeight: number) => {
              const minEdge = Math.min(viewfinderWidth, viewfinderHeight);
              const size = Math.floor(minEdge * 0.8);
              return { width: size, height: size };
            },
            aspectRatio: 1,
          },
          handleScanSuccess,
          () => { } // Ignore scan failures (no QR in frame)
        );
      } catch (err) {
        console.error('Scanner init error:', err);
        setScanStatus('error');
        onError?.(err instanceof Error ? err.message : '스캐너 초기화 실패');
      } finally {
        setIsInitializing(false);
      }
    };

    initScanner();

    // Cleanup on unmount
    return () => {
      cleanupScanner();
    };
  }, [isOpen, cleanupScanner, handleScanSuccess, onError]);

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className={cn(
        'fixed inset-0 z-50',
        'flex items-center justify-center',
        'bg-black/80 backdrop-blur-sm',
        'animate-fade-in'
      )}
      onClick={handleBackdropClick}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        className={cn(
          'absolute top-4 right-4 z-10',
          'p-3 rounded-full',
          'bg-white/20 hover:bg-white/30',
          'text-white transition-colors'
        )}
      >
        <X className="w-6 h-6" />
      </button>

      {/* Title */}
      <div className="absolute top-4 left-4 right-16">
        <h2 className="text-white text-lg font-semibold flex items-center gap-2">
          <Camera className="w-5 h-5" />
          {title}
        </h2>
        <p className="text-white/70 text-sm mt-1">
          QR 코드를 프레임 안에 위치시키세요
        </p>
      </div>

      {/* Scanner container */}
      <div
        className={cn(
          'relative w-[85vw] h-[85vw] max-w-[600px] max-h-[600px]',
          'rounded-3xl overflow-hidden',
          'shadow-2xl border-2 border-white/10',
          scanStatus === 'success' && 'ring-8 ring-success-500',
          scanStatus === 'error' && 'ring-8 ring-danger-500'
        )}
      >
        {/* Camera view */}
        <div
          id="scanner-modal-reader"
          className="w-full h-full bg-neutral-900"
        />

        {/* Scanner overlay */}
        <ScannerOverlay
          status={scanStatus}
          isActive={scanStatus === 'scanning' || scanStatus === 'idle'}
        />

        {/* Loading indicator */}
        {isInitializing && (
          <div className="absolute inset-0 flex items-center justify-center bg-neutral-900/80">
            <div className="flex flex-col items-center gap-3">
              <div className="w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-white text-sm">카메라 시작 중...</span>
            </div>
          </div>
        )}

        {/* Success indicator */}
        {scanStatus === 'success' && (
          <div className="absolute inset-0 flex items-center justify-center bg-success-500/20 animate-success-pulse">
            <div className="bg-success-500 rounded-full p-4">
              <Zap className="w-8 h-8 text-white" />
            </div>
          </div>
        )}
      </div>

      {/* Bottom hint */}
      <div className="absolute bottom-8 left-0 right-0 text-center">
        <p className="text-white/60 text-sm">
          탭하여 닫기 또는 ESC 키
        </p>
      </div>
    </div>
  );
};

export default ScannerModal;
