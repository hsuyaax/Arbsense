import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";

export function Tabs({
  tabs,
  active,
  onChange
}: {
  tabs: readonly string[];
  active: string;
  onChange: (tab: string) => void;
}) {
  return (
    <div className="mb-5 flex flex-wrap gap-2">
      {tabs.map((tab) => (
        <Button key={tab} active={active === tab} onClick={() => onChange(tab)}>
          {tab}
        </Button>
      ))}
    </div>
  );
}

export function TabPanel({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
