/**
 * Unit tests for logger utility.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createLogger, nullLogger } from './logger';

// Need to test pre-configured loggers separately since they're singletons
// and would share spy state across tests

describe('logger', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'info').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('createLogger', () => {
    it('should create logger with prefix', () => {
      const log = createLogger({ prefix: 'TestLogger' });

      log.debug('test message');

      expect(console.log).toHaveBeenCalledWith('[TestLogger] test message');
    });

    it('should support all log levels', () => {
      const log = createLogger({ prefix: 'Test', minLevel: 'debug' });

      log.debug('debug msg');
      log.info('info msg');
      log.warn('warn msg');
      log.error('error msg');

      expect(console.log).toHaveBeenCalled();
      expect(console.info).toHaveBeenCalled();
      expect(console.warn).toHaveBeenCalled();
      expect(console.error).toHaveBeenCalled();
    });

    it('should respect minLevel', () => {
      const log = createLogger({ prefix: 'Test', minLevel: 'warn' });

      log.debug('debug');
      log.info('info');
      log.warn('warn');
      log.error('error');

      // debug and info should NOT be called because minLevel is warn
      expect(console.log).not.toHaveBeenCalled();
      expect(console.info).not.toHaveBeenCalled();
      expect(console.warn).toHaveBeenCalledWith('[Test] warn');
      expect(console.error).toHaveBeenCalledWith('[Test] error');
    });

    it('should include timestamps when configured', () => {
      const log = createLogger({ prefix: 'Test', timestamps: true });

      log.info('test');

      expect(console.info).toHaveBeenCalled();
      const call = vi.mocked(console.info).mock.calls[0]?.[0] as string;
      // Should contain ISO timestamp format followed by prefix
      expect(call).toMatch(/^\d{4}-\d{2}-\d{2}T.+ \[Test\] test$/);
    });

    it('should truncate IDs correctly', () => {
      const log = createLogger({ prefix: 'Test' });

      expect(log.truncateId('abcdefghijklmnop')).toBe('abcdefgh...');
      expect(log.truncateId('short')).toBe('short');
      expect(log.truncateId('12345678')).toBe('12345678');
      expect(log.truncateId('123456789')).toBe('12345678...');
    });

    it('should format batch logs', () => {
      const log = createLogger({ prefix: 'Test', minLevel: 'debug' });

      log.batch('abcdefghijklmnop', 'action', { key: 'value' });

      expect(console.log).toHaveBeenCalled();
      const call = vi.mocked(console.log).mock.calls[0]?.[0] as string;
      expect(call).toContain('action');
      expect(call).toContain('abcdefgh...');
      expect(call).toContain('key=value');
    });

    it('should pass additional arguments', () => {
      const log = createLogger({ prefix: 'Test' });

      log.debug('message', { extra: 'data' }, 123);

      expect(console.log).toHaveBeenCalledWith(
        '[Test] message',
        { extra: 'data' },
        123
      );
    });
  });

  describe('pre-configured loggers', () => {
    it('wsLogger should have WS prefix', async () => {
      // Import fresh instance to avoid singleton state issues
      const { wsLogger } = await import('./logger');
      wsLogger.debug('test');
      expect(console.log).toHaveBeenCalledWith('[WS] test');
    });

    it('batchLogger should have batchStore prefix', async () => {
      // Import fresh instance to avoid singleton state issues
      const { batchLogger } = await import('./logger');
      batchLogger.debug('test');
      expect(console.log).toHaveBeenCalledWith('[batchStore] test');
    });
  });

  describe('nullLogger', () => {
    it('should not log anything', () => {
      nullLogger.debug('debug');
      nullLogger.info('info');
      nullLogger.warn('warn');
      nullLogger.error('error');
      nullLogger.batch('id', 'action');

      // nullLogger methods are no-ops, so no console methods should be called
      expect(console.log).not.toHaveBeenCalled();
      expect(console.info).not.toHaveBeenCalled();
      expect(console.warn).not.toHaveBeenCalled();
      expect(console.error).not.toHaveBeenCalled();
    });

    it('truncateId should still work', () => {
      expect(nullLogger.truncateId('abcdefghijklmnop')).toBe('abcdefgh');
    });
  });
});
