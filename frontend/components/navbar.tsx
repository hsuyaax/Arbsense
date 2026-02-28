"use client";

import { useState } from "react";

type Props = {
  tabs: readonly string[];
  active: string;
  onChange: (tab: string) => void;
};

export function Navbar({ tabs, active, onChange }: Props) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="animate-fade-in-down">
      {/* Top bar */}
      <div className="flex justify-between items-center py-6">
        {/* Logo */}
        <div className="flex items-center gap-3 group cursor-default">
          <div className="w-8 h-8 border border-white/20 flex items-center justify-center text-[10px] font-mono group-hover:border-white/50 transition-colors duration-300">
            AS
          </div>
          <div className="flex flex-col">
            <span className="text-[18px] font-light tracking-tight leading-none">ArbSense</span>
            <span className="font-mono text-[9px] text-muted tracking-wider uppercase">prediction intelligence</span>
          </div>
        </div>

        {/* Desktop CTA */}
        <div className="hidden md:flex items-center gap-4">
          <div className="flex items-center gap-2 font-mono text-[10px] text-muted">
            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-blink" />
            LIVE
          </div>
          <a
            href="https://testnet.bscscan.com/address/0x7Ba8FA52dAEd1c1Ea1acEB26E52339946458DeDa"
            target="_blank"
            rel="noreferrer"
            className="bg-white text-[#030303] px-5 py-2 font-mono text-[11px] font-medium cursor-pointer hover:bg-neutral-200 transition-all duration-200 hover:-translate-y-px active:translate-y-0"
          >
            View Contract
          </a>
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden bg-transparent border border-white/12 p-2 cursor-pointer"
        >
          <div className="flex flex-col gap-1">
            <span className={`w-4 h-px bg-white transition-all duration-300 ${mobileOpen ? "rotate-45 translate-y-[3px]" : ""}`} />
            <span className={`w-4 h-px bg-white transition-all duration-300 ${mobileOpen ? "opacity-0" : ""}`} />
            <span className={`w-4 h-px bg-white transition-all duration-300 ${mobileOpen ? "-rotate-45 -translate-y-[3px]" : ""}`} />
          </div>
        </button>
      </div>

      {/* Tab navigation */}
      <nav className={`border-t border-b border-border py-3 ${mobileOpen ? "block" : "hidden md:block"}`}>
        <div className="flex gap-1 flex-wrap">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => {
                onChange(tab);
                setMobileOpen(false);
              }}
              className={`
                relative px-4 py-2 font-mono text-[11px] uppercase tracking-wider
                bg-transparent border-none cursor-pointer
                transition-all duration-200
                ${active === tab
                  ? "text-white"
                  : "text-muted hover:text-white"
                }
              `}
            >
              {active === tab && (
                <span className="absolute inset-0 bg-white/[0.06] border border-white/[0.12]" />
              )}
              <span className="relative">/ {tab}</span>
            </button>
          ))}
        </div>
      </nav>
    </header>
  );
}
