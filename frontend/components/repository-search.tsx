"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Github, Loader2 } from "lucide-react";
import { validateGitHubUrl } from "@/lib/utils";
import { ErrorState } from "@/components/error-state";

const examples = ["https://github.com/fastapi/fastapi", "https://github.com/vercel/next.js", "https://github.com/pallets/flask"];

export function RepositorySearch() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!validateGitHubUrl(url)) {
      setError("Enter a public GitHub repository URL like https://github.com/fastapi/fastapi.");
      return;
    }
    setIsLoading(true);
    router.push(`/analyze?url=${encodeURIComponent(url.trim())}`);
  }

  return (
    <div className="rounded-lg border border-border bg-surface p-4 shadow-soft sm:p-5">
      <form onSubmit={onSubmit} className="space-y-4">
        <label htmlFor="repository-url" className="text-sm font-medium text-foreground">
          GitHub repository URL
        </label>
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Github className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" aria-hidden="true" />
            <input
              id="repository-url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://github.com/owner/repository"
              className="h-12 w-full rounded-md border border-border bg-background pl-10 pr-3 text-sm text-foreground outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/20"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-accent px-5 text-sm font-semibold text-slate-950 transition hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <ArrowRight className="h-4 w-4" aria-hidden="true" />}
            Analyze Repository
          </button>
        </div>
      </form>
      <div className="mt-4 flex flex-wrap gap-2">
        {examples.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => setUrl(example)}
            className="rounded-full border border-border px-3 py-1.5 text-xs text-muted transition hover:border-accent/70 hover:text-foreground"
          >
            {example.replace("https://github.com/", "")}
          </button>
        ))}
      </div>
      {error ? <div className="mt-4"><ErrorState message={error} /></div> : null}
    </div>
  );
}
