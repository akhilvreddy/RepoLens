import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { RepositorySearch } from "@/components/repository-search";
import { analyzeRepository } from "@/lib/api";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

vi.mock("@/lib/api", () => ({
  analyzeRepository: vi.fn(),
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
    expect(analyzeRepository).not.toHaveBeenCalled();
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("navigates to repository page after successful analysis", async () => {
    const user = userEvent.setup();
    vi.mocked(analyzeRepository).mockResolvedValue({
      repository: { owner: "fastapi", name: "fastapi" },
    } as any);

    render(<RepositorySearch />);

    await user.type(screen.getByLabelText("GitHub repository URL"), "https://github.com/fastapi/fastapi");
    await user.click(screen.getByRole("button", { name: "Analyze Repository" }));

    await waitFor(() => expect(analyzeRepository).toHaveBeenCalledWith("https://github.com/fastapi/fastapi"));
    await waitFor(() => expect(pushMock).toHaveBeenCalledWith("/repositories/fastapi/fastapi"));
  });

  it("shows API error message when analysis fails", async () => {
    const user = userEvent.setup();
    vi.mocked(analyzeRepository).mockRejectedValue(new Error("Repository analysis failed badly"));

    render(<RepositorySearch />);

    await user.type(screen.getByLabelText("GitHub repository URL"), "https://github.com/fastapi/fastapi");
    await user.click(screen.getByRole("button", { name: "Analyze Repository" }));

    expect(await screen.findByText("Repository analysis failed badly")).toBeInTheDocument();
    expect(pushMock).not.toHaveBeenCalled();
  });
});
