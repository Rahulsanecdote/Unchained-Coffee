import { useState } from 'react';

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

export function useSessionId() {
  const [sessionId] = useState(() => {
    let id = localStorage.getItem('taste_fit_session_id');
    if (!id) {
      id = generateUUID();
      localStorage.setItem('taste_fit_session_id', id);
    }
    return id;
  });
  return sessionId;
}
