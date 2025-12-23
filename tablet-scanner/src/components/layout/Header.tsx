/**
 * Header Component
 *
 * App header with title, network status, and controls
 */
import { Volume2, VolumeX, Calendar, LogOut, Sun, Moon } from 'lucide-react';
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
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
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
  theme,
  onToggleTheme,
}) => {
  return (
    <header className="flex justify-between items-center mb-6">
      {/* Left side - Title and status */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-black tracking-tight" style={{ color: 'var(--app-text)' }}>
            {title}
          </h1>
          {/* Network status indicator */}
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-white/5 border border-white/10">
            <span
              className={cn(
                'w-2 h-2 rounded-full flex-shrink-0 animate-pulse',
                isOnline ? 'bg-success-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]' : 'bg-danger-400 shadow-[0_0_8px_rgba(248,113,113,0.6)]'
              )}
            />
            <span className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">
              {isOnline ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
        {subtitle && (
          <p className="text-sm font-medium text-neutral-400 mt-1 flex items-center gap-2">
            <span className="opacity-70">{subtitle}</span>
            {queueCount > 0 && (
              <span className="bg-warning-500/20 text-warning-400 px-2 py-0.5 rounded text-xs font-bold">
                QUEUE: {queueCount}
              </span>
            )}
          </p>
        )}
      </div>

      {/* Right side - Controls */}
      <div className="flex items-center gap-3 ml-4">
        {/* Theme toggle */}
        <button
          onClick={onToggleTheme}
          className={cn(
            'p-2.5 rounded-xl border transition-all duration-300',
            theme === 'light'
              ? 'bg-amber-500/10 border-amber-500/20 text-amber-600'
              : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400'
          )}
        >
          {theme === 'light' ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>

        {/* Sound toggle */}
        <button
          onClick={onToggleSound}
          className={cn(
            'p-2.5 rounded-xl border transition-all duration-300',
            soundEnabled
              ? 'bg-primary-500/20 border-primary-500/40 text-primary-400'
              : 'bg-white/5 border-white/10 text-neutral-500'
          )}
        >
          {soundEnabled ? (
            <Volume2 className="w-5 h-5" />
          ) : (
            <VolumeX className="w-5 h-5" />
          )}
        </button>

        {/* Date display */}
        {showDate && (
          <div className="hidden md:flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm text-neutral-400">
            <Calendar className="w-4 h-4 text-primary-400" />
            <span className="font-medium tracking-tight">{new Date().toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'short' })}</span>
          </div>
        )}

        {/* Logout button */}
        {onLogout && (
          <button
            onClick={onLogout}
            className={cn(
              'p-2.5 rounded-xl border border-white/10 bg-white/5 text-neutral-400 transition-all duration-300',
              'hover:bg-danger-500/10 hover:border-danger-500/20 hover:text-danger-400'
            )}
          >
            <LogOut className="w-5 h-5" />
          </button>
        )}
      </div>
    </header>
  );
};
