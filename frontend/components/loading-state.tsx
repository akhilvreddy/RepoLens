export function LoadingState({ label = "Loading repository intelligence" }: { label?: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-6 shadow-soft">
      <div className="mb-4 h-4 w-44 animate-pulse rounded bg-panel" />
      <div className="space-y-3">
        <div className="h-3 w-full animate-pulse rounded bg-panel" />
        <div className="h-3 w-5/6 animate-pulse rounded bg-panel" />
        <div className="h-3 w-2/3 animate-pulse rounded bg-panel" />
      </div>
      <p className="mt-5 text-sm text-muted">{label}</p>
    </div>
  );
}
