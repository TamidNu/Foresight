import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  turbopack: {
    // Ensure Turbopack uses this directory as the workspace root
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
