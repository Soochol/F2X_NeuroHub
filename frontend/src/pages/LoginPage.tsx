/**
 * Login Page Component
 */

import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getErrorMessage } from '@/types/api';

export const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ username, password });
      navigate('/');
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, '로그인에 실패했습니다');
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: 'var(--color-bg-secondary)',
    }}>
      <div style={{
        backgroundColor: 'var(--color-bg-primary)',
        padding: '40px',
        borderRadius: '8px',
        boxShadow: 'var(--shadow-lg)',
        border: '1px solid var(--color-border)',
        width: '100%',
        maxWidth: '400px',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: 'var(--color-brand)', margin: 0 }}>
            F2X NeuroHub
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '10px' }}>Manufacturing Execution System</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '5px',
              fontWeight: '500',
              color: 'var(--color-text-primary)',
            }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid var(--color-border-strong)',
                borderRadius: '4px',
                fontSize: '16px',
                boxSizing: 'border-box',
                backgroundColor: 'var(--color-bg-primary)',
                color: 'var(--color-text-primary)',
              }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '5px',
              fontWeight: '500',
              color: 'var(--color-text-primary)',
            }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid var(--color-border-strong)',
                borderRadius: '4px',
                fontSize: '16px',
                boxSizing: 'border-box',
                backgroundColor: 'var(--color-bg-primary)',
                color: 'var(--color-text-primary)',
              }}
            />
          </div>

          {error && (
            <div style={{
              backgroundColor: 'var(--color-badge-error-bg)',
              color: 'var(--color-error)',
              padding: '10px',
              borderRadius: '4px',
              marginBottom: '20px',
              fontSize: '14px',
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: isLoading ? 'var(--color-text-tertiary)' : 'var(--color-brand-400)',
              color: isLoading ? 'var(--color-text-secondary)' : 'var(--color-text-inverse)',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s',
            }}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};
