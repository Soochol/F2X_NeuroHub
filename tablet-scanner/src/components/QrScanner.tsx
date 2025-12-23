/**
 * Enhanced QR Scanner Component
 *
 * 개선된 기능:
 * - 카메라 선택 UI
 * - 애니메이션 오버레이
 * - 스캔 성공/실패 피드백
 * - 향상된 UX
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { Html5Qrcode, Html5QrcodeScannerState } from 'html5-qrcode';
import { Camera, AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/cn';
import { ScannerOverlay } from './scanner/ScannerOverlay';
import { CameraSelector } from './scanner/CameraSelector';

type ScanStatus = 'idle' | 'scanning' | 'success' | 'error' | 'processing';

interface QrScannerProps {
  onScan: (decodedText: string) => void;
  onError?: (error: string) => void;
  width?: number;
  height?: number;
  fps?: number;
  qrbox?: number;
  aspectRatio?: number;
  disabled?: boolean;
  className?: string;
  /** 카메라 선택 UI 표시 */
  showCameraSelector?: boolean;
  /** 성공 시 자동 일시정지 시간 (ms) */
  successPauseDuration?: number;
}

export const QrScanner: React.FC<QrScannerProps> = ({
  onScan,
  onError,
  width = 300,
  height = 300,
  fps = 10,
  qrbox = 220,
  aspectRatio = 1,
  disabled = false,
  className,
  showCameraSelector = true,
  successPauseDuration = 1500,
}) => {
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanStatus, setScanStatus] = useState<ScanStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [lastScanned, setLastScanned] = useState<string>('');
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null);
  const lastScanTime = useRef<number>(0);

  // Debounce scan results
  const handleScanSuccess = useCallback(
    (decodedText: string) => {
      const now = Date.now();
      // Prevent same code within 2 seconds
      if (decodedText === lastScanned && now - lastScanTime.current < 2000) {
        return;
      }

      lastScanTime.current = now;
      setLastScanned(decodedText);

      // Visual feedback
      setScanStatus('success');

      // Vibrate for feedback
      if (navigator.vibrate) {
        navigator.vibrate([50, 30, 50]);
      }

      // Call parent handler
      onScan(decodedText);

      // Reset status after delay
      setTimeout(() => {
        setScanStatus('scanning');
      }, successPauseDuration);
    },
    [lastScanned, onScan, successPauseDuration]
  );

  // Start scanner with specific camera
  const startScanner = useCallback(
    async (cameraId?: string) => {
      if (!containerRef.current || disabled) return;

      try {
        setError(null);
        setScanStatus('idle');

        // Stop existing scanner
        if (scannerRef.current) {
          try {
            const state = scannerRef.current.getState();
            if (state === Html5QrcodeScannerState.SCANNING) {
              await scannerRef.current.stop();
            }
            await scannerRef.current.clear();
          } catch {
            // Ignore
          }
        }

        // Create new scanner instance
        const scanner = new Html5Qrcode('qr-reader');
        scannerRef.current = scanner;

        // Determine camera to use
        let targetCameraId = cameraId || selectedCameraId;

        if (!targetCameraId) {
          const cameras = await Html5Qrcode.getCameras();
          if (cameras.length === 0) {
            throw new Error('카메라를 찾을 수 없습니다');
          }

          // Prefer back camera
          const backCamera = cameras.find(
            (camera) =>
              camera.label.toLowerCase().includes('back') ||
              camera.label.toLowerCase().includes('rear') ||
              camera.label.toLowerCase().includes('환경')
          );

          targetCameraId = backCamera?.id || cameras[0].id;
          setSelectedCameraId(targetCameraId);
        }

        // Start scanning
        await scanner.start(
          targetCameraId,
          {
            fps,
            qrbox: { width: qrbox, height: qrbox },
            aspectRatio,
          },
          handleScanSuccess,
          () => {} // Ignore failures
        );

        setIsScanning(true);
        setScanStatus('scanning');
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : '스캐너 시작 실패';
        setError(errorMessage);
        setScanStatus('error');
        onError?.(errorMessage);
      }
    },
    [
      disabled,
      selectedCameraId,
      fps,
      qrbox,
      aspectRatio,
      handleScanSuccess,
      onError,
    ]
  );

  // Stop scanner
  const stopScanner = useCallback(async () => {
    if (scannerRef.current) {
      try {
        const state = scannerRef.current.getState();
        if (state === Html5QrcodeScannerState.SCANNING) {
          await scannerRef.current.stop();
        }
        await scannerRef.current.clear();
      } catch {
        // Ignore
      }
      scannerRef.current = null;
      setIsScanning(false);
      setScanStatus('idle');
    }
  }, []);

  // Handle camera change
  const handleCameraChange = useCallback(
    (cameraId: string) => {
      setSelectedCameraId(cameraId);
      if (isScanning) {
        startScanner(cameraId);
      }
    },
    [isScanning, startScanner]
  );

  // Initialize on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      startScanner();
    }, 100);

    return () => {
      clearTimeout(timer);
      stopScanner();
    };
  }, []);

  // Handle disabled state
  useEffect(() => {
    if (disabled && isScanning) {
      stopScanner();
    } else if (!disabled && !isScanning && !error) {
      startScanner();
    }
  }, [disabled]);

  const isActive = isScanning && !disabled;

  return (
    <div className={cn('flex flex-col items-center gap-3', className)}>
      {/* Camera selector (if enabled) */}
      {showCameraSelector && (
        <div className="w-full flex justify-end mb-2">
          <CameraSelector
            selectedCameraId={selectedCameraId}
            onCameraSelect={handleCameraChange}
            compact
          />
        </div>
      )}

      {/* Scanner container */}
      <div
        ref={containerRef}
        className="rounded-2xl overflow-hidden bg-neutral-900 relative shadow-lg"
        style={{ width, height }}
      >
        <div id="qr-reader" className="w-full h-full" />

        {/* Enhanced overlay */}
        <ScannerOverlay
          status={scanStatus}
          isActive={isActive}
          successMessage="스캔 완료!"
          errorMessage="인식 실패"
        />

        {/* Disabled overlay */}
        {disabled && (
          <div
            className={cn(
              'absolute inset-0 bg-black/80 backdrop-blur-sm',
              'flex flex-col items-center justify-center gap-2',
              'text-white animate-fade-in'
            )}
          >
            <Camera className="w-8 h-8 opacity-50" />
            <span className="text-sm">스캐너 일시정지</span>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div
          className={cn(
            'flex items-center gap-2',
            'text-sm text-danger-600',
            'px-4 py-2',
            'bg-danger-50 rounded-lg',
            'border border-danger-200',
            'animate-error-shake'
          )}
        >
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
          <button
            onClick={() => startScanner()}
            className="ml-2 p-1 hover:bg-danger-100 rounded-full transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Status indicator */}
      <div
        className={cn(
          'flex items-center gap-2 px-4 py-2 rounded-full',
          'transition-all duration-300',
          isActive
            ? 'bg-success-50 text-success-700'
            : error
            ? 'bg-danger-50 text-danger-600'
            : 'bg-neutral-100 text-neutral-500'
        )}
      >
        <span
          className={cn(
            'w-2 h-2 rounded-full transition-all',
            isActive
              ? 'bg-success-500 animate-pulse'
              : error
              ? 'bg-danger-500'
              : 'bg-neutral-400'
          )}
        />
        <Camera className="w-4 h-4" />
        <span className="text-sm font-medium">
          {isActive
            ? 'QR 코드를 스캔하세요'
            : error
            ? '스캐너 오류'
            : '스캐너 준비 중...'}
        </span>
      </div>

      <style>{`
        #qr-reader video {
          border-radius: 16px;
          object-fit: cover;
        }

        #qr-reader__scan_region {
          display: none !important;
        }

        #qr-reader__dashboard {
          display: none !important;
        }

        #qr-reader img {
          display: none !important;
        }
      `}</style>
    </div>
  );
};

export default QrScanner;
