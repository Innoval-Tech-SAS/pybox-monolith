import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Switch } from "@/ui/components/switch";

describe("Switch", () => {
  it("exposes role=switch and aria-checked reflecting the current state", () => {
    render(<Switch checked={true} onChange={() => {}} ariaLabel="Estado" />);
    const control = screen.getByRole("switch", { name: "Estado" });
    expect(control).toHaveAttribute("aria-checked", "true");
  });

  it("reflects checked=false via aria-checked", () => {
    render(<Switch checked={false} onChange={() => {}} ariaLabel="Estado" />);
    expect(screen.getByRole("switch", { name: "Estado" })).toHaveAttribute("aria-checked", "false");
  });

  it("calls onChange with the toggled value on click", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Switch checked={false} onChange={onChange} ariaLabel="Estado" />);

    await user.click(screen.getByRole("switch", { name: "Estado" }));

    expect(onChange).toHaveBeenCalledWith(true);
  });

  it("can be toggled from the keyboard (Space), unlike a bare <div onClick>", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Switch checked={false} onChange={onChange} ariaLabel="Estado" />);

    await user.tab();
    expect(screen.getByRole("switch", { name: "Estado" })).toHaveFocus();
    await user.keyboard(" ");

    expect(onChange).toHaveBeenCalledWith(true);
  });

  it("does not call onChange when disabled", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Switch checked={false} onChange={onChange} disabled ariaLabel="Estado" />);

    await user.click(screen.getByRole("switch", { name: "Estado" }));

    expect(onChange).not.toHaveBeenCalled();
  });

  it("falls back to `label` as the accessible name when ariaLabel is not given", () => {
    render(<Switch checked={true} onChange={() => {}} label="Activo" />);
    expect(screen.getByRole("switch", { name: "Activo" })).toBeInTheDocument();
  });
});
