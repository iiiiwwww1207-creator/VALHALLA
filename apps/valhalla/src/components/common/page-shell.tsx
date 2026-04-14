import { cn } from '@/lib/utils';

interface PageShellProps {
  children: React.ReactNode;
  contentClassName?: string;
}

export function PageShell({ children, contentClassName }: PageShellProps) {
  return (
    <main className="min-h-dvh px-4 py-6">
      <div className={cn('mx-auto flex min-h-[calc(100dvh-3rem)] max-w-[375px] flex-col', contentClassName)}>
        {children}
      </div>
    </main>
  );
}
