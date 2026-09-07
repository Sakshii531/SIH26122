/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: '/',
        destination: '/planner/dashboard',
        permanent: false,
      },
      {
        source: '/dashboard',
        destination: '/planner/dashboard',
        permanent: false,
      },
      {
        source: '/planner',
        destination: '/planner/dashboard',
        permanent: false,
      },
    ]
  },
}

module.exports = nextConfig
