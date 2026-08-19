import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { RepositorySearch } from "@/components/repository-search";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

describe("RepositorySearch", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows validation error for invalid GitHub URL", async () => {
    const user = userEvent.setup();
    render(<RepositorySearch />);

    await user.type(screen.getByLabelText("GitHub repository URL"), "not-a-url");
    await user.click(screen.getByRole("button", { name: "Analyze Repository" }));

    expect(screen.getByText("Enter a public GitHub repository URL like https://github.com/fastapi/fastapi.")).toBeInTheDocument();
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("navigates to analyze route for valid URL", async () => {
    const user = userEvent.setup();

    render(<RepositorySearch />);

    await user.type(screen.getByLabelText("GitHub repository URL"), "https://github.com/fastapi/fastapi");
    await user.click(screen.getByRole("button", { name: "Analyze Repository" }));

    expect(pushMock).toHaveBeenCalledWith("/analyze?url=https%3A%2F%2Fgithub.com%2Ffastapi%2Ffastapi");
  });

  it("navigates using example repository value", async () => {
    const user = userEvent.setup();

    render(<RepositorySearch />);

    await user.click(screen.getByRole("button", { name: "vercel/next.js" }));
    await user.click(screen.getByRole("button", { name: "Analyze Repository" }));

    expect(pushMock).toHaveBeenCalledWith("/analyze?url=https%3A%2F%2Fgithub.com%2Fvercel%2Fnext.js");
  });
});
