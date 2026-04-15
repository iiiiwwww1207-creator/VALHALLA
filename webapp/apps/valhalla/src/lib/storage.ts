'use client';

import type { DiagnosisAnswer } from '@yggdra/shared';

const STORAGE_KEY = 'valhalla-diagnosis-v1';

export interface StoredDiagnosisState {
  answers: DiagnosisAnswer[];
  completedAt?: string;
}

export function loadDiagnosisState(): StoredDiagnosisState | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as StoredDiagnosisState;
  } catch {
    return null;
  }
}

export function saveDiagnosisState(state: StoredDiagnosisState) {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function clearDiagnosisState() {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.removeItem(STORAGE_KEY);
}
