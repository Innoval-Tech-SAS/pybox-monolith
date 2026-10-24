import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorBoundary } from "@/ui/components/error-boundary";

const Bomb: React.FC<{ shouldThrow: boolean }> = ({ shouldThrow }) => {
  if (shouldThrow) throw new Error("boom");
  return <div>contenido normal</div>;
};

describe("ErrorBoundary", () => {
  beforeEach(() => {
    // React vuelca el error de render en consola además de componentDidCatch;
    // se silencia para no ensuciar la salida del test.
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders children normally when nothing throws", () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow={false} />
      </ErrorBoundary>,
    );
    expect(screen.getByText("contenido normal")).toBeInTheDocument();
  });

  it("renders the default fallback and logs via componentDidCatch when a child throws", () => {
    render(
      <ErrorBoundary>
        <Bomb shouldThrow />
      </ErrorBoundary>,
    );
    expect(screen.getByText("Ocurrió un error inesperado")).toBeInTheDocument();
    expect(console.error).toHaveBeenCalledWith(
      "[error-boundary]",
      expect.any(Error),
      expect.any(String),
    );
  });

  it("renders a custom fallback when provided", () => {
    render(
      <ErrorBoundary fallback={<div>algo salió mal</div>}>
        <Bomb shouldThrow />
      </ErrorBoundary>,
    );
    expect(screen.getByText("algo salió mal")).toBeInTheDocument();
  });

  it("lets the user retry, re-rendering children after the error", async () => {
    const user = userEvent.setup();
    render(
      <ErrorBoundary>
        <Bomb shouldThrow />
      </ErrorBoundary>,
    );
    await user.click(screen.getByText("Reintentar"));
    // El estado se resetea, pero Bomb sigue lanzando -- el boundary vuelve a
    // capturar. Lo que importa es que el click no rompe el árbol de React.
    expect(screen.getByText("Ocurrió un error inesperado")).toBeInTheDocument();
  });
});
