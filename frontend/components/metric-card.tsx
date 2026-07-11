import { Info } from "lucide-react";
import type { RepositoryMetric } from "@/lib/types";
import { cn } from "@/lib/utils";

const statusClass = {
  healthy: "border-accent/40 text-accent",
  warning: "border-amber/50 text-amber",
  risk: "border-danger/50 text-danger",
  unknown: "border-border text-muted",
};

export function MetricCard({ metric }: { metric: RepositoryMetric }) {
  return (
    <div className="group rounded-lg border border-border bg-surface p-4">
      <div className="mb-3 flex items-start justify-between gap-2">
        <h3 className="text-sm font-medium text-muted">{metric.name}</h3>
        <div className="relative">
          <Info className="h-4 w-4 text-muted" aria-hidden="true" />
          <div className="pointer-events-none absolute right-0 top-6 z-10 hidden w-64 rounded-md border border-border bg-background p-3 text-xs leading-5 text-muted shadow-soft group-hover:block">
            {metric.explanation}
          </div>
        </div>
      </div>
      <div className="flex items-end justify-between gap-3">
        <p className="break-words text-2xl font-semibold text-foreground">{metric.display_value}</p>
        <span className={cn("rounded-full border px-2 py-1 text-xs capitalize", statusClass[metric.status])}>{metric.status}</span>
      </div>
    </div>
  );
}
