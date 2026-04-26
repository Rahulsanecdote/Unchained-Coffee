import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export default function BottomDrawer({ isOpen, onClose, children, title }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  return (
    <>
      <div
        className={`fixed inset-0 bg-black/60 z-40 transition-opacity duration-300
          ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
        data-testid="drawer-overlay"
      />
      <div
        className={`fixed bottom-0 left-0 right-0 z-50 bg-[var(--w-bg)] rounded-t-2xl
          transition-transform duration-500 ease-out
          ${isOpen ? 'translate-y-0' : 'translate-y-full'}`}
        style={{ maxHeight: '88vh' }}
        data-testid="bottom-drawer"
      >
        <div className="flex items-center justify-between px-5 pt-4 pb-2">
          <div className="w-10 h-1 rounded-full bg-[var(--w-text-sec)] opacity-40 mx-auto absolute left-1/2 -translate-x-1/2 top-3" />
          {title && (
            <h3 className="font-heading text-lg font-semibold text-[var(--w-text)]">{title}</h3>
          )}
          <button
            onClick={onClose}
            className="ml-auto p-1 rounded-lg hover:bg-[var(--w-surface)] transition-colors"
            data-testid="drawer-close-btn"
          >
            <X size={20} className="text-[var(--w-text-sec)]" />
          </button>
        </div>
        <div className="overflow-y-auto px-5 pb-8 scrollbar-hide" style={{ maxHeight: 'calc(88vh - 56px)' }}>
          {children}
        </div>
      </div>
    </>
  );
}
