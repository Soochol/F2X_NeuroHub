/**
 * Scanner Overlay Component
 *
 * QR 스캐너 위에 표시되는 애니메이션 오버레이
 * - 코너 마커
 * - 스캔 라인 애니메이션
 * - 상태 표시
 */
import { useState, useEffect } from 'react';
import { Scan, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/cn';

type ScannerStatus = 'idle' | 'scanning' | 'success' | 'error' | 'processing';

interface ScannerOverlayProps {
  /** 스캐너 상태 */
  status?: ScannerStatus;
  /** 스캐너 활성화 여부 */
  isActive?: boolean;
  /** 성공 시 표시할 메시지 */
  successMessage?: string;
  /** 에러 시 표시할 메시지 */
  errorMessage?: string;
  /** 추가 클래스 */
  className?: string;
}

export const ScannerOverlay: React.FC<ScannerOverlayProps> = ({
  status = 'idle',
  isActive = true,
  successMessage = '스캔 성공!',
  errorMessage = '인식 실패',
  className,
}) => {
  const [showFlash, setShowFlash] = useState(false);

  // 성공/에러 시 플래시 효과
  useEffect(() => {
    if (status === 'success' || status === 'error') {
      setShowFlash(true);
      const timer = setTimeout(() => setShowFlash(false), 300);
      return () => clearTimeout(timer);
    }
  }, [status]);

  const getStatusBgColor = () => {
    switch (status) {
      case 'success':
        return 'bg-success-500/20';
      case 'error':
        return 'bg-danger-500/20';
      default:
        return 'bg-transparent';
    }
  };

  return (
    <div
      className={cn(
        'absolute inset-0 pointer-events-none',
        'transition-all duration-200',
        showFlash && getStatusBgColor(),
        className
      )}
    >
      {/* Corner Markers */}
      <CornerMarkers status={status} isActive={isActive} />

      {/* Scan Line (only when active and scanning) */}
      {isActive && (status === 'idle' || status === 'scanning') && (
        <ScanLine />
      )}

      {/* Center Status Indicator */}
      <StatusIndicator
        status={status}
        successMessage={successMessage}
        errorMessage={errorMessage}
      />

      {/* Bottom Status Text */}
      <BottomStatusText status={status} isActive={isActive} />
    </div>
  );
};

// 코너 마커 컴포넌트
interface CornerMarkersProps {
  status: ScannerStatus;
  isActive: boolean;
}

const CornerMarkers: React.FC<CornerMarkersProps> = ({ status, isActive }) => {
  const getColor = () => {
    switch (status) {
      case 'success':
        return 'border-success-500';
      case 'error':
        return 'border-danger-500';
      case 'processing':
        return 'border-warning-500';
      default:
        return 'border-primary-500';
    }
  };

  const cornerClass = cn(
    'absolute w-16 h-16 transition-all duration-300',
    getColor(),
    isActive && status === 'scanning' && 'animate-pulse'
  );

  return (
    <>
      {/* Top Left */}
      <div
        className={cn(
          cornerClass,
          'top-6 left-6',
          'border-t-6 border-l-6 rounded-tl-3xl'
        )}
      />

      {/* Top Right */}
      <div
        className={cn(
          cornerClass,
          'top-6 right-6',
          'border-t-6 border-r-6 rounded-tr-3xl'
        )}
      />

      {/* Bottom Left */}
      <div
        className={cn(
          cornerClass,
          'bottom-6 left-6',
          'border-b-6 border-l-6 rounded-bl-3xl'
        )}
      />

      {/* Bottom Right */}
      <div
        className={cn(
          cornerClass,
          'bottom-6 right-6',
          'border-b-6 border-r-6 rounded-br-3xl'
        )}
      />
    </>
  );
};

// 스캔 라인 애니메이션
const ScanLine: React.FC = () => {
  return (
    <div className="absolute inset-x-0 inset-y-12 overflow-hidden pointer-events-none">
      <div className="scanner-line" />
    </div>
  );
};

// 중앙 상태 인디케이터
interface StatusIndicatorProps {
  status: ScannerStatus;
  successMessage: string;
  errorMessage: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  successMessage,
  errorMessage,
}) => {
  if (status === 'idle' || status === 'scanning') {
    return null;
  }

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div
        className={cn(
          'flex flex-col items-center gap-2 p-4 rounded-2xl',
          'backdrop-blur-sm animate-scale-in',
          status === 'success' && 'bg-success-500/90',
          status === 'error' && 'bg-danger-500/90',
          status === 'processing' && 'bg-white/90 border border-neutral-200'
        )}
      >
        {status === 'success' && (
          <>
            <CheckCircle className="w-12 h-12 text-white animate-bounce-in" />
            <span className="text-white font-medium">{successMessage}</span>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle className="w-12 h-12 text-white animate-error-shake" />
            <span className="text-white font-medium">{errorMessage}</span>
          </>
        )}

        {status === 'processing' && (
          <>
            <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
            <span className="text-neutral-700 font-medium">처리 중...</span>
          </>
        )}
      </div>
    </div>
  );
};

// 하단 상태 텍스트
interface BottomStatusTextProps {
  status: ScannerStatus;
  isActive: boolean;
}

const BottomStatusText: React.FC<BottomStatusTextProps> = ({
  status,
  isActive,
}) => {
  if (status === 'success' || status === 'error' || status === 'processing') {
    return null;
  }

  return (
    <div className="absolute bottom-8 left-0 right-0 flex justify-center">
      <div
        className={cn(
          'flex items-center gap-2 px-4 py-2 rounded-full',
          'bg-black/60 backdrop-blur-sm',
          'text-white text-sm font-medium',
          'transition-all duration-200'
        )}
      >
        {isActive ? (
          <>
            <Scan className="w-4 h-4" />
            <span>QR 코드를 프레임 안에 위치시키세요</span>
          </>
        ) : (
          <span>스캐너가 비활성화되었습니다</span>
        )}
      </div>
    </div>
  );
};

/**
 * 간단한 스캔 프레임 (코너만)
 */
interface SimpleScanFrameProps {
  size?: number;
  color?: string;
  className?: string;
}

export const SimpleScanFrame: React.FC<SimpleScanFrameProps> = ({
  size = 200,
  color = 'border-primary-500',
  className,
}) => {
  return (
    <div
      className={cn('relative', className)}
      style={{ width: size, height: size }}
    >
      {/* Top Left */}
      <div
        className={cn(
          'absolute top-0 left-0 w-8 h-8',
          'border-t-3 border-l-3 rounded-tl-lg',
          color
        )}
      />
      {/* Top Right */}
      <div
        className={cn(
          'absolute top-0 right-0 w-8 h-8',
          'border-t-3 border-r-3 rounded-tr-lg',
          color
        )}
      />
      {/* Bottom Left */}
      <div
        className={cn(
          'absolute bottom-0 left-0 w-8 h-8',
          'border-b-3 border-l-3 rounded-bl-lg',
          color
        )}
      />
      {/* Bottom Right */}
      <div
        className={cn(
          'absolute bottom-0 right-0 w-8 h-8',
          'border-b-3 border-r-3 rounded-br-lg',
          color
        )}
      />
    </div>
  );
};

export default ScannerOverlay;
