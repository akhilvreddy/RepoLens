"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, RotateCcw, X } from "lucide-react";
import { analyzeRepository } from "@/lib/api";
import { ErrorState } from "@/components/error-state";
import { validateGitHubUrl } from "@/lib/utils";

function toFriendlyError(message: string) {
  if (message.includes("404")) return "Repository not found. Confirm the URL and that it is public.";
  if (message.includes("403")) return "Access denied or rate-limited by GitHub. Try again in a moment.";
  if (message.includes("429")) return "Rate limit reached. Please retry shortly.";
  if (message.toLowerCase().includes("network")) return "Network issue detected. Check your connection and retry.";
  return message;
}

export default function AnalyzePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const url = searchParams.get("url")?.trim() || "";
  const abortControllerRef = useRef<AbortController | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = useCallback(async () => {
    if (!validateGitHubUrl(url)) {
      setError("Invalid GitHub URL. Please go back and enter a public repository URL.");
      return;
    }
    setIsLoading(true);
    setError(null);
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const analysis = await analyzeRepository(url, false, { signal: abortController.signal });
      router.replace(`/repositories/${analysis.repository.owner}/${analysis.repository.name}`);
    } catch (err) {
      if (abortController.signal.aborted) return;
      const message = err instanceof Error ? err.message : "Repository analysis failed.";
      setError(toFriendlyError(message));
    } finally {
      if (!abortController.signal.aborted) {
        setIsLoading(false);
      }
    }
  }, [router, url]);

  useEffect(() => {
    runAnalysis();
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [runAnalysis]);

  function handleCancel() {
    abortControllerRef.current?.abort();
    router.push("/");
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-4xl items-center justify-center px-4 sm:px-6">
      <div className="w-full rounded-xl border border-border bg-surface p-8 shadow-soft">
        <h1 className="text-2xl font-semibold text-foreground">Analyzing repository</h1>
        <p className="mt-2 text-sm text-muted">
          RepoLens is fetching repository metadata, engineering metrics, and AI-grounded insights.
        </p>
        <p className="mt-4 rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground">{url || "No repository URL provided."}</p>

        {error ? (
          <div className="mt-6 space-y-4">
            <ErrorState message={error} />
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={runAnalysis}
                className="inline-flex h-10 items-center gap-2 rounded-md bg-accent px-4 text-sm font-semibold text-slate-950 transition hover:bg-accent/90"
              >
                <RotateCcw className="h-4 w-4" aria-hidden="true" />
                Retry analysis
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="inline-flex h-10 items-center gap-2 rounded-md border border-border px-4 text-sm font-medium text-foreground transition hover:border-accent/70"
              >
                <X className="h-4 w-4" aria-hidden="true" />
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="mt-6 space-y-4">
            <div className="inline-flex items-center gap-2 text-sm text-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-accent" aria-hidden="true" />
              {isLoading ? "Working on your repository analysis..." : "Preparing analysis..."}
            </div>
            <button
              type="button"
              onClick={handleCancel}
              className="inline-flex h-10 items-center gap-2 rounded-md border border-border px-4 text-sm font-medium text-foreground transition hover:border-accent/70"
            >
              <X className="h-4 w-4" aria-hidden="true" />
              Cancel
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
