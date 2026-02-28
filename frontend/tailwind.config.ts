import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: "#05070c",
        panel: "#0d111a",
        line: "rgba(255,255,255,0.08)",
        primary: "#29b6f6",
        safe: "#22c55e",
        caution: "#eab308",
        danger: "#ef4444"
      },
      boxShadow: {
        glow: "0 0 16px rgba(41, 182, 246, 0.35)"
      },
      backgroundImage: {
        "hero-shader":
          "radial-gradient(circle at 20% 20%, rgba(41,182,246,0.25), transparent 45%), radial-gradient(circle at 80% 0%, rgba(139,92,246,0.2), transparent 40%), linear-gradient(180deg, rgba(255,255,255,0.03), transparent)"
      }
    }
  },
  plugins: []
};

export default config;
