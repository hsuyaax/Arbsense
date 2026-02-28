import type { ReactNode } from "react";

export function Badge({
  children,
  variant = "default"
}: {
  children: ReactNode;
  variant?: "default" | "safe" | "caution" | "danger";
}) {
  const cls =
    variant === "safe"
      ? "border-green-400/30 bg-green-500/20 text-green-300"
      : variant === "danger"
        ? "border-red-400/30 bg-red-500/20 text-red-300"
        : variant === "caution"
          ? "border-yellow-400/30 bg-yellow-500/20 text-yellow-300"
          : "border-white/20 bg-white/10 text-slate-200";
  return <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${cls}`}>{children}</span>;
}
