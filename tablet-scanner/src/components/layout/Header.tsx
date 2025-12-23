/**
 * Header Component
 *
 * App header with title, network status, and controls
 */
import { Volume2, VolumeX, Calendar, LogOut } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface HeaderProps {
  title: string;
  subtitle?: string;
  isOnline: boolean;
  soundEnabled: boolean;
  onToggleSound: () => void;
  queueCount?: number;
  showDate?: boolean;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  isOnline,
  soundEnabled,
  onToggleSound,
  queueCount = 0,
  showDate = true,
  onLogout,
}) => {
  return (
    <header className="flex justify-between items-center mb-4">
      {/* Left side - Title and status */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-neutral-800 truncate">
            {title}
          </h1>
          {/* Network status indicator */}
          <span
            className={cn(
              'w-2.5 h-2.5 rounded-full flex-shrink-0',
              isOnline ? 'bg-success-500' : 'bg-danger-500'
            )}
            title={isOnline ? '온라인' : '오프라인'}
          />
        </div>
        {subtitle && (
          <p className="text-sm text-neutral-500 mt-0.5 truncate">
            {subtitle}
            {queueCount > 0 && (
              <span className="text-warning-600 ml-2 font-medium">
                (대기: {queueCount}건)
              </span>
            )}
          </p>
        )}
      </div>

      {/* Right side - Controls */}
      <div className="flex items-center gap-2 ml-4">
        {/* Sound toggle */}
        <button
          onClick={onToggleSound}
          className={cn(
            'p-2 rounded-lg border transition-colors',
            soundEnabled
              ? 'bg-primary-50 border-primary-200 text-primary-600'
              : 'bg-neutral-100 border-neutral-200 text-neutral-500'
          )}
          title={soundEnabled ? '소리 끄기' : '소리 켜기'}
        >
          {soundEnabled ? (
            <Volume2 className="w-5 h-5" />
          ) : (
            <VolumeX className="w-5 h-5" />
          )}
        </button>

        {/* Date display */}
        {showDate && (
          <div className="hidden sm:flex items-center gap-1.5 text-sm text-neutral-500">
            <Calendar className="w-4 h-4" />
            <span>{new Date().toLocaleDateString('ko-KR')}</span>
          </div>
        )}

        {/* Logout button */}
        {onLogout && (
          <button
            onClick={onLogout}
            className={cn(
              'p-2 rounded-lg border transition-colors',
              'bg-neutral-100 border-neutral-200 text-neutral-500',
              'hover:bg-neutral-200 hover:text-neutral-700'
            )}
            title="로그아웃"
          >
            <LogOut className="w-5 h-5" />
          </button>
        )}
      </div>
    </header>
  );
};
