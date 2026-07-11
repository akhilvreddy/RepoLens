export function MetricChartFallback() {
  return (
    <div className="rounded-md border border-border bg-surface p-4">
      <p className="text-sm text-muted">No deterministic metrics were available for this repository.</p>
    </div>
  );
}
