import type { ReactNode } from "react";

export function Accordion({
  title,
  children
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <details className="rounded-lg border border-white/10 bg-white/5 p-3">
      <summary className="cursor-pointer text-sm text-slate-200">{title}</summary>
      <div className="mt-2 text-sm text-slate-300">{children}</div>
    </details>
  );
}
