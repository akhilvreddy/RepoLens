"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, RefreshCw } from "lucide-react";
import { analyzeRepository } from "@/lib/api";
import { ErrorState } from "@/components/error-state";

type ReanalyzeButtonProps = {
  repositoryUrl: string;
};

export function ReanalyzeButton({ repositoryUrl }: ReanalyzeButtonProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleReanalyze() {
    setIsLoading(true);
    setError(null);
    try {
      await analyzeRepository(repositoryUrl, true);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh repository analysis.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <button
        type="button"
        onClick={handleReanalyze}
        disabled={isLoading}
        className="inline-flex h-10 items-center gap-2 rounded-md border border-border px-4 text-sm font-medium text-foreground transition hover:border-accent/70 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {isLoading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="h-4 w-4" aria-hidden="true" />}
        {isLoading ? "Reanalyzing..." : "Reanalyze now"}
      </button>
      {error ? <ErrorState message={error} /> : null}
    </div>
  );
}
