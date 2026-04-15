import Link from 'next/link';
import type { Host } from '@yggdra/shared';
import { ArrowLeft, Disc3, Gem, HeartHandshake, Music4, Sparkles } from 'lucide-react';
import { PageShell } from '@/components/common/page-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  conversationLabels,
  distanceLabels,
  faceTypeLabels,
  personalityLabels,
  styleLabels,
} from '@/lib/labels';

interface HostProfileProps {
  host: Host;
}

export function HostProfile({ host }: HostProfileProps) {
  return (
    <PageShell contentClassName="gap-5 pb-8 pt-4">
      <div className="flex items-center justify-between">
        <Button asChild variant="ghost" size="sm" className="px-0">
          <Link href="/results">
            <ArrowLeft className="mr-1 h-4 w-4" />
            結果へ戻る
          </Link>
        </Button>
        <Badge variant="secondary">HOST PROFILE</Badge>
      </div>

      <Card className="overflow-hidden border-primary/25">
        <div className="relative h-[420px] w-full overflow-hidden">
          <img src={host.photoUrl} alt={host.displayName} className="h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 p-6">
            <div className="mb-3 flex flex-wrap gap-2">
              <Badge>{faceTypeLabels[host.faceType]}</Badge>
              <Badge>{styleLabels[host.primaryStyleTag]}</Badge>
              <Badge variant="secondary">{host.kpopGroup ?? 'スタイル未設定'}</Badge>
            </div>
            <h1 className="font-display text-5xl leading-none text-white text-balance">{host.displayName}</h1>
            <p className="mt-3 max-w-[280px] text-sm leading-7 text-white/78 text-pretty">{host.catchCopy}</p>
          </div>
        </div>
      </Card>

      <Card className="panel-sheen">
        <CardContent className="space-y-6 p-6">
          <div className="grid gap-3">
            <div className="flex items-center gap-2 text-xs uppercase text-primary/75">
              <Sparkles className="h-4 w-4" />
              3秒で刺さる要素
            </div>
            <div className="flex flex-wrap gap-2">
              {host.stylesTags.map((style) => (
                <Badge key={style}>{styleLabels[style]}</Badge>
              ))}
              {host.personalityTags.map((personality) => (
                <Badge key={personality} variant="secondary">
                  {personalityLabels[personality]}
                </Badge>
              ))}
            </div>
          </div>

          <div className="grid gap-4 text-sm leading-7 text-foreground/78">
            <div className="rounded-[24px] border border-white/10 bg-black/20 p-4">
              <div className="mb-2 flex items-center gap-2 text-xs uppercase text-primary/70">
                <HeartHandshake className="h-4 w-4" />
                接客の芯
              </div>
              <p className="text-pretty">{host.coreValue}</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-[24px] border border-white/10 bg-black/20 p-4">
                <div className="text-xs uppercase text-primary/70">距離感</div>
                <p className="mt-2">{distanceLabels[host.distanceType]}</p>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-black/20 p-4">
                <div className="text-xs uppercase text-primary/70">会話</div>
                <p className="mt-2">{conversationLabels[host.conversationStyle]}</p>
              </div>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-black/20 p-4">
              <div className="mb-3 flex items-center gap-2 text-xs uppercase text-primary/70">
                <Gem className="h-4 w-4" />
                趣味
              </div>
              <div className="flex flex-wrap gap-2">
                {host.hobbies.map((hobby) => (
                  <Badge key={hobby} variant="secondary">
                    {hobby}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-black/20 p-4">
              <div className="mb-3 flex items-center gap-2 text-xs uppercase text-primary/70">
                <Music4 className="h-4 w-4" />
                音楽
              </div>
              <div className="flex flex-wrap gap-2">
                {host.musicGenres.map((genre) => (
                  <Badge key={genre}>{genre}</Badge>
                ))}
              </div>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-black/20 p-4">
              <div className="mb-3 flex items-center gap-2 text-xs uppercase text-primary/70">
                <Disc3 className="h-4 w-4" />
                仮面と素顔の隙間
              </div>
              <p className="text-pretty">
                {host.gapText ?? '派手に見えても、会話のテンポは相手に合わせるタイプ。刺さる一言のあとに静けさを残すので、余韻ごと記憶に残ります。'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-3">
        <Button disabled className="w-full">
          シャンパンコール
          <span className="ml-2 text-xs opacity-80">Coming Soon</span>
        </Button>
        <Button disabled variant="outline" className="w-full">
          店舗予約
          <span className="ml-2 text-xs opacity-80">Coming Soon</span>
        </Button>
      </div>
    </PageShell>
  );
}
