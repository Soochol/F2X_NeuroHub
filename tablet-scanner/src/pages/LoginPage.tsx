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
        'flex flex-col items-center justify-center min-h-screen bg-neutral-100 px-6 py-8',
        'transition-all duration-500',
        isSuccess && 'bg-success-50'
      )}
    >
      {/* Logo & Title */}
      <FadeInScale delay={100}>
        <div className="text-center mb-10">
          <div
            className={cn(
              'w-20 h-20 mx-auto mb-4',
              'rounded-2xl shadow-lg',
              'flex items-center justify-center',
              'transition-all duration-500',
              isSuccess
                ? 'bg-success-500 scale-110'
                : 'bg-gradient-to-br from-primary-500 to-primary-600'
            )}
          >
            {isSuccess ? (
              <CheckCircle className="w-10 h-10 text-white animate-success-check" />
            ) : (
              <Cpu className={cn('w-10 h-10 text-white', isLoading && 'animate-pulse')} />
            )}
          </div>
          <h1
            className={cn(
              'text-2xl font-bold mb-2 transition-colors duration-500',
              isSuccess ? 'text-success-700' : 'text-neutral-800'
            )}
          >
            {isSuccess ? '로그인 성공!' : 'NeuroHub Scanner'}
          </h1>
          <p className="text-sm text-neutral-500">
            {isSuccess ? '잠시 후 이동합니다...' : '태블릿 QR 스캐너 로그인'}
          </p>
        </div>
      </FadeInScale>

      {/* Login Form */}
      {!isSuccess && (
        <FadeIn delay={200}>
          <Card
            className={cn(
              'w-full max-w-[340px]',
              loginState === 'error' && 'animate-error-shake'
            )}
          >
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Error message */}
              {error && (
                <div
                  className={cn(
                    'flex items-center gap-2',
                    'p-3 rounded-lg',
                    'bg-danger-50 border border-danger-200',
                    'text-sm text-danger-600',
                    'animate-fade-in'
                  )}
                >
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Username */}
              <FadeIn delay={300}>
                <div className="relative">
                  <Input
                    type="text"
                    label="사용자 ID"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="아이디를 입력하세요"
                    required
                    autoComplete="username"
                    disabled={isLoading}
                  />
                </div>
              </FadeIn>

              {/* Password */}
              <FadeIn delay={400}>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    label="비밀번호"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="비밀번호를 입력하세요"
                    required
                    autoComplete="current-password"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className={cn(
                      'absolute right-3 top-[38px]',
                      'p-1 rounded-md',
                      'text-neutral-400 hover:text-neutral-600',
                      'hover:bg-neutral-100',
                      'transition-colors'
                    )}
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </FadeIn>

              {/* Submit Button */}
              <FadeIn delay={500}>
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  isLoading={isLoading}
                  disabled={isLoading}
                  className="w-full mt-2"
                >
                  <LogIn className="w-5 h-5" />
                  로그인
                </Button>
              </FadeIn>
            </form>
          </Card>
        </FadeIn>
      )}

      {/* Footer */}
      <FadeIn delay={600}>
        <div className="mt-6 text-xs text-neutral-400">
          F2X NeuroHub MES v1.0
        </div>
      </FadeIn>
    </div>
  );
};
