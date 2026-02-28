import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ArbSense",
  description: "Prediction Market Intelligence Layer for BNB Chain"
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
