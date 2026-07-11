"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { MetricsPayload } from "@/lib/types";

export function ActivityChart({ metrics }: { metrics: MetricsPayload }) {
  const data = [
    { name: "Previous 30d", commits: metrics.commits_previous_30_days },
    { name: "Last 30d", commits: metrics.commits_last_30_days },
  ];
  return (
    <div className="h-64 rounded-lg border border-border bg-surface p-4">
      <h3 className="mb-4 text-sm font-semibold text-foreground">Commit Activity</h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data}>
          <CartesianGrid stroke="#313846" vertical={false} />
          <XAxis dataKey="name" stroke="#9aa4b2" fontSize={12} />
          <YAxis stroke="#9aa4b2" fontSize={12} allowDecimals={false} />
          <Tooltip contentStyle={{ background: "#171b23", border: "1px solid #313846", borderRadius: 6 }} />
          <Bar dataKey="commits" fill="#61d394" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
