import type { Metadata, Viewport } from 'next';
import { M_PLUS_Rounded_1c, Noto_Sans_JP } from 'next/font/google';
import './globals.css';

const display = M_PLUS_Rounded_1c({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['400', '500', '700', '800'],
});

const body = Noto_Sans_JP({
  subsets: ['latin'],
  variable: '--font-body',
  weight: ['400', '500', '700'],
});

export const metadata: Metadata = {
  title: 'ユグドラ - あなたの推しアイドルを見つけよう',
  description: 'アイドルマッチング＆育成デモアプリ',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className={`${display.variable} ${body.variable}`}>
        {children}
      </body>
    </html>
  );
}
