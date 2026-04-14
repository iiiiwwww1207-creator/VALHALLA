'use client';

import type { DiagnosisAnswer } from '@yggdra/shared';

const DIAGNOSIS_KEY = 'yggdra-diagnosis-v1';
const OSHI_KEY = 'yggdra-oshi-v1';

export interface StoredDiagnosisState {
  answers: DiagnosisAnswer[];
  completedAt?: string;
}

export function loadDiagnosisState(): StoredDiagnosisState | null {
  if (typeof window === 'undefined') return null;
  const raw = window.localStorage.getItem(DIAGNOSIS_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredDiagnosisState;
  } catch {
    return null;
  }
}

export function saveDiagnosisState(state: StoredDiagnosisState) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(DIAGNOSIS_KEY, JSON.stringify(state));
}

export function clearDiagnosisState() {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(DIAGNOSIS_KEY);
}

export function saveOshi(hostId: string) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(OSHI_KEY, hostId);
}

export function loadOshi(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(OSHI_KEY);
}

export function getTarotKey(date: string): string {
  return `yggdra-tarot-${date}`;
}

export function hasDoneTarotToday(date: string): boolean {
  if (typeof window === 'undefined') return false;
  return window.localStorage.getItem(getTarotKey(date)) !== null;
}

export function saveTarotResult(date: string, cardIndex: number, isReversed: boolean) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(
    getTarotKey(date),
    JSON.stringify({ cardIndex, isReversed })
  );
}

export function loadTarotResult(date: string): { cardIndex: number; isReversed: boolean } | null {
  if (typeof window === 'undefined') return null;
  const raw = window.localStorage.getItem(getTarotKey(date));
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
