import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AnalyzePage from "@/app/analyze/page";
import { analyzeRepository } from "@/lib/api";

const pushMock = vi.fn();
const replaceMock = vi.fn();
let currentUrl = "https://github.com/fastapi/fastapi";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
    replace: replaceMock,
  }),
  useSearchParams: () => ({
    get: (key: string) => (key === "url" ? currentUrl : null),
  }),
}));

vi.mock("@/lib/api", () => ({
  analyzeRepository: vi.fn(),
}));

describe("AnalyzePage", () => {
  beforeEach(() => {
    currentUrl = "https://github.com/fastapi/fastapi";
    vi.clearAllMocks();
  });

  it("runs analysis and redirects to dashboard", async () => {
    vi.mocked(analyzeRepository).mockResolvedValue({
      repository: { owner: "fastapi", name: "fastapi" },
    } as any);

    render(<AnalyzePage />);

    await waitFor(() => expect(analyzeRepository).toHaveBeenCalledWith(currentUrl, false, expect.any(Object)));
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith("/repositories/fastapi/fastapi"));
  });

  it("shows clear centered error and retries", async () => {
    const user = userEvent.setup();
    currentUrl = "invalid-url";

    render(<AnalyzePage />);

    expect(await screen.findByText("Invalid GitHub URL. Please go back and enter a public repository URL.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Retry analysis" }));

    expect(analyzeRepository).not.toHaveBeenCalled();
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("cancels and navigates back home", async () => {
    const user = userEvent.setup();
    vi.mocked(analyzeRepository).mockImplementation(() => new Promise(() => {}) as never);

    render(<AnalyzePage />);

    await waitFor(() => expect(analyzeRepository).toHaveBeenCalled());
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(pushMock).toHaveBeenCalledWith("/");
  });
});
