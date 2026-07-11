import type { HealthScores } from "@/lib/types";

const labels: Record<keyof HealthScores, string> = {
  overall: "Overall",
  activity: "Activity",
  maintenance: "Maintenance",
  contributor: "Contributor",
  issue_health: "Issue Health",
  release: "Release",
  documentation: "Docs",
  engineering_maturity: "Maturity",
};

export function HealthScoreCard({ scores }: { scores: HealthScores }) {
  return (
    <section className="rounded-lg border border-border bg-surface p-5 shadow-soft">
      <div className="mb-5 flex items-end justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Repository Health</h2>
          <p className="mt-1 text-sm text-muted">Deterministic score from activity, maintenance, releases, docs, and engineering signals.</p>
        </div>
        <div className="text-right">
          <div className="text-4xl font-semibold text-accent">{scores.overall}</div>
          <div className="text-xs text-muted">out of 100</div>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {(Object.keys(labels) as Array<keyof HealthScores>).filter((key) => key !== "overall").map((key) => (
          <div key={key} className="rounded-md border border-border bg-background p-3">
            <div className="mb-2 flex justify-between text-sm">
              <span className="text-muted">{labels[key]}</span>
              <span className="font-medium text-foreground">{scores[key]}</span>
            </div>
            <div className="h-2 rounded-full bg-panel">
              <div className="h-2 rounded-full bg-accent" style={{ width: `${scores[key]}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
