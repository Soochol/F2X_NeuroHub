/**
 * F2X NeuroHub MES - Toast Notification Utilities
 *
 * Wrapper around Ant Design's message API for consistent toast notifications
 */

import { message, notification } from 'antd';

// Default duration in seconds
const DEFAULT_DURATION = 3;

interface ToastOptions {
  duration?: number;
  key?: string;
  onClose?: () => void;
}

interface NotifyOptions {
  title: string;
  description?: string;
  duration?: number;
  placement?: 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
  onClose?: () => void;
}

/**
 * Simple toast messages (small, auto-dismiss)
 */
export const toast = {
  success: (content: string, options?: ToastOptions) => {
    message.success({
      content,
      duration: options?.duration ?? DEFAULT_DURATION,
      key: options?.key,
      onClose: options?.onClose,
    });
  },

  error: (content: string, options?: ToastOptions) => {
    message.error({
      content,
      duration: options?.duration ?? DEFAULT_DURATION,
      key: options?.key,
      onClose: options?.onClose,
    });
  },

  warning: (content: string, options?: ToastOptions) => {
    message.warning({
      content,
      duration: options?.duration ?? DEFAULT_DURATION,
      key: options?.key,
      onClose: options?.onClose,
    });
  },

  info: (content: string, options?: ToastOptions) => {
    message.info({
      content,
      duration: options?.duration ?? DEFAULT_DURATION,
      key: options?.key,
      onClose: options?.onClose,
    });
  },

  loading: (content: string, options?: ToastOptions) => {
    message.loading({
      content,
      duration: options?.duration ?? 0, // Loading doesn't auto-dismiss
      key: options?.key,
      onClose: options?.onClose,
    });
  },

  destroy: (key?: string) => {
    if (key) {
      message.destroy(key);
    } else {
      message.destroy();
    }
  },
};

/**
 * Rich notifications (larger, with title and description)
 */
export const notify = {
  success: (options: NotifyOptions) => {
    notification.success({
      message: options.title,
      description: options.description,
      duration: options.duration ?? 4.5,
      placement: options.placement ?? 'topRight',
      onClose: options.onClose,
    });
  },

  error: (options: NotifyOptions) => {
    notification.error({
      message: options.title,
      description: options.description,
      duration: options.duration ?? 4.5,
      placement: options.placement ?? 'topRight',
      onClose: options.onClose,
    });
  },

  warning: (options: NotifyOptions) => {
    notification.warning({
      message: options.title,
      description: options.description,
      duration: options.duration ?? 4.5,
      placement: options.placement ?? 'topRight',
      onClose: options.onClose,
    });
  },

  info: (options: NotifyOptions) => {
    notification.info({
      message: options.title,
      description: options.description,
      duration: options.duration ?? 4.5,
      placement: options.placement ?? 'topRight',
      onClose: options.onClose,
    });
  },

  destroy: () => {
    notification.destroy();
  },
};

/**
 * API response helper - shows appropriate toast based on response
 */
export const showApiResult = {
  success: (action: string) => {
    toast.success(`${action} 완료`);
  },

  error: (action: string, errorMessage?: string) => {
    const msg = errorMessage ? `${action} 실패: ${errorMessage}` : `${action} 실패`;
    toast.error(msg);
  },
};

export default toast;
