'use client';

import React, { useEffect } from 'react';
import { Toaster } from 'sonner';

/**
 * Root providers for the application
 * Wraps all global providers like theme, notifications, etc.
 */
export default function Providers({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    // Initialize any global listeners or setup
    console.log('[Providers] Application initialized');
  }, []);

  return (
    <>
      {children}
      <Toaster position="bottom-right" richColors />
    </>
  );
}
