'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { DiagnosisAnswer } from '@yggdra/shared';
import { DIAGNOSIS_QUESTIONS } from '@yggdra/shared';
import { loadDiagnosisState, saveDiagnosisState } from '@/lib/storage';

function upsertAnswer(answers: DiagnosisAnswer[], next: DiagnosisAnswer) {
  return [...answers.filter((a) => a.questionId !== next.questionId), next];
}

function getAnswerValue(answers: DiagnosisAnswer[], questionId: string) {
  return answers.find((a) => a.questionId === questionId)?.value;
}

export default function DiagnosisPage() {
  const router = useRouter();
  const [answers, setAnswers] = useState<DiagnosisAnswer[]>([]);
  const [step, setStep] = useState(0);
  const [isReady, setIsReady] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    const stored = loadDiagnosisState();
    if (stored?.answers?.length) {
      setAnswers(stored.answers);
      const firstMissing = DIAGNOSIS_QUESTIONS.findIndex(
        (q) => getAnswerValue(stored.answers, q.id) === undefined
      );
      setStep(firstMissing === -1 ? DIAGNOSIS_QUESTIONS.length - 1 : firstMissing);
    }
    setIsReady(true);
  }, []);

  useEffect(() => {
    if (!isReady) return;
    saveDiagnosisState({ answers });
  }, [answers, isReady]);

  const question = DIAGNOSIS_QUESTIONS[step];
  const selectedValue = getAnswerValue(answers, question.id);
  const progressPercent = useMemo(
    () => ((step + 1) / DIAGNOSIS_QUESTIONS.length) * 100,
    [step]
  );

  const animateTo = (nextStep: number) => {
    setIsTransitioning(true);
    window.setTimeout(() => {
      setStep(nextStep);
      setIsTransitioning(false);
    }, 180);
  };

  const handleSelectOption = (value: string) => {
    const nextAnswers = upsertAnswer(answers, { questionId: question.id, value });
    setAnswers(nextAnswers);

    if (step === DIAGNOSIS_QUESTIONS.length - 1) {
      saveDiagnosisState({ answers: nextAnswers, completedAt: new Date().toISOString() });
      router.push('/select');
      return;
    }

    animateTo(step + 1);
  };

  const handleBirthdaySubmit = () => {
    if (typeof selectedValue !== 'string' || !selectedValue) return;
    if (step === DIAGNOSIS_QUESTIONS.length - 1) {
      saveDiagnosisState({ answers, completedAt: new Date().toISOString() });
      router.push('/select');
      return;
    }
    animateTo(step + 1);
  };

  if (!isReady) {
    return (
      <main className="min-h-dvh bg-background flex items-center justify-center px-6">
        <div className="text-muted-foreground text-sm">読み込み中...</div>
      </main>
    );
  }

  return (
    <main className="min-h-dvh bg-background flex flex-col px-6 py-8">
      <div className="w-full max-w-sm mx-auto flex flex-col flex-1">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            type="button"
            onClick={() => (step === 0 ? router.push('/') : setStep(step - 1))}
            className="text-sm text-muted-foreground flex items-center gap-1 transition-opacity duration-200 active:opacity-60"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10 12L6 8L10 4" />
            </svg>
            戻る
          </button>
          <span className="text-sm font-medium text-muted-foreground">
            {step + 1} / {DIAGNOSIS_QUESTIONS.length}
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full h-2 rounded-full bg-muted mb-8 overflow-hidden">
          <div
            className="h-full rounded-full bg-primary transition-all duration-200"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Question card */}
        <div
          className={`flex-1 flex flex-col transition-all duration-200 ${
            isTransitioning ? 'translate-x-4 opacity-0' : 'translate-x-0 opacity-100'
          }`}
        >
          <h2 className="font-display text-2xl font-bold text-foreground text-balance mb-2">
            {question.text}
          </h2>
          <p className="text-sm text-muted-foreground text-pretty mb-6">
            直感で選んでみてね。正解はないよ。
          </p>

          {question.type === 'birthday' ? (
            <div className="flex flex-col gap-4">
              <input
                type="date"
                max={new Date().toISOString().split('T')[0]}
                value={typeof selectedValue === 'string' ? selectedValue : ''}
                onChange={(e) =>
                  setAnswers(
                    upsertAnswer(answers, { questionId: question.id, value: e.target.value })
                  )
                }
                className="w-full px-4 py-3 rounded-2xl border border-border bg-card text-foreground text-base"
              />
              <div className="flex items-start gap-2 px-4 py-3 rounded-2xl bg-muted text-xs text-muted-foreground">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="mt-0.5 shrink-0">
                  <rect x="3" y="7" width="10" height="7" rx="1.5" />
                  <path d="M5 7V5a3 3 0 016 0v2" />
                </svg>
                誕生日はこの診断だけに使います。外部には送信されません。
              </div>
              <button
                type="button"
                onClick={handleBirthdaySubmit}
                disabled={typeof selectedValue !== 'string' || selectedValue.length === 0}
                className="w-full py-3.5 rounded-full bg-primary text-primary-foreground font-bold text-base transition-transform duration-200 active:scale-95 disabled:opacity-40 disabled:active:scale-100"
              >
                次へ
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {question.options?.map((option) => {
                const isActive = selectedValue === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleSelectOption(option.value)}
                    className={`px-5 py-4 rounded-full border-2 text-left text-sm font-medium transition-all duration-200 active:scale-95 ${
                      isActive
                        ? 'border-primary bg-primary text-primary-foreground'
                        : 'border-border bg-card text-foreground'
                    }`}
                  >
                    {option.label}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
