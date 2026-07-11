import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0f1218",
        surface: "#171b23",
        panel: "#202632",
        border: "#313846",
        foreground: "#f5f7fb",
        muted: "#9aa4b2",
        accent: "#61d394",
        amber: "#f0b85a",
        danger: "#ef6f6c"
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-geist-mono)", "ui-monospace", "SFMono-Regular"]
      },
      boxShadow: {
        soft: "0 18px 60px rgba(0, 0, 0, 0.26)"
      }
    }
  },
  plugins: []
};

export default config;
