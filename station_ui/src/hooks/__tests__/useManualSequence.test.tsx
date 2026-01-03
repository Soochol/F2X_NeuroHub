/**
 * useManualSequence hooks 테스트.
 *
 * 테스트 대상: station_ui/src/hooks/useManualSequence.ts
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { beforeAll, afterAll, afterEach, describe, it, expect, vi } from 'vitest';
import type { ReactNode } from 'react';

import {
  useManualSessions,
  useManualSession,
  useCreateManualSession,
  useInitializeManualSession,
  useFinalizeManualSession,
  useAbortManualSession,
  useRunManualStep,
  useSkipManualStep,
  useDeleteManualSession,
  useHardwareCommands,
  useExecuteHardwareCommand,
} from '../useManualSequence';

// Mock API 응답
const mockSession = {
  id: 'test-session-123',
  sequenceName: 'test_sequence',
  sequenceVersion: '1.0.0',
  status: 'created',
  createdAt: '2026-01-03T10:00:00Z',
  currentStepIndex: 0,
  steps: [
    {
      name: 'initialize',
      displayName: 'Initialize',
      order: 1,
      skippable: false,
      status: 'pending',
      duration: 0,
      measurements: {},
      parameterOverrides: [],
    },
    {
      name: 'test_step',
      displayName: 'Test Step',
      order: 2,
      skippable: true,
      status: 'pending',
      duration: 0,
      measurements: {},
      parameterOverrides: [],
    },
  ],
  hardware: [
    {
      id: 'test_device',
      displayName: 'Test Device',
      connected: false,
      config: {},
      commands: [],
    },
  ],
  parameters: {},
  hardwareConfig: {},
  overallPass: false,
};

const mockStepResult = {
  name: 'test_step',
  displayName: 'Test Step',
  order: 2,
  skippable: true,
  status: 'passed',
  duration: 0.5,
  result: { test: 'passed' },
  measurements: { value: 42 },
  parameterOverrides: [],
};

const mockCommands = [
  { name: 'ping', displayName: 'Ping', parameters: [] },
  { name: 'reset', displayName: 'Reset', parameters: [] },
];

const mockCommandResult = {
  success: true,
  hardwareId: 'test_device',
  command: 'ping',
  result: { status: 'ok' },
  duration: 0.05,
};

// MSW 서버 설정
const server = setupServer(
  // 세션 목록
  http.get('/api/manual-sequence/sessions', () => {
    return HttpResponse.json({
      success: true,
      data: [mockSession],
      message: 'Found 1 sessions',
    });
  }),

  // 세션 조회
  http.get('/api/manual-sequence/sessions/:id', ({ params }) => {
    if (params.id === 'nonexistent') {
      return HttpResponse.json(
        { success: false, error: 'Session not found' },
        { status: 404 }
      );
    }
    return HttpResponse.json({
      success: true,
      data: mockSession,
    });
  }),

  // 세션 생성
  http.post('/api/manual-sequence/sessions', async () => {
    return HttpResponse.json(
      {
        success: true,
        data: mockSession,
        message: 'Session created',
      },
      { status: 201 }
    );
  }),

  // 세션 삭제
  http.delete('/api/manual-sequence/sessions/:id', () => {
    return HttpResponse.json({
      success: true,
      data: true,
    });
  }),

  // 세션 초기화
  http.post('/api/manual-sequence/sessions/:id/initialize', () => {
    return HttpResponse.json({
      success: true,
      data: { ...mockSession, status: 'ready' },
    });
  }),

  // 세션 종료
  http.post('/api/manual-sequence/sessions/:id/finalize', () => {
    return HttpResponse.json({
      success: true,
      data: { ...mockSession, status: 'completed' },
    });
  }),

  // 세션 중단
  http.post('/api/manual-sequence/sessions/:id/abort', () => {
    return HttpResponse.json({
      success: true,
      data: { ...mockSession, status: 'aborted' },
    });
  }),

  // 스텝 실행
  http.post('/api/manual-sequence/sessions/:id/steps/:name/run', () => {
    return HttpResponse.json({
      success: true,
      data: mockStepResult,
    });
  }),

  // 스텝 건너뛰기
  http.post('/api/manual-sequence/sessions/:id/steps/:name/skip', () => {
    return HttpResponse.json({
      success: true,
      data: { ...mockStepResult, status: 'skipped' },
    });
  }),

  // 하드웨어 명령 목록
  http.get('/api/manual-sequence/sessions/:id/hardware/:hw/commands', () => {
    return HttpResponse.json({
      success: true,
      data: mockCommands,
    });
  }),

  // 하드웨어 명령 실행
  http.post('/api/manual-sequence/sessions/:id/hardware/:hw/execute', () => {
    return HttpResponse.json({
      success: true,
      data: mockCommandResult,
    });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// 테스트 wrapper
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}

describe('useManualSequence hooks', () => {
  // =========================================================================
  // FE-06: 세션 데이터 로드
  // =========================================================================
  describe('useManualSession', () => {
    it('FE-06: should load session data', async () => {
      const { result } = renderHook(() => useManualSession('test-session-123'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.id).toBe('test-session-123');
      expect(result.current.data?.status).toBe('created');
    });

    it('should handle session not found', async () => {
      const { result } = renderHook(() => useManualSession('nonexistent'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isError).toBe(true));
    });

    it('should not fetch when sessionId is null', () => {
      const { result } = renderHook(() => useManualSession(null), {
        wrapper: createWrapper(),
      });

      expect(result.current.isFetching).toBe(false);
    });
  });

  // =========================================================================
  // FE-07: 세션 생성 mutation
  // =========================================================================
  describe('useCreateManualSession', () => {
    it('FE-07: should create session', async () => {
      const { result } = renderHook(() => useCreateManualSession(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({ sequenceName: 'test_sequence' });
      });

      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data?.id).toBe('test-session-123');
    });
  });

  // =========================================================================
  // FE-08: 스텝 실행 및 캐시 무효화
  // =========================================================================
  describe('useRunManualStep', () => {
    it('FE-08: should run step and return result', async () => {
      const { result } = renderHook(() => useRunManualStep(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({
          sessionId: 'test-session-123',
          stepName: 'test_step',
        });
      });

      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data?.status).toBe('passed');
    });
  });

  // =========================================================================
  // FE-09: 하드웨어 명령 실행
  // =========================================================================
  describe('useExecuteHardwareCommand', () => {
    it('FE-09: should execute hardware command', async () => {
      const { result } = renderHook(() => useExecuteHardwareCommand(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({
          sessionId: 'test-session-123',
          hardwareId: 'test_device',
          command: 'ping',
        });
      });

      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data?.success).toBe(true);
      expect(result.current.data?.command).toBe('ping');
    });
  });

  // =========================================================================
  // 추가 훅 테스트
  // =========================================================================
  describe('useManualSessions', () => {
    it('should load session list', async () => {
      const { result } = renderHook(() => useManualSessions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(Array.isArray(result.current.data)).toBe(true);
    });
  });

  describe('useInitializeManualSession', () => {
    it('should initialize session', async () => {
      const { result } = renderHook(() => useInitializeManualSession(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync('test-session-123');
      });

      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data?.status).toBe('ready');
    });
  });

  describe('useFinalizeManualSession', () => {
    it('should finalize session', async () => {
      const { result } = renderHook(() => useFinalizeManualSession(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync('test-session-123');
      });

      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data?.status).toBe('completed');
    });
  });

  describe('useAbortManualSession', () => {
    it('should abort session', async () => {
      const { result } = renderHook(() => useAbortManualSession(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync('test-session-123');
      });

      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data?.status).toBe('aborted');
    });
  });

  describe('useSkipManualStep', () => {
    it('should skip step', async () => {
      const { result } = renderHook(() => useSkipManualStep(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync({
          sessionId: 'test-session-123',
          stepName: 'test_step',
        });
      });

      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data?.status).toBe('skipped');
    });
  });

  describe('useDeleteManualSession', () => {
    it('should delete session', async () => {
      const { result } = renderHook(() => useDeleteManualSession(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        await result.current.mutateAsync('test-session-123');
      });

      expect(result.current.isSuccess).toBe(true);
    });
  });

  describe('useHardwareCommands', () => {
    it('should load hardware commands', async () => {
      const { result } = renderHook(
        () => useHardwareCommands('test-session-123', 'test_device'),
        {
          wrapper: createWrapper(),
        }
      );

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(Array.isArray(result.current.data)).toBe(true);
      expect(result.current.data?.length).toBe(2);
    });

    it('should not fetch when sessionId or hardwareId is null', () => {
      const { result } = renderHook(() => useHardwareCommands(null, null), {
        wrapper: createWrapper(),
      });

      expect(result.current.isFetching).toBe(false);
    });
  });
});
