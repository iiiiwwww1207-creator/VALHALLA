import { cn } from '@/lib/utils';

interface ProgressProps {
  value: number;
  className?: string;
}

export function Progress({ value, className }: ProgressProps) {
  return (
    <div className={cn('h-2 w-full overflow-hidden rounded-full bg-white/8', className)}>
      <div
        className="h-full rounded-full bg-gradient-to-r from-primary via-[#f6dea1] to-[#8f5fe8] transition-all duration-500"
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  );
}
