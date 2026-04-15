import Link from 'next/link';
import { ArrowRight, Crown, Sparkles } from 'lucide-react';
import { PageShell } from '@/components/common/page-shell';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function HomePage() {
  return (
    <PageShell contentClassName="gap-8 pt-10">
      <section className="relative overflow-hidden rounded-[32px] border border-primary/20 panel-sheen px-6 py-8 shadow-luxe">
        <div className="absolute inset-x-10 top-0 h-px bg-gradient-to-r from-transparent via-primary/70 to-transparent" />
        <div className="mb-5 flex items-center gap-2 text-xs uppercase text-primary/80">
          <Crown className="h-4 w-4" />
          Valhalla Host Matching
        </div>
        <h1 className="font-display text-5xl leading-none text-gradient-gold text-balance">
          運命の夜を、
          <br />
          指名する。
        </h1>
        <p className="mt-5 text-sm leading-7 text-foreground/78 text-pretty">
          6つの質問で、今のあなたに刺さるホストを診断。見た目だけではなく、距離感や会話の温度まで含めて相性を可視化します。
        </p>
        <div className="mt-8">
          <Button asChild className="w-full">
            <Link href="/diagnosis">
              診断をはじめる
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      <section className="grid gap-4">
        <Card className="rounded-[28px] p-5">
          <div className="flex items-center gap-3 text-sm text-primary">
            <Sparkles className="h-4 w-4" />
            デモで見せるポイント
          </div>
          <div className="mt-4 grid gap-4 text-sm leading-7 text-foreground/72">
            <div>
              <div className="font-medium text-foreground">コーチング系の結果演出</div>
              <p className="text-pretty">「今の自分に合う一本」を提案する、背中を押すトーンで設計。</p>
            </div>
            <div>
              <div className="font-medium text-foreground">黒 × 金 × 深紫の世界観</div>
              <p className="text-pretty">実写ホスト向けに、艶感と奥行きが出る照明表現を UI に反映。</p>
            </div>
            <div>
              <div className="font-medium text-foreground">スマホで見せやすい 375px 基準</div>
              <p className="text-pretty">MTG でそのまま触れる、縦長のデモ導線に揃えています。</p>
            </div>
          </div>
        </Card>
      </section>
    </PageShell>
  );
}
