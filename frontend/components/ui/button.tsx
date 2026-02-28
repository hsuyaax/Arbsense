import type { ButtonHTMLAttributes, ReactNode } from "react";

export function Button({
  children,
  active = false,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode; active?: boolean }) {
  const base = "rounded-full border px-3 py-1.5 text-sm transition";
  const state = active
    ? "border-primary bg-primary/20 text-cyan-200 shadow-glow"
    : "border-white/10 bg-white/5 text-slate-300 hover:border-white/20";
  return (
    <button type="button" className={`${base} ${state}`} {...props}>
      {children}
    </button>
  );
}
