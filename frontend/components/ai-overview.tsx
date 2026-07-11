import { BrainCircuit, CheckCircle2, Route, ShieldAlert } from "lucide-react";
import type { AIOverview } from "@/lib/types";

export function AIOverviewPanel({ overview }: { overview: AIOverview }) {
  return (
    <section className="rounded-lg border border-border bg-surface p-5 shadow-soft">
      <div className="mb-4 flex items-center gap-2">
        <BrainCircuit className="h-5 w-5 text-accent" aria-hidden="true" />
        <h2 className="text-lg font-semibold text-foreground">AI Overview</h2>
      </div>
      <p className="text-sm leading-6 text-muted">{overview.summary}</p>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <TextBlock title="Purpose" body={overview.purpose} />
        <TextBlock title="Architecture" body={overview.architecture} />
        <ListBlock icon={<CheckCircle2 className="h-4 w-4 text-accent" />} title="Strengths" items={overview.strengths} />
        <ListBlock icon={<ShieldAlert className="h-4 w-4 text-amber" />} title="Risks" items={overview.risks} />
        <ListBlock icon={<Route className="h-4 w-4 text-accent" />} title="Onboarding Path" items={overview.onboarding_steps} />
        <ListBlock title="Recommendations" items={overview.recommendations} />
      </div>
    </section>
  );
}

function TextBlock({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <h3 className="mb-2 text-sm font-semibold text-foreground">{title}</h3>
      <p className="text-sm leading-6 text-muted">{body}</p>
    </div>
  );
}

function ListBlock({ title, items, icon }: { title: string; items: string[]; icon?: React.ReactNode }) {
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">{icon}{title}</h3>
      <ul className="space-y-2 text-sm leading-6 text-muted">
        {(items.length ? items : ["No grounded item returned."]).map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}
