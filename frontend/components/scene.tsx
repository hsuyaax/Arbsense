"use client";

import { useEffect, useRef } from "react";

export function Scene() {
  const streamRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = streamRef.current;
    if (!el) return;

    let chars: string[] = [];
    for (let i = 0; i < 5000; i++) {
      chars.push(Math.random() > 0.5 ? "1" : "0");
      if (Math.random() > 0.95) chars.push("_");
    }
    el.textContent = chars.join(" ");

    const interval = setInterval(() => {
      const idx = Math.floor(Math.random() * chars.length);
      if (chars[idx] === "1") chars[idx] = "0";
      else if (chars[idx] === "0") chars[idx] = "1";
      el.textContent = chars.join(" ");
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className="bg-grid" />
      <div className="binary-stream" ref={streamRef} />
    </>
  );
}
