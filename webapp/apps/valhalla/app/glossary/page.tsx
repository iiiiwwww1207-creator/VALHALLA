'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { PageShell } from '@/components/common/page-shell';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const glossary = [
  {
    term: 'サブ担（サブたん）',
    reading: 'さぶたん',
    short: '本担以外で指名しているホスト',
    detail:
      '「サブ担当」の略。一番メインで指名しているホスト（本担）以外に指名しているホストのこと。主に本担への気持ちや悩みを聞いてくれる役割を持っており、本担に直接言えないことを相談できる存在。本担との関係をサポートしてくれる心強い味方。',
    emoji: '🧑‍🤝‍🧑',
  },
  {
    term: '飲み直し（のみなおし）',
    reading: 'のみなおし',
    short: '送り指名のタイミングで追加注文すること',
    detail:
      '送り指名をもらったタイミングで、もう1本ボトルを追加注文してそのまま飲み続けること。飲み直しをするかどうかはお客さんが自由に決めてOK。飲み直しをしない場合はそのまま送りに移ります。',
    emoji: '🍾',
  },
  {
    term: '相伴（あいばん）',
    reading: 'あいばん',
    short: '複数のホストが一緒につくこと',
    detail:
      '担当ホスト以外の別のホストも一緒に席についてくれること。人数が多くなって賑やかになる。担当1人よりも楽しい雰囲気になることも。',
    emoji: '👥',
  },
  {
    term: 'クイック',
    reading: 'くいっく',
    short: '1時間だけ顔を出す来店スタイル',
    detail:
      '1時間だけ来店すること。「クイックで行く」と言えば「ちょっとだけ顔出しに行く」という意味。時間がないときや、軽く会いに行きたいときに使うスタイル。',
    emoji: '⚡',
  },
  {
    term: '送り（おくり）',
    reading: 'おくり',
    short: '退店時にホストが出入り口まで見送ること',
    detail:
      'ホストから「送り指名」をもらい、飲み直しをしない場合にお店の出入り口まで見送ってもらうこと。送り指名をもらったタイミングで飲み直しにするか送りにするかを決めます。担当ホストとの別れ際の特別な時間。',
    emoji: '🚗',
  },
  {
    term: '同伴（どうはん）',
    reading: 'どうはん',
    short: '出勤前のホストと会ってそのままお店に入ること',
    detail:
      'ホストが出勤する前にお客様と会い、ホストの出勤に合わせてそのまま一緒にお店に指名で入ること。お店の外でホストと過ごせる貴重な時間で、担当との距離がぐっと縮まります。',
    emoji: '🌙',
  },
  {
    term: '場内指名（じょうないしめい）',
    reading: 'じょうないしめい',
    short: 'お気に入りのヘルプを優先してつけられる指名',
    detail:
      'お気に入りのヘルプや仲のいいキャストに優先して席についてもらうために、指名のお客様が入れられる指名のこと。担当ホストの指名とは別に、ヘルプとして来てほしいキャストを指定できるシステム。',
    emoji: '🎯',
  },
  {
    term: '通常コール',
    reading: 'つうじょうこーる',
    short: 'オールコール以外のシャンパンコール',
    detail:
      'オールコール以外のシャンパンコールの総称。特定のホストや一部のメンバーが集まって行うコールのこと。オールコールに比べてコンパクトな形で盛り上がる。',
    emoji: '🥂',
  },
  {
    term: 'オールコール',
    reading: 'おーるこーる',
    short: 'キャスト全員が集まるシャンパンコール',
    detail:
      'お店にいるキャスト全員が一斉に集まって行うシャンパンコールのこと。店内が一番盛り上がる瞬間で、特別感が段違い。初めての来店でも圧倒されること間違いなし。',
    emoji: '🎊',
  },
  {
    term: 'ラスソン',
    reading: 'らすそん',
    short: 'その日の売上1位のホストが歌う特別な曲',
    detail:
      '「ラストソング」の略。その日の1日の売上が一番高かったホストが歌う、閉店前の特別な曲のこと。1位のホストにとって名誉ある瞬間で、お店全体が盛り上がる締めくくりのセレモニー。誰がラスソンを歌うかで、その日の売上トップがわかります。',
    emoji: '🎵',
  },
];

function GlossaryCard({ item }: { item: typeof glossary[0] }) {
  const [open, setOpen] = useState(false);
  return (
    <button
      type="button"
      className="w-full text-left"
      onClick={() => setOpen((v) => !v)}
    >
      <Card className="rounded-[20px] border border-white/8 transition-all duration-200 hover:border-sky-400/40">
        <CardContent className="p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{item.emoji}</span>
              <div>
                <p className="font-medium text-sm text-foreground leading-5">{item.term}</p>
                <p className="text-xs text-foreground/50 leading-4">{item.short}</p>
              </div>
            </div>
            {open ? (
              <ChevronUp className="h-4 w-4 text-foreground/40 shrink-0" />
            ) : (
              <ChevronDown className="h-4 w-4 text-foreground/40 shrink-0" />
            )}
          </div>
          {open && (
            <p className="mt-3 pt-3 border-t border-white/8 text-xs leading-6 text-foreground/70 text-pretty">
              {item.detail}
            </p>
          )}
        </CardContent>
      </Card>
    </button>
  );
}

export default function GlossaryPage() {
  const router = useRouter();
  return (
    <PageShell contentClassName="gap-5">
      {/* ヘッダー */}
      <div className="flex items-center justify-between pt-2">
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="px-0">
          <ChevronLeft className="mr-1 h-4 w-4" />
          戻る
        </Button>
      </div>

      {/* タイトル */}
      <section className="space-y-2">
        <div className="flex items-center gap-2 text-xs uppercase text-sky-400/80">
          <span>📖</span>
          はじめてのホストクラブ
        </div>
        <h1 className="font-display text-[2rem] leading-[1.15] text-foreground">
          ホスト用語<br />説明集
        </h1>
        <p className="text-sm leading-6 text-foreground/55 text-pretty">
          初めてホストクラブに来るときに知っておきたい用語を全部解説。タップすると詳しい説明が見られます。
        </p>
      </section>

      {/* 用語リスト */}
      <section className="grid gap-3 pb-6">
        {glossary.map((item) => (
          <GlossaryCard key={item.term} item={item} />
        ))}
      </section>
    </PageShell>
  );
}
