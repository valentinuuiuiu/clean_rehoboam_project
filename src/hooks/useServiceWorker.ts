import { useEffect, useState } from 'react';
import { useNotification } from './useNotification';

interface ServiceWorkerHookReturn {
  isReady: boolean;
  isUpdateAvailable: boolean;
  updateServiceWorker: () => void;
}

export function useServiceWorker(): ServiceWorkerHookReturn {
  const [isReady, setIsReady] = useState(false);
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);
  const { addNotification } = useNotification();

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/service-worker.js')
        .then((reg) => {
          setRegistration(reg);
          setIsReady(true);

          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  setIsUpdateAvailable(true);
                  addNotification('info', 'A new version is available', 0);
                }
              });
            }
          });
        })
        .catch((error) => {
          console.error('Service worker registration failed:', error);
          addNotification('error', 'Failed to enable offline support');
        });

      navigator.serviceWorker.addEventListener('controllerchange', () => {
        addNotification('success', 'Application updated to the latest version');
      });
    }
  }, [addNotification]);

  const updateServiceWorker = () => {
    if (registration && registration.waiting) {
      registration.waiting.postMessage({ type: 'SKIP_WAITING' });
    }
  };

  return {
    isReady,
    isUpdateAvailable,
    updateServiceWorker
  };
}