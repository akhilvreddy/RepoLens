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
    vi.mocked(analyzeRepository)
      .mockRejectedValueOnce(new Error("Request failed with 404"))
      .mockResolvedValueOnce({
        repository: { owner: "fastapi", name: "fastapi" },
      } as any);

    render(<AnalyzePage />);

    expect(await screen.findByText("Repository not found. Confirm the URL and that it is public.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Retry analysis" }));

    await waitFor(() => expect(analyzeRepository).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith("/repositories/fastapi/fastapi"));
  });

  it("cancels and navigates back home", async () => {
    const user = userEvent.setup();
    vi.mocked(analyzeRepository).mockImplementation(() => new Promise(() => {}) as never);

    render(<AnalyzePage />);

    await waitFor(() => expect(analyzeRepository).toHaveBeenCalledTimes(1));
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(pushMock).toHaveBeenCalledWith("/");
  });
});
