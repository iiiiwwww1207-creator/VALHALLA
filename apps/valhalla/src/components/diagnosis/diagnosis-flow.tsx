'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { DiagnosisAnswer } from '@yggdra/shared';
import { DIAGNOSIS_QUESTIONS } from '@yggdra/shared';
import { ChevronLeft, LockKeyhole, Sparkles } from 'lucide-react';
import { PageShell } from '@/components/common/page-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { loadDiagnosisState, saveDiagnosisState } from '@/lib/storage';

function upsertAnswer(answers: DiagnosisAnswer[], nextAnswer: DiagnosisAnswer) {
  const next = answers.filter((answer) => answer.questionId !== nextAnswer.questionId);
  next.push(nextAnswer);
  return next;
}

function getAnswerValue(answers: DiagnosisAnswer[], questionId: string) {
  return answers.find((answer) => answer.questionId === questionId)?.value;
}

export function DiagnosisFlow() {
  const router = useRouter();
  const [answers, setAnswers] = useState<DiagnosisAnswer[]>([]);
  const [step, setStep] = useState(0);
  const [isReady, setIsReady] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    const stored = loadDiagnosisState();
    if (stored?.answers?.length) {
      setAnswers(stored.answers);
      const firstMissingIndex = DIAGNOSIS_QUESTIONS.findIndex(
        (question) => getAnswerValue(stored.answers, question.id) === undefined
      );
      setStep(firstMissingIndex === -1 ? DIAGNOSIS_QUESTIONS.length - 1 : firstMissingIndex);
    }
    setIsReady(true);
  }, []);

  useEffect(() => {
    if (!isReady) {
      return;
    }

    saveDiagnosisState({ answers });
  }, [answers, isReady]);

  const question = DIAGNOSIS_QUESTIONS[step];
  const selectedValue = getAnswerValue(answers, question.id);
  const progressValue = useMemo(
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
      saveDiagnosisState({
        answers: nextAnswers,
        completedAt: new Date().toISOString(),
      });
      router.push('/results');
      return;
    }

    animateTo(step + 1);
  };

  const handleBirthdaySubmit = () => {
    if (typeof selectedValue !== 'string' || !selectedValue) {
      return;
    }
    animateTo(step + 1);
  };

  if (!isReady) {
    return (
      <PageShell contentClassName="justify-center">
        <Card className="p-6 text-center text-sm text-foreground/70">診断データを読み込み中...</Card>
      </PageShell>
    );
  }

  return (
    <PageShell contentClassName="justify-between">
      <div className="space-y-5">
        <div className="flex items-center justify-between pt-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => (step === 0 ? router.push('/') : setStep(step - 1))}
            className="px-0"
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            戻る
          </Button>
          <Badge variant="secondary">Question {step + 1} / 6</Badge>
        </div>

        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs uppercase text-primary/75">
            <Sparkles className="h-3.5 w-3.5" />
            Destiny Diagnosis
          </div>
          <Progress value={progressValue} />
        </div>
      </div>

      <Card
        className={`my-6 overflow-hidden border-primary/20 panel-sheen transition-all duration-300 ${
          isTransitioning ? 'translate-y-3 opacity-0' : 'translate-y-0 opacity-100'
        }`}
      >
        <CardContent className="space-y-6 p-6">
          <div className="space-y-3">
            <p className="text-xs uppercase text-primary/70 text-pretty">運命のヒント</p>
            <h1 className="font-display text-[2.2rem] leading-[1.05] text-foreground text-balance">
              {question.text}
            </h1>
            <p className="text-sm leading-7 text-foreground/68 text-pretty">
              直感で選んで大丈夫。考えすぎず、今いちばん惹かれるものを選んでください。
            </p>
          </div>

          {question.type === 'birthday' ? (
            <div className="space-y-4">
              <Input
                type="date"
                max={new Date().toISOString().split('T')[0]}
                value={typeof selectedValue === 'string' ? selectedValue : ''}
                onChange={(event) =>
                  setAnswers(
                    upsertAnswer(answers, {
                      questionId: question.id,
                      value: event.target.value,
                    })
                  )
                }
              />
              <div className="flex items-start gap-2 rounded-2xl border border-white/8 bg-black/20 px-4 py-3 text-xs leading-6 text-foreground/62">
                <LockKeyhole className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                誕生日はデモ用の診断にのみ利用します。外部公開はしません。
              </div>
              <Button
                className="w-full"
                onClick={handleBirthdaySubmit}
                disabled={typeof selectedValue !== 'string' || selectedValue.length === 0}
              >
                次へ進む
              </Button>
            </div>
          ) : (
            <div className="grid gap-3">
              {question.options?.map((option) => {
                const isActive = selectedValue === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleSelectOption(option.value)}
                    className={`rounded-[24px] border px-4 py-4 text-left transition-all duration-200 ${
                      isActive
                        ? 'border-primary/65 bg-primary/12 shadow-[0_12px_32px_rgba(212,175,55,0.12)]'
                        : 'border-white/8 bg-black/20 hover:border-primary/35 hover:bg-white/5'
                    }`}
                  >
                    <div className="text-sm font-medium leading-6 text-foreground">{option.label}</div>
                  </button>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

    </PageShell>
  );
}
