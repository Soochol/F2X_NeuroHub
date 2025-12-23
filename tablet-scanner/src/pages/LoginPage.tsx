/**
 * Login Page
 *
 * Modern login form for tablet authentication
 * - 애니메이션 로고 (scale + fade)
 * - 폼 필드 순차 등장
 * - 에러 애니메이션 (shake)
 * - 성공 전환 효과
 * - 비밀번호 표시 토글
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, AlertCircle, Cpu, Eye, EyeOff, CheckCircle } from 'lucide-react';
import { authApi, getErrorMessage } from '@/api/client';
import { useAppStore } from '@/store/appStore';
import { Card } from '@/components/ui';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { FadeIn, FadeInScale } from '@/components/animations';
import { cn } from '@/lib/cn';

type LoginState = 'idle' | 'loading' | 'success' | 'error';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setUser } = useAppStore();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loginState, setLoginState] = useState<LoginState>('idle');
  const [error, setError] = useState<string | null>(null);

  const isLoading = loginState === 'loading';
  const isSuccess = loginState === 'success';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoginState('loading');

    try {
      const response = await authApi.login({ username, password });

      // Store token
      localStorage.setItem('access_token', response.access_token);

      // Update store
      setUser(response.user);

      // Success state
      setLoginState('success');

      // Navigate after success animation
      setTimeout(() => {
        navigate('/');
      }, 800);
    } catch (err) {
      setError(getErrorMessage(err));
      setLoginState('error');

      // Reset to idle after shake animation
      setTimeout(() => {
        setLoginState('idle');
      }, 600);
    }
  };

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center min-h-screen px-6 py-8 relative overflow-hidden',
        'transition-all duration-700',
        isSuccess ? 'bg-success-900/20' : 'bg-transparent'
      )}
    >
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary-500/10 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-violet-500/5 rounded-full blur-[120px]" />

      {/* Logo & Title */}
      <FadeInScale delay={100}>
        <div className="text-center mb-12 relative">
          <div
            className={cn(
              'w-24 h-24 mx-auto mb-6',
              'rounded-[2.5rem] shadow-2xl relative group',
              'flex items-center justify-center',
              'transition-all duration-700 border border-white/10',
              isSuccess
                ? 'bg-success-500 scale-110 shadow-success-500/40 border-success-400'
                : 'bg-gradient-to-br from-primary-600 to-primary-400'
            )}
          >
            <div className="absolute inset-0 bg-white/20 rounded-[2.5rem] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            {isSuccess ? (
              <CheckCircle className="w-12 h-12 text-white animate-success-check" />
            ) : (
              <Cpu className={cn('w-12 h-12 text-white relative z-10', isLoading && 'animate-pulse')} />
            )}
          </div>
          <h1
            className={cn(
              'text-4xl font-black mb-3 transition-colors duration-700 tracking-tighter',
              isSuccess ? 'text-success-400' : 'text-dynamic'
            )}
          >
            {isSuccess ? 'WELCOME BACK' : 'NEUROHUB'}
          </h1>
          <p className="text-xs font-black text-primary-400 uppercase tracking-[0.4em] opacity-80">
            {isSuccess ? 'Authentication Successful' : 'Premium Tablet Terminal'}
          </p>
        </div>
      </FadeInScale>

      {/* Login Form */}
      {!isSuccess && (
        <FadeIn delay={200}>
          <div className="w-full max-w-[380px] perspective-1000">
            <Card
              variant="glass"
              className={cn(
                'p-8 border-white/10 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.6)] backdrop-blur-2xl',
                loginState === 'error' && 'animate-error-shake border-danger-500/50'
              )}
            >
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Error message */}
                {error && (
                  <div
                    className={cn(
                      'flex items-center gap-3',
                      'p-4 rounded-2xl',
                      'bg-danger-500/10 border border-danger-500/20',
                      'text-sm font-bold text-danger-400',
                      'animate-in fade-in slide-in-from-top-2 duration-300'
                    )}
                  >
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <span>{error}</span>
                  </div>
                )}

                {/* Username */}
                <FadeIn delay={300}>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-neutral-400 uppercase tracking-widest ml-1">Operator ID</label>
                    <Input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Enter ID..."
                      required
                      autoComplete="username"
                      disabled={isLoading}
                      className="h-14 rounded-2xl"
                    />
                  </div>
                </FadeIn>

                {/* Password */}
                <FadeIn delay={400}>
                  <div className="space-y-1.5 relative">
                    <label className="text-[10px] font-black text-neutral-500 uppercase tracking-widest ml-1">Security Key</label>
                    <div className="relative">
                      <Input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        required
                        autoComplete="current-password"
                        disabled={isLoading}
                        className="h-14 rounded-2xl pr-12"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className={cn(
                          'absolute right-4 top-1/2 -translate-y-1/2',
                          'p-1.5 rounded-lg',
                          'text-neutral-600 hover:text-primary-400',
                          'hover:bg-white/5',
                          'transition-all duration-200'
                        )}
                        tabIndex={-1}
                      >
                        {showPassword ? (
                          <EyeOff className="w-5 h-5" />
                        ) : (
                          <Eye className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </FadeIn>

                {/* Submit Button */}
                <FadeIn delay={500}>
                  <Button
                    type="submit"
                    variant="primary"
                    isLoading={isLoading}
                    disabled={isLoading}
                    className="w-full h-16 mt-4 rounded-2xl btn-action-primary font-black text-lg tracking-tight shadow-xl hover:shadow-primary-500/20"
                  >
                    {!isLoading && <LogIn className="w-6 h-6 mr-2" />}
                    ACCESS SYSTEM
                  </Button>
                </FadeIn>
              </form>
            </Card>
          </div>
        </FadeIn>
      )}

    </div>
  );
};
