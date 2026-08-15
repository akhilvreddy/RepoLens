import Link from "next/link";
import { BookText, Layers, Sparkles, Zap } from "lucide-react";
import { RepositorySearch } from "@/components/repository-search";
import type { ReactNode } from "react";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col gap-8 px-4 pb-16 pt-10 sm:px-6 lg:px-8">
      <section className="rounded-lg border border-border bg-gradient-to-br from-[#171b23] to-[#202632] p-8 shadow-soft">
        <p className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">RepoLens • Private repository intelligence</p>
        <h1 className="mt-4 max-w-3xl text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Understand any GitHub repository in minutes.
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-muted">
          RepoLens combines GitHub analytics with grounded AI insights to help engineers evaluate, explore, and onboard unfamiliar codebases.
        </p>
      </section>

      <RepositorySearch />

      <section className="rounded-lg border border-border bg-surface p-6 shadow-soft">
        <h2 className="text-lg font-semibold text-foreground">What RepoLens analyzes</h2>
        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Feature title="Repository signals" icon={<BookText className="h-4 w-4" />} items={["Metadata, stars, forks, watchers", "Languages and dependencies", "CI, docs, and test detection"]} />
          <Feature title="Engineering metrics" icon={<Layers className="h-4 w-4" />} items={["Commit momentum", "Contributor concentration", "Issue & PR staleness", "Release health and activity"]} />
          <Feature title="AI-guided interpretation" icon={<Sparkles className="h-4 w-4" />} items={["Deterministic data first", "Structured AI overview", "Source-grounded repository chat"]} />
          <Feature title="Stateless flow" icon={<Zap className="h-4 w-4" />} items={["Fresh analysis per request", "No server-side cache", "Request-scoped repository chunking"]} />
        </div>
      </section>

      <p className="text-xs text-muted">
        Want to jump straight to the dashboard? Use{" "}
        <Link href="/repositories/fastapi/fastapi" className="text-accent underline underline-offset-2">
          /repositories/fastapi/fastapi
        </Link>
        .
      </p>
    </main>
  );
}

function Feature({ title, icon, items }: { title: string; icon: ReactNode; items: string[] }) {
  return (
    <div className="rounded-md border border-border bg-background p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
        {icon}
        {title}
      </div>
      <ul className="space-y-2 text-sm text-muted">
        {items.map((item) => (
          <li key={item} className="list-disc pl-4">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
