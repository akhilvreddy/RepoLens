import { BookOpen, ExternalLink, GitFork, Star } from "lucide-react";
import type { RepositorySummary } from "@/lib/types";
import { formatDate, formatNumber } from "@/lib/utils";

export function RepositoryHeader({ repository }: { repository: RepositorySummary }) {
  return (
    <header className="border-b border-border bg-background/95">
      <div className="mx-auto flex max-w-7xl flex-col gap-5 px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm text-muted">
              <BookOpen className="h-4 w-4" aria-hidden="true" />
              <span>{repository.owner}</span>
            </div>
            <h1 className="text-3xl font-semibold tracking-normal text-foreground">{repository.name}</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{repository.description || "No repository description provided."}</p>
          </div>
          <a
            href={repository.github_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-border px-4 text-sm font-medium text-foreground transition hover:border-accent"
          >
            GitHub
            <ExternalLink className="h-4 w-4" aria-hidden="true" />
          </a>
        </div>
        <div className="grid metric-grid gap-3">
          <HeaderStat icon={<Star className="h-4 w-4" />} label="Stars" value={formatNumber(repository.stars)} />
          <HeaderStat icon={<GitFork className="h-4 w-4" />} label="Forks" value={formatNumber(repository.forks)} />
          <HeaderStat label="Language" value={repository.primary_language || "Unknown"} />
          <HeaderStat label="License" value={repository.license || "Unknown"} />
          <HeaderStat label="Updated" value={formatDate(repository.updated_at)} />
        </div>
      </div>
    </header>
  );
}

function HeaderStat({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-3">
      <div className="mb-1 flex items-center gap-2 text-xs uppercase text-muted">
        {icon}
        {label}
      </div>
      <div className="truncate text-sm font-semibold text-foreground">{value}</div>
    </div>
  );
}
