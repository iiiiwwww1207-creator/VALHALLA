'use client';

import { CHARACTER_COLORS } from '@/data/characters';

interface AvatarPlaceholderProps {
  characterId: string;
  name: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeMap = {
  sm: 'w-16 h-16 text-lg',
  md: 'w-24 h-24 text-2xl',
  lg: 'w-36 h-36 text-4xl',
};

export function AvatarPlaceholder({ characterId, name, size = 'md', className = '' }: AvatarPlaceholderProps) {
  const colors = CHARACTER_COLORS[characterId] ?? { bg: '#e0e0e0', text: '#333' };
  const initial = name.charAt(0);

  return (
    <div
      className={`flex items-center justify-center rounded-full font-display font-bold ${sizeMap[size]} ${className}`}
      style={{ backgroundColor: colors.bg, color: colors.text }}
    >
      {initial}
    </div>
  );
}
