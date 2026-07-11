import { getRepositoryAnalysis } from "@/lib/api";
import { AIOverviewPanel } from "@/components/ai-overview";
import { ActivityChart } from "@/components/activity-chart";
import { ContributorList } from "@/components/contributor-list";
import { HealthScoreCard } from "@/components/health-score-card";
import { IssueList } from "@/components/issue-list";
import { LanguageChart } from "@/components/language-chart";
import { MetricCard } from "@/components/metric-card";
import { RepositoryChat } from "@/components/repository-chat";
import { RepositoryHeader } from "@/components/repository-header";
import { RepositoryTree } from "@/components/repository-tree";
import { LoadingState } from "@/components/loading-state";
import { ErrorState } from "@/components/error-state";
import { MetricChartFallback } from "@/components/metric-fallback";
import { formatDate } from "@/lib/utils";
import type { RepositoryAnalysis } from "@/lib/types";

async function loadRepository(owner: string, repo: string): Promise<RepositoryAnalysis> {
  return getRepositoryAnalysis(owner, repo);
}

export default async function RepositoryPage({
  params,
}: {
  params: Promise<{ owner: string; repo: string }>;
}) {
  const { owner, repo } = await params;
  let analysis: RepositoryAnalysis | null = null;
  let error: string | null = null;

  try {
    analysis = await loadRepository(owner, repo);
  } catch (err) {
    error = err instanceof Error ? err.message : "Failed to load repository analysis.";
  }

  if (error) {
    return <div className="mx-auto flex min-h-screen max-w-7xl items-start px-4 pt-8 sm:px-6 lg:px-8"><ErrorState message={error} /></div>;
  }

  if (!analysis) {
    return <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"><LoadingState label="Loading repository analysis..." /></div>;
  }

  return (
    <main className="mx-auto min-h-screen max-w-7xl px-4 pb-12 pt-6 sm:px-6 lg:px-8">
      <RepositoryHeader repository={analysis.repository} />
      <section className="mt-6 grid gap-4 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-4">
          <AIOverviewPanel overview={analysis.ai_overview} />
          <div className="grid gap-4 md:grid-cols-2">
            <ActivityChart metrics={analysis.metrics} />
            <LanguageChart languages={analysis.repository.languages} />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {analysis.metrics.metrics.length ? analysis.metrics.metrics.map((metric) => <MetricCard key={metric.name} metric={metric} />) : <MetricChartFallback />}
            <ContributorList contributors={analysis.contributors} />
            <IssueList issues={analysis.open_issues} pullRequests={analysis.open_pull_requests} />
          </div>
          <RepositoryTree tree={analysis.tree} readme={analysis.readme} />
        </div>
        <aside className="space-y-4">
          <div className="rounded-lg border border-border bg-surface p-4">
            <h3 className="mb-2 text-sm font-semibold text-foreground">Repository Data Snapshot</h3>
            <SnapshotRow label="Analyzed" value={formatDate(analysis.analyzed_at)} />
            <SnapshotRow label="Cache expires" value={formatDate(analysis.expires_at)} />
            <SnapshotRow label="Open issues" value={`${analysis.metrics.open_issues} open`} />
            <SnapshotRow label="Stale issues" value={`${analysis.metrics.stale_issues} open`} />
            <SnapshotRow label="Open PRs" value={`${analysis.metrics.open_pull_requests}`} />
            <SnapshotRow label="Stale PRs" value={`${analysis.metrics.stale_pull_requests}`} />
            <SnapshotRow label="Contributor coverage" value={`${analysis.metrics.active_contributors} active`} />
            <SnapshotRow label="CI detected" value={analysis.metrics.has_ci ? "Yes" : "No"} />
            <SnapshotRow label="Tests detected" value={analysis.metrics.has_tests ? "Yes" : "No"} />
          </div>
          <HealthScoreCard scores={analysis.metrics.scores} />
          <RepositoryChat owner={analysis.repository.owner} repo={analysis.repository.name} />
        </aside>
      </section>
    </main>
  );
}

function SnapshotRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-border py-2 text-sm">
      <span className="text-muted">{label}</span>
      <span className="text-foreground">{value}</span>
    </div>
  );
}
