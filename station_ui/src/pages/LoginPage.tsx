/**
 * Login page - Authentication gate for the application.
 */

import { useState } from 'react';
import { Activity, LogIn, Loader2, AlertCircle } from 'lucide-react';
import { useOperatorLogin } from '../hooks';
import { Button } from '../components/atoms/Button';

interface LoginPageProps {
  onLoginSuccess: () => void;
}

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const operatorLogin = useOperatorLogin();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!username.trim() || !password.trim()) {
      setError('Username and password are required');
      return;
    }

    try {
      await operatorLogin.mutateAsync({
        username: username.trim(),
        password: password,
      });
      onLoginSuccess();
    } catch (err: unknown) {
      console.error('Login error:', err);
      // Handle different error formats
      if (err && typeof err === 'object') {
        const errorObj = err as Record<string, unknown>;
        // API error format: { code, message, status }
        if (errorObj.message) {
          setError(String(errorObj.message));
        } else if (errorObj.detail) {
          setError(String(errorObj.detail));
        } else {
          setError('Login failed. Please try again.');
        }
      } else if (err instanceof Error) {
        setError(err.message || 'Login failed');
      } else {
        setError('Login failed. Please try again.');
      }
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ backgroundColor: 'var(--color-bg-primary)' }}
    >
      <div
        className="w-full max-w-md p-8 rounded-xl border"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
            style={{ backgroundColor: 'var(--color-brand-500)' }}
          >
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h1
            className="text-2xl font-bold"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Station UI
          </h1>
          <p
            className="text-sm mt-1"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            Sign in to continue
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div
            className="flex items-center gap-2 p-3 rounded-lg mb-4"
            style={{
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              color: 'var(--color-status-error)',
            }}
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              autoFocus
              disabled={operatorLogin.isPending}
              className="w-full px-4 py-3 text-sm rounded-lg border outline-none transition-colors disabled:opacity-50"
              style={{
                backgroundColor: 'var(--color-bg-primary)',
                borderColor: 'var(--color-border-default)',
                color: 'var(--color-text-primary)',
              }}
            />
          </div>

          <div>
            <label
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={operatorLogin.isPending}
              className="w-full px-4 py-3 text-sm rounded-lg border outline-none transition-colors disabled:opacity-50"
              style={{
                backgroundColor: 'var(--color-bg-primary)',
                borderColor: 'var(--color-border-default)',
                color: 'var(--color-text-primary)',
              }}
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={operatorLogin.isPending}
            className="w-full mt-6"
          >
            {operatorLogin.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="w-4 h-4 mr-2" />
                Sign In
              </>
            )}
          </Button>
        </form>

        {/* Footer */}
        <p
          className="text-xs text-center mt-6"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          Use your MES account credentials
        </p>
      </div>
    </div>
  );
}
