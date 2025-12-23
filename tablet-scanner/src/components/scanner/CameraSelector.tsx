/**
 * Camera Selector Component
 *
 * 사용 가능한 카메라 목록을 표시하고 선택할 수 있는 컴포넌트
 */
import { useState, useEffect, useCallback } from 'react';
import { Camera, ChevronDown, RefreshCw, Check } from 'lucide-react';
import { cn } from '@/lib/cn';

interface CameraSelectorProps {
  /** 선택된 카메라 ID */
  selectedCameraId: string | null;
  /** 카메라 선택 핸들러 */
  onCameraSelect: (cameraId: string) => void;
  /** 컴팩트 모드 (아이콘만 표시) */
  compact?: boolean;
  /** 추가 클래스 */
  className?: string;
}

interface CameraInfo {
  deviceId: string;
  label: string;
  facingMode: 'user' | 'environment' | 'unknown';
}

const CAMERA_STORAGE_KEY = 'f2x_scanner_camera_id';

export const CameraSelector: React.FC<CameraSelectorProps> = ({
  selectedCameraId,
  onCameraSelect,
  compact = false,
  className,
}) => {
  const [cameras, setCameras] = useState<CameraInfo[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 카메라 목록 가져오기
  const fetchCameras = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // 권한 요청
      await navigator.mediaDevices.getUserMedia({ video: true });

      // 디바이스 목록 가져오기
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter((d) => d.kind === 'videoinput');

      const cameraList: CameraInfo[] = videoDevices.map((device, index) => {
        const label = device.label || `Camera ${index + 1}`;
        let facingMode: 'user' | 'environment' | 'unknown' = 'unknown';

        // 레이블에서 facing mode 추론
        const lowerLabel = label.toLowerCase();
        if (
          lowerLabel.includes('back') ||
          lowerLabel.includes('rear') ||
          lowerLabel.includes('environment')
        ) {
          facingMode = 'environment';
        } else if (
          lowerLabel.includes('front') ||
          lowerLabel.includes('user') ||
          lowerLabel.includes('face')
        ) {
          facingMode = 'user';
        }

        return {
          deviceId: device.deviceId,
          label,
          facingMode,
        };
      });

      setCameras(cameraList);

      // 저장된 카메라가 있으면 자동 선택
      const savedCameraId = localStorage.getItem(CAMERA_STORAGE_KEY);
      if (savedCameraId && cameraList.some((c) => c.deviceId === savedCameraId)) {
        if (!selectedCameraId) {
          onCameraSelect(savedCameraId);
        }
      } else if (cameraList.length > 0 && !selectedCameraId) {
        // 후면 카메라 우선 선택
        const backCamera = cameraList.find((c) => c.facingMode === 'environment');
        onCameraSelect(backCamera?.deviceId || cameraList[0].deviceId);
      }
    } catch (err) {
      console.error('Failed to fetch cameras:', err);
      setError('카메라 접근 권한이 필요합니다');
    } finally {
      setIsLoading(false);
    }
  }, [selectedCameraId, onCameraSelect]);

  // 초기 로드
  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  // 카메라 선택
  const handleSelect = (cameraId: string) => {
    localStorage.setItem(CAMERA_STORAGE_KEY, cameraId);
    onCameraSelect(cameraId);
    setIsOpen(false);
  };

  // 선택된 카메라 정보
  const selectedCamera = cameras.find((c) => c.deviceId === selectedCameraId);

  if (compact) {
    return (
      <div className={cn('relative', className)}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          disabled={isLoading || cameras.length === 0}
          className={cn(
            'p-2 rounded-lg transition-all',
            'bg-white/80 backdrop-blur-sm',
            'border border-neutral-200',
            'hover:bg-white hover:shadow-sm',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {isLoading ? (
            <RefreshCw className="w-5 h-5 text-neutral-500 animate-spin" />
          ) : (
            <Camera className="w-5 h-5 text-neutral-700" />
          )}
        </button>

        {isOpen && cameras.length > 0 && (
          <CameraDropdown
            cameras={cameras}
            selectedCameraId={selectedCameraId}
            onSelect={handleSelect}
            onClose={() => setIsOpen(false)}
          />
        )}
      </div>
    );
  }

  return (
    <div className={cn('relative', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading || cameras.length === 0}
        className={cn(
          'w-full flex items-center gap-3 p-3 rounded-xl',
          'bg-white border border-neutral-200',
          'hover:border-primary-300 hover:bg-primary-50/50',
          'transition-all duration-200',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          isOpen && 'border-primary-400 bg-primary-50/50'
        )}
      >
        <div className="p-2 bg-primary-100 rounded-lg">
          <Camera className="w-5 h-5 text-primary-600" />
        </div>

        <div className="flex-1 text-left">
          <div className="text-sm font-medium text-neutral-900">
            {isLoading
              ? '카메라 검색 중...'
              : selectedCamera?.label || '카메라를 선택하세요'}
          </div>
          {selectedCamera && (
            <div className="text-xs text-neutral-500">
              {selectedCamera.facingMode === 'environment'
                ? '후면 카메라'
                : selectedCamera.facingMode === 'user'
                ? '전면 카메라'
                : ''}
            </div>
          )}
        </div>

        <ChevronDown
          className={cn(
            'w-5 h-5 text-neutral-400 transition-transform',
            isOpen && 'transform rotate-180'
          )}
        />
      </button>

      {error && (
        <p className="mt-2 text-sm text-danger-500 flex items-center gap-1">
          <span>⚠️</span> {error}
        </p>
      )}

      {isOpen && cameras.length > 0 && (
        <CameraDropdown
          cameras={cameras}
          selectedCameraId={selectedCameraId}
          onSelect={handleSelect}
          onClose={() => setIsOpen(false)}
          fullWidth
        />
      )}
    </div>
  );
};

// 카메라 드롭다운 메뉴
interface CameraDropdownProps {
  cameras: CameraInfo[];
  selectedCameraId: string | null;
  onSelect: (cameraId: string) => void;
  onClose: () => void;
  fullWidth?: boolean;
}

const CameraDropdown: React.FC<CameraDropdownProps> = ({
  cameras,
  selectedCameraId,
  onSelect,
  onClose,
  fullWidth = false,
}) => {
  // 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.camera-dropdown')) {
        onClose();
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [onClose]);

  // 카메라 그룹화
  const backCameras = cameras.filter((c) => c.facingMode === 'environment');
  const frontCameras = cameras.filter((c) => c.facingMode === 'user');
  const otherCameras = cameras.filter((c) => c.facingMode === 'unknown');

  const renderCameraItem = (camera: CameraInfo) => (
    <button
      key={camera.deviceId}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(camera.deviceId);
      }}
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2.5 text-left',
        'hover:bg-primary-50 transition-colors',
        'rounded-lg',
        selectedCameraId === camera.deviceId && 'bg-primary-50'
      )}
    >
      <span className="text-lg">
        {camera.facingMode === 'environment'
          ? '📷'
          : camera.facingMode === 'user'
          ? '🤳'
          : '📹'}
      </span>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-neutral-800 truncate">
          {camera.label}
        </div>
      </div>
      {selectedCameraId === camera.deviceId && (
        <Check className="w-4 h-4 text-primary-500" />
      )}
    </button>
  );

  return (
    <div
      className={cn(
        'camera-dropdown absolute z-50 mt-2',
        'bg-white rounded-xl shadow-lg border border-neutral-200',
        'py-2 animate-scale-in origin-top',
        fullWidth ? 'left-0 right-0' : 'right-0 min-w-[240px]'
      )}
    >
      {backCameras.length > 0 && (
        <div>
          <div className="px-3 py-1.5 text-xs font-medium text-neutral-500 uppercase">
            후면 카메라
          </div>
          {backCameras.map(renderCameraItem)}
        </div>
      )}

      {frontCameras.length > 0 && (
        <div className={backCameras.length > 0 ? 'mt-2 pt-2 border-t border-neutral-100' : ''}>
          <div className="px-3 py-1.5 text-xs font-medium text-neutral-500 uppercase">
            전면 카메라
          </div>
          {frontCameras.map(renderCameraItem)}
        </div>
      )}

      {otherCameras.length > 0 && (
        <div
          className={
            backCameras.length > 0 || frontCameras.length > 0
              ? 'mt-2 pt-2 border-t border-neutral-100'
              : ''
          }
        >
          <div className="px-3 py-1.5 text-xs font-medium text-neutral-500 uppercase">
            기타 카메라
          </div>
          {otherCameras.map(renderCameraItem)}
        </div>
      )}
    </div>
  );
};

export default CameraSelector;
