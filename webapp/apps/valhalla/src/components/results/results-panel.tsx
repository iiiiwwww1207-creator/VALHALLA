'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { DiagnosisAnswer } from '@yggdra/shared';
import { getTopMatches } from '@yggdra/shared';
import { ArrowLeft, ArrowRight, Crown, Sparkles } from 'lucide-react';
import { PageShell } from '@/components/common/page-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { hosts } from '@/data/hosts';
import { faceTypeLabels, styleLabels } from '@/lib/labels';
import { clearDiagnosisState, loadDiagnosisState } from '@/lib/storage';

function getCoachMessage(topHostName: string) {
  return `${topHostName}は、今のあなたが無理なく魅力を出せる相手。背伸びよりも、気分が上がる素直さで会いに行くと流れが動きます。`;
}

export function ResultsPanel() {
  const router = useRouter();
  const [answers, setAnswers] = useState<DiagnosisAnswer[] | null>(null);

  useEffect(() => {
    const stored = loadDiagnosisState();
    if (!stored?.answers?.length) {
      router.replace('/diagnosis');
      return;
    }
    setAnswers(stored.answers);
  }, [router]);

  const results = useMemo(() => {
    if (!answers?.length) {
      return [];
    }
    return getTopMatches(answers, hosts, 3).map((result) => ({
      ...result,
      host: hosts.find((host) => host.id === result.hostId)!,
    }));
  }, [answers]);

  if (!answers) {
    return (
      <PageShell contentClassName="justify-center">
        <Card className="p-6 text-center text-sm text-foreground/70">結果を計算中...</Card>
      </PageShell>
    );
  }

  const topHost = results[0]?.host;

  return (
    <PageShell contentClassName="gap-5 pb-8 pt-4">
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" className="px-0" onClick={() => router.push('/diagnosis')}>
          <ArrowLeft className="mr-1 h-4 w-4" />
          診断へ戻る
        </Button>
        <Badge variant="secondary">TOP 3 MATCHES</Badge>
      </div>

      <Card className="overflow-hidden border-primary/25 panel-sheen">
        <CardContent className="space-y-4 p-6">
          <div className="flex items-center gap-2 text-xs uppercase text-primary/75">
            <Crown className="h-4 w-4" />
            Coaching Message
          </div>
          <h1 className="font-display text-4xl leading-none text-gradient-gold text-balance">診断結果</h1>
          <p className="text-sm leading-7 text-foreground/78 text-pretty">
            {topHost ? getCoachMessage(topHost.displayName) : 'あなたの運命ラインを解析中です。'}
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {results.map(({ host, score, matchReasons }, index) => (
          <Card key={host.id} className="overflow-hidden">
            <div className="relative h-48 w-full overflow-hidden">
              <img
                src={host.photoUrl}
                alt={host.displayName}
                className="h-full w-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent" />
              <div className="absolute left-4 top-4">
                <Badge>{`No.${index + 1}`}</Badge>
              </div>
              <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between">
                <div>
                  <p className="font-display text-3xl text-white">{host.displayName}</p>
                  <p className="text-xs text-white/72 text-pretty">{host.kpopGroup}</p>
                </div>
                <div className="rounded-full border border-primary/30 bg-black/45 px-4 py-2 text-right">
                  <div className="text-[10px] uppercase text-primary/70">Match</div>
                  <div className="text-xl font-semibold text-primary">{score}%</div>
                </div>
              </div>
            </div>
            <CardContent className="space-y-4 p-5">
              <div className="flex flex-wrap gap-2">
                <Badge>{faceTypeLabels[host.faceType]}</Badge>
                <Badge variant="secondary">{styleLabels[host.primaryStyleTag]}</Badge>
              </div>
              <div className="space-y-2 text-sm leading-6 text-foreground/72">
                {matchReasons.slice(0, 2).map((reason) => (
                  <div key={reason} className="flex items-start gap-2">
                    <Sparkles className="mt-1 h-3.5 w-3.5 shrink-0 text-primary" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
              <Button asChild variant="outline" className="w-full">
                <Link href={`/host/${host.id}`}>
                  プロフィールを見る
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Button
        variant="secondary"
        className="w-full"
        onClick={() => {
          clearDiagnosisState();
          router.push('/diagnosis');
        }}
      >
        もう一度診断する
      </Button>
    </PageShell>
  );
}
