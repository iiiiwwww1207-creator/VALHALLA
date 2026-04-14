import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  transpilePackages: ['@yggdra/shared'],
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'placehold.co',
      },
    ],
  },
};

export default nextConfig;
