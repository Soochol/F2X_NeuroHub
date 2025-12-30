/**
 * Application entry point with provider hierarchy.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { queryClient } from './api/queryClient';
import { WebSocketProvider } from './contexts';
import { ErrorBoundary } from './components/common';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <WebSocketProvider>
          <BrowserRouter basename="/ui">
            <App />
          </BrowserRouter>
        </WebSocketProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>
);
