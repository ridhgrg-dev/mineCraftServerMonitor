import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import Home from "../app/page";
import ErrorBoundary from "../app/error";
import NotFound from "../app/not-found";
import Loading from "../app/loading";
afterEach(cleanup);
describe("foundation shell", () => {
  it("explains empty state without invented statistics", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { name: "Your workspace starts here" }),
    ).toBeVisible();
    expect(
      screen.getByRole("link", { name: /Check system health/ }),
    ).toHaveAttribute("href", "/system");
  });
  it("allows retry after an error", () => {
    const reset = vi.fn();
    render(<ErrorBoundary error={new Error("private detail")} reset={reset} />);
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(reset).toHaveBeenCalledOnce();
    expect(screen.queryByText("private detail")).toBeNull();
  });
  it("provides a route home on 404", () => {
    render(<NotFound />);
    expect(
      screen.getByRole("link", { name: "Return to workspace" }),
    ).toHaveAttribute("href", "/");
  });
  it("announces loading", () => {
    render(<Loading />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading workspace");
  });
});
