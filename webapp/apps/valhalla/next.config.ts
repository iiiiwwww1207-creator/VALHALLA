import type { NextConfig } from 'next';

const isProd = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  output: 'export',
  basePath: isProd ? '/VALHALLA' : '',
  assetPrefix: isProd ? '/VALHALLA/' : '',
  transpilePackages: ['@yggdra/shared'],
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
