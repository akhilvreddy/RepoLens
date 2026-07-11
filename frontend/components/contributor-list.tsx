import type { ContributorSummary } from "@/lib/types";
import { formatNumber } from "@/lib/utils";

export function ContributorList({ contributors }: { contributors: ContributorSummary[] }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <h3 className="mb-4 text-sm font-semibold text-foreground">Top Contributors</h3>
      <div className="space-y-3">
        {contributors.slice(0, 8).map((contributor) => (
          <a key={contributor.login} href={contributor.html_url || "#"} target="_blank" rel="noreferrer" className="flex items-center gap-3 rounded-md p-2 transition hover:bg-panel">
            {contributor.avatar_url ? <img src={contributor.avatar_url} alt="" className="h-8 w-8 rounded-full" /> : <div className="h-8 w-8 rounded-full bg-panel" />}
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-foreground">{contributor.login}</p>
              <p className="text-xs text-muted">{formatNumber(contributor.contributions)} contributions</p>
            </div>
          </a>
        ))}
        {!contributors.length ? <p className="text-sm text-muted">No contributor data returned by GitHub.</p> : null}
      </div>
    </div>
  );
}
