import type { NextConfig } from 'next'
import type { webpack } from 'next/dist/compiled/webpack/webpack'

const nextConfig: NextConfig = {
  // use polling for WSL
  webpackDevMiddleware: (config: webpack.Configuration) => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    }
    return config
  },
}

export default nextConfig
