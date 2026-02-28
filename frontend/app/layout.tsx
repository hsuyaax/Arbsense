import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ArbSense — Intelligence Platform",
  description:
    "AI-powered prediction market intelligence layer on BNB Chain. Find safe arbitrage. Skip the traps.",
  keywords: [
    "prediction markets",
    "arbitrage",
    "BNB Chain",
    "DeFi",
    "AI",
    "Web3",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500&family=JetBrains+Mono:wght@100;400;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-base text-white antialiased font-sans leading-relaxed">
        {children}
      </body>
    </html>
  );
}
