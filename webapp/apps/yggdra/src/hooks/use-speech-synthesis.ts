'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

interface UseSpeechSynthesisOptions {
  lang?: string;
  pitch?: number;
  rate?: number;
  volume?: number;
  onStart?: (text: string) => void;
  onEnd?: (text: string) => void;
  onError?: (message: string) => void;
}

function pickJapaneseVoice(voices: SpeechSynthesisVoice[]) {
  return (
    voices.find((voice) => voice.lang === 'ja-JP') ??
    voices.find((voice) => voice.lang.startsWith('ja-')) ??
    voices.find((voice) => voice.lang.startsWith('ja')) ??
    null
  );
}

export function useSpeechSynthesis({
  lang = 'ja-JP',
  pitch = 1.18,
  rate = 1.03,
  volume = 1,
  onStart,
  onEnd,
  onError,
}: UseSpeechSynthesisOptions = {}) {
  const [supported, setSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const activeUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const onStartRef = useRef(onStart);
  const onEndRef = useRef(onEnd);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    onStartRef.current = onStart;
    onEndRef.current = onEnd;
    onErrorRef.current = onError;
  }, [onEnd, onError, onStart]);

  useEffect(() => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setSupported(false);
      return;
    }

    setSupported(true);

    const synth = window.speechSynthesis;

    const updateVoices = () => {
      setVoices(synth.getVoices());
    };

    updateVoices();
    synth.addEventListener('voiceschanged', updateVoices);

    return () => {
      synth.removeEventListener('voiceschanged', updateVoices);
      synth.cancel();
      activeUtteranceRef.current = null;
      setIsSpeaking(false);
    };
  }, []);

  const cancel = useCallback(() => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      return;
    }

    window.speechSynthesis.cancel();
    activeUtteranceRef.current = null;
    setIsSpeaking(false);
  }, []);

  const speak = useCallback((text: string) => {
    if (!supported || !text.trim() || typeof window === 'undefined') {
      return false;
    }

    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    const selectedVoice = pickJapaneseVoice(voices);

    synth.cancel();

    utterance.lang = selectedVoice?.lang ?? lang;
    utterance.voice = selectedVoice;
    utterance.pitch = pitch;
    utterance.rate = rate;
    utterance.volume = volume;

    utterance.onstart = () => {
      setIsSpeaking(true);
      onStartRef.current?.(text);
    };

    utterance.onend = () => {
      activeUtteranceRef.current = null;
      setIsSpeaking(false);
      onEndRef.current?.(text);
    };

    utterance.onerror = () => {
      activeUtteranceRef.current = null;
      setIsSpeaking(false);
      onErrorRef.current?.('音声の再生に失敗しました');
    };

    activeUtteranceRef.current = utterance;
    synth.speak(utterance);

    return true;
  }, [lang, pitch, rate, supported, voices, volume]);

  return {
    supported,
    voices,
    isSpeaking,
    speak,
    cancel,
  };
}
