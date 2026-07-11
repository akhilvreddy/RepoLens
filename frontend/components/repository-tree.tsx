import { FileCode2, FolderTree } from "lucide-react";
import type { RepositoryFileSummary } from "@/lib/types";

export function RepositoryTree({ tree, readme }: { tree: RepositoryFileSummary[]; readme: string | null }) {
  const topItems = tree.slice(0, 80);
  return (
    <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
      <div className="rounded-lg border border-border bg-surface p-4">
        <div className="mb-4 flex items-center gap-2">
          <FolderTree className="h-4 w-4 text-accent" aria-hidden="true" />
          <h3 className="text-sm font-semibold text-foreground">Repository Structure</h3>
        </div>
        <div className="max-h-[440px] overflow-auto rounded-md border border-border bg-background p-3 font-mono text-xs leading-6 text-muted">
          {topItems.map((item) => (
            <div key={item.path} className="truncate">
              {item.type === "tree" ? "dir  " : "file "} {item.path}
            </div>
          ))}
          {!topItems.length ? <p>No tree data returned by GitHub.</p> : null}
        </div>
      </div>
      <div className="rounded-lg border border-border bg-surface p-4">
        <div className="mb-4 flex items-center gap-2">
          <FileCode2 className="h-4 w-4 text-accent" aria-hidden="true" />
          <h3 className="text-sm font-semibold text-foreground">README Preview</h3>
        </div>
        <pre className="max-h-[440px] overflow-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 font-mono text-xs leading-6 text-muted">
          {(readme || "No README was returned by the GitHub API.").slice(0, 8000)}
        </pre>
      </div>
    </div>
  );
}
