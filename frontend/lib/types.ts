export type MetricStatus = "healthy" | "warning" | "risk" | "unknown";

export type RepositoryMetric = {
  name: string;
  value: number | string | boolean | null;
  display_value: string;
  status: MetricStatus;
  explanation: string;
};

export type HealthScores = {
  overall: number;
  activity: number;
  maintenance: number;
  contributor: number;
  issue_health: number;
  release: number;
  documentation: number;
  engineering_maturity: number;
};

export type MetricsPayload = {
  scores: HealthScores;
  metrics: RepositoryMetric[];
  commits_last_30_days: number;
  commits_previous_30_days: number;
  commit_momentum_percentage: number | null;
  active_contributors: number;
  top_contributor_share: number | null;
  open_issues: number;
  stale_issues: number;
  median_issue_age_days: number | null;
  open_pull_requests: number;
  stale_pull_requests: number;
  has_ci: boolean;
  has_tests: boolean;
  has_documentation: boolean;
  has_dependency_files: boolean;
};

export type RepositorySummary = {
  owner: string;
  name: string;
  full_name: string;
  description: string | null;
  github_url: string;
  homepage_url: string | null;
  default_branch: string | null;
  created_at: string | null;
  updated_at: string | null;
  pushed_at: string | null;
  stars: number;
  forks: number;
  watchers: number;
  open_issues_count: number;
  primary_language: string | null;
  languages: Record<string, number>;
  license: string | null;
  topics: string[];
  size: number;
  archived: boolean;
};

export type CommitSummary = { sha: string; message: string; author: string | null; date: string | null; url: string | null };
export type ContributorSummary = { login: string; avatar_url: string | null; html_url: string | null; contributions: number };
export type IssueSummary = { number: number; title: string; html_url: string; created_at: string | null; updated_at: string | null; labels: string[] };
export type PullRequestSummary = { number: number; title: string; html_url: string; created_at: string | null; updated_at: string | null };
export type ReleaseSummary = { name: string | null; tag_name: string; html_url: string | null; published_at: string | null };
export type RepositoryFileSummary = { path: string; type: string; size: number | null };

export type TechnologyDetection = {
  frameworks: string[];
  package_managers: string[];
  dependency_files: string[];
  infrastructure: string[];
  ci_cd: string[];
  testing_tools: string[];
};

export type AIOverview = {
  summary: string;
  purpose: string;
  architecture: string;
  technologies: string[];
  strengths: string[];
  risks: string[];
  recommendations: string[];
  onboarding_steps: string[];
};

export type RepositoryAnalysis = {
  repository: RepositorySummary;
  metrics: MetricsPayload;
  ai_overview: AIOverview;
  recent_commits: CommitSummary[];
  contributors: ContributorSummary[];
  open_issues: IssueSummary[];
  open_pull_requests: PullRequestSummary[];
  releases: ReleaseSummary[];
  tree: RepositoryFileSummary[];
  readme: string | null;
  important_files: Record<string, string>;
  technologies: TechnologyDetection;
  analyzed_at: string;
  expires_at: string;
  cached: boolean;
};

export type ChatResponse = {
  answer: string;
  sources: { path: string; start_line: number; end_line: number }[];
  confidence: "high" | "medium" | "low";
  session_id: number;
};
