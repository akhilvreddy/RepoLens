"use client";

import { FormEvent, useState } from "react";
import { Bot, Loader2, Send, User } from "lucide-react";
import { askRepository } from "@/lib/api";
import type { ChatResponse } from "@/lib/types";

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: ChatResponse["sources"];
};

const starters = [
  "What does this repository do?",
  "Is this repository actively maintained?",
  "Where should a new contributor start?",
  "What are the biggest maintenance risks?",
];

export function RepositoryChat({ owner, repo }: { owner: string; repo: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [sessionId, setSessionId] = useState<number | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(nextQuestion = question) {
    const cleanQuestion = nextQuestion.trim();
    if (!cleanQuestion) return;
    setQuestion("");
    setError(null);
    setMessages((current) => [...current, { role: "user", content: cleanQuestion }]);
    setIsLoading(true);
    try {
      const response = await askRepository(owner, repo, cleanQuestion, sessionId);
      setSessionId(response.session_id);
      setMessages((current) => [...current, { role: "assistant", content: response.answer, sources: response.sources }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submit();
  }

  return (
    <section className="rounded-lg border border-border bg-surface p-4 shadow-soft">
      <div className="mb-4 flex items-center gap-2">
        <Bot className="h-5 w-5 text-accent" aria-hidden="true" />
        <h2 className="text-lg font-semibold text-foreground">Repository Chat</h2>
      </div>
      <div className="mb-4 flex flex-wrap gap-2">
        {starters.map((starter) => (
          <button key={starter} onClick={() => void submit(starter)} disabled={isLoading} className="rounded-full border border-border px-3 py-1.5 text-xs text-muted transition hover:border-accent/70 hover:text-foreground">
            {starter}
          </button>
        ))}
      </div>
      <div className="min-h-52 space-y-3 rounded-md border border-border bg-background p-3">
        {messages.length === 0 ? <p className="text-sm text-muted">Ask a grounded question about README, files, activity, issues, or metrics.</p> : null}
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className="flex gap-3 rounded-md bg-surface p-3">
            {message.role === "user" ? <User className="mt-0.5 h-4 w-4 text-muted" /> : <Bot className="mt-0.5 h-4 w-4 text-accent" />}
            <div className="min-w-0 flex-1">
              <p className="whitespace-pre-wrap text-sm leading-6 text-foreground">{message.content}</p>
              {message.sources?.length ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  {message.sources.map((source) => (
                    <span key={`${source.path}-${source.start_line}`} className="rounded-md border border-border bg-background px-2 py-1 font-mono text-xs text-muted">
                      {source.path}:{source.start_line}-{source.end_line}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          </div>
        ))}
        {isLoading ? <div className="flex items-center gap-2 text-sm text-muted"><Loader2 className="h-4 w-4 animate-spin" /> Thinking from indexed repository context</div> : null}
      </div>
      {error ? <p className="mt-3 text-sm text-danger">{error}</p> : null}
      <form onSubmit={onSubmit} className="mt-4 flex gap-2">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about architecture, stack, maintenance, or onboarding"
          className="h-11 flex-1 rounded-md border border-border bg-background px-3 text-sm text-foreground outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
        <button type="submit" disabled={isLoading} className="inline-flex h-11 items-center justify-center rounded-md bg-accent px-4 text-slate-950 transition hover:bg-accent/90 disabled:opacity-60" aria-label="Send question">
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </form>
    </section>
  );
}
