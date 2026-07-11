import type { IssueSummary, PullRequestSummary } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export function IssueList({ issues, pullRequests }: { issues: IssueSummary[]; pullRequests: PullRequestSummary[] }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Panel title="Open Issues" empty="No open issues returned.">
        {issues.slice(0, 8).map((issue) => (
          <a key={issue.number} href={issue.html_url} target="_blank" rel="noreferrer" className="block rounded-md border border-border bg-background p-3 transition hover:border-accent/70">
            <div className="text-sm font-medium text-foreground">#{issue.number} {issue.title}</div>
            <div className="mt-1 text-xs text-muted">Updated {formatDate(issue.updated_at)}</div>
          </a>
        ))}
        {!issues.length ? null : undefined}
      </Panel>
      <Panel title="Open Pull Requests" empty="No open pull requests returned.">
        {pullRequests.slice(0, 8).map((pr) => (
          <a key={pr.number} href={pr.html_url} target="_blank" rel="noreferrer" className="block rounded-md border border-border bg-background p-3 transition hover:border-accent/70">
            <div className="text-sm font-medium text-foreground">#{pr.number} {pr.title}</div>
            <div className="mt-1 text-xs text-muted">Updated {formatDate(pr.updated_at)}</div>
          </a>
        ))}
        {!pullRequests.length ? null : undefined}
      </Panel>
    </div>
  );
}

function Panel({ title, empty, children }: { title: string; empty: string; children: React.ReactNode }) {
  const items = Array.isArray(children) ? children.filter(Boolean) : children;
  const isEmpty = Array.isArray(items) ? items.length === 0 : !items;
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <h3 className="mb-4 text-sm font-semibold text-foreground">{title}</h3>
      <div className="space-y-3">{isEmpty ? <p className="text-sm text-muted">{empty}</p> : children}</div>
    </div>
  );
}
