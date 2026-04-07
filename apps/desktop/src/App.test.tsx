import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renders the Step0 shell heading", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /AI Desktop Assistant/i })).toBeInTheDocument();
    expect(screen.getByText(/Step0 \/ Project Skeleton/i)).toBeInTheDocument();
  });
});

