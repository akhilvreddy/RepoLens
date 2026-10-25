import { describe, expect, it } from "vitest";

import { formatDate, formatNumber, validateGitHubUrl } from "./utils";

describe("formatNumber", () => {
  it("formats small integers without compact notation", () => {
    expect(formatNumber(42)).toBe("42");
    expect(formatNumber(9999)).toBe("9,999");
  });

  it("uses compact notation for large values", () => {
    expect(formatNumber(10_000)).toMatch(/10K|10,000/);
  });
});

describe("formatDate", () => {
  it('returns "Unknown" for empty input', () => {
    expect(formatDate(null)).toBe("Unknown");
    expect(formatDate(undefined)).toBe("Unknown");
  });

  it("formats ISO dates", () => {
    expect(formatDate("2024-06-15T12:00:00Z")).toMatch(/Jun 15, 2024/);
  });
});

describe("validateGitHubUrl", () => {
  it("accepts standard github.com owner/repo URLs", () => {
    expect(validateGitHubUrl("https://github.com/octocat/Hello-World")).toBe(true);
    expect(validateGitHubUrl("http://github.com/foo/bar/")).toBe(true);
  });

  it("rejects non-GitHub or incomplete paths", () => {
    expect(validateGitHubUrl("https://gitlab.com/foo/bar")).toBe(false);
    expect(validateGitHubUrl("https://github.com/octocat")).toBe(false);
    expect(validateGitHubUrl("not-a-url")).toBe(false);
  });
});
