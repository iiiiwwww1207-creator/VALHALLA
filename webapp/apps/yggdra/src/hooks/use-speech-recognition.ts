'use client';

import { useEffect, useRef, useState } from 'react';

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  length: number;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionResultList {
  length: number;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognitionInstance extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  onstart: ((event: Event) => void) | null;
  onend: ((event: Event) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

type SpeechRecognitionConstructor = new () => SpeechRecognitionInstance;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

interface UseSpeechRecognitionOptions {
  lang?: string;
  silenceDelayMs?: number;
  onResult?: (text: string) => void;
  onSilence?: (text: string) => void;
  onError?: (message: string) => void;
}

function getSpeechRecognitionConstructor() {
  if (typeof window === 'undefined') {
    return null;
  }

  return window.SpeechRecognition ?? window.webkitSpeechRecognition ?? null;
}

function normalizeSpeechText(text: string) {
  return text.replace(/\s+/g, ' ').trim();
}

export function useSpeechRecognition({
  lang = 'ja-JP',
  silenceDelayMs = 1500,
  onResult,
  onSilence,
  onError,
}: UseSpeechRecognitionOptions = {}) {
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const silenceTimerRef = useRef<number | null>(null);
  const finalTranscriptRef = useRef('');
  const stopRequestedRef = useRef(false);
  const onResultRef = useRef(onResult);
  const onSilenceRef = useRef(onSilence);
  const onErrorRef = useRef(onError);
  const [supported, setSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [finalTranscript, setFinalTranscript] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    onResultRef.current = onResult;
    onSilenceRef.current = onSilence;
    onErrorRef.current = onError;
  }, [onError, onResult, onSilence]);

  useEffect(() => {
    const Recognition = getSpeechRecognitionConstructor();

    if (!Recognition) {
      setSupported(false);
      return;
    }

    const recognition = new Recognition();
    recognition.lang = lang;
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setError('');
      setIsListening(true);
    };

    recognition.onend = () => {
      setIsListening(false);
      stopRequestedRef.current = false;
    };

    recognition.onerror = (event) => {
      const message = event.message || event.error || '音声入力の開始に失敗しました';
      setError(message);
      onErrorRef.current?.(message);
    };

    recognition.onresult = (event) => {
      let nextFinalTranscript = '';
      let nextInterimTranscript = '';

      for (let index = 0; index < event.results.length; index += 1) {
        const result = event.results[index];
        const transcript = normalizeSpeechText(result[0]?.transcript ?? '');

        if (!transcript) {
          continue;
        }

        if (result.isFinal) {
          nextFinalTranscript = `${nextFinalTranscript} ${transcript}`.trim();
        } else {
          nextInterimTranscript = `${nextInterimTranscript} ${transcript}`.trim();
        }
      }

      finalTranscriptRef.current = nextFinalTranscript;
      setFinalTranscript(nextFinalTranscript);
      setInterimTranscript(nextInterimTranscript);

      const combinedTranscript = normalizeSpeechText(
        [nextFinalTranscript, nextInterimTranscript].filter(Boolean).join(' ')
      );

      if (combinedTranscript) {
        onResultRef.current?.(combinedTranscript);
      }

      if (!nextFinalTranscript) {
        return;
      }

      if (silenceTimerRef.current) {
        window.clearTimeout(silenceTimerRef.current);
      }

      silenceTimerRef.current = window.setTimeout(() => {
        const latestTranscript = normalizeSpeechText(finalTranscriptRef.current);

        if (!latestTranscript) {
          return;
        }

        stopRequestedRef.current = true;
        recognitionRef.current?.stop();
        onSilenceRef.current?.(latestTranscript);
      }, silenceDelayMs);
    };

    recognitionRef.current = recognition;
    setSupported(true);

    return () => {
      recognition.onstart = null;
      recognition.onend = null;
      recognition.onerror = null;
      recognition.onresult = null;

      if (silenceTimerRef.current) {
        window.clearTimeout(silenceTimerRef.current);
      }

      recognition.abort();
      recognitionRef.current = null;
    };
  }, [lang, silenceDelayMs]);

  const resetTranscript = () => {
    finalTranscriptRef.current = '';
    setFinalTranscript('');
    setInterimTranscript('');
    setError('');

    if (silenceTimerRef.current) {
      window.clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  };

  const startListening = () => {
    const recognition = recognitionRef.current;
    if (!recognition || isListening) {
      return;
    }

    resetTranscript();

    try {
      recognition.start();
    } catch (startError) {
      const message =
        startError instanceof Error
          ? startError.message
          : '音声入力の開始に失敗しました';

      setError(message);
      onErrorRef.current?.(message);
    }
  };

  const stopListening = () => {
    if (!recognitionRef.current) {
      return;
    }

    stopRequestedRef.current = true;
    recognitionRef.current.stop();
  };

  return {
    supported,
    isListening,
    interimTranscript,
    finalTranscript,
    transcript: normalizeSpeechText([finalTranscript, interimTranscript].join(' ')),
    error,
    startListening,
    stopListening,
    resetTranscript,
  };
}
