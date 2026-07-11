"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const colors = ["#61d394", "#70a7ff", "#f0b85a", "#ef6f6c", "#b9a7ff", "#67d8ef"];

export function LanguageChart({ languages }: { languages: Record<string, number> }) {
  const data = Object.entries(languages)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([name, value]) => ({ name, value }));
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <h3 className="mb-4 text-sm font-semibold text-foreground">Language Breakdown</h3>
      {data.length ? (
        <div className="grid gap-4 sm:grid-cols-[180px_1fr]">
          <div className="h-44">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data} dataKey="value" nameKey="name" innerRadius={52} outerRadius={78} paddingAngle={3}>
                  {data.map((entry, index) => <Cell key={entry.name} fill={colors[index % colors.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: "#171b23", border: "1px solid #313846", borderRadius: 6 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2">
            {data.map((entry, index) => (
              <div key={entry.name} className="flex items-center justify-between gap-3 text-sm">
                <span className="flex items-center gap-2 text-muted">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: colors[index % colors.length] }} />
                  {entry.name}
                </span>
                <span className="font-mono text-xs text-foreground">{entry.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-sm text-muted">No language data returned by GitHub.</p>
      )}
    </div>
  );
}
