"""
Lotto 6/49 — desktop UI (tkinter). Entertainment only.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from tkinter import scrolledtext

import lotto_logic as L

COL_DEFAULT = "#e8e8e8"
COL_SELECTED = "#4a7ab8"
COL_MATCH = "#2d8f47"
COL_TEXT = "#1a1a1a"

# One-click draw counts (same as spinbox "Draws")
DRAW_PRESETS = (1, 3, 5)


class LottoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Lotto 6/49")
        root.minsize(420, 640)
        root.configure(padx=12, pady=12)

        self.selected: set[int] = set()
        self.last_winning: list[int] | None = None
        # When Draws > 1: one saved ticket per round (sorted lists), built with Next round.
        self.round_tickets: list[list[int]] = []
        self.buttons: dict[int, tk.Button] = {}

        title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        normal_font = tkfont.Font(family="Segoe UI", size=10)
        btn_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")

        tk.Label(
            root,
            text="Pick 6 numbers (1–49) — click the grid or use Random ticket",
            font=title_font,
            fg=COL_TEXT,
        ).pack(anchor="w", pady=(0, 4))

        self.counter_var = tk.StringVar(value="Selected: 0 / 6")
        tk.Label(root, textvariable=self.counter_var, font=normal_font, fg=COL_TEXT).pack(
            anchor="w", pady=(0, 4)
        )

        self.round_status_var = tk.StringVar(value="")
        tk.Label(root, textvariable=self.round_status_var, font=normal_font, fg=COL_TEXT).pack(
            anchor="w", pady=(0, 4)
        )
        round_nav = tk.Frame(root)
        round_nav.pack(fill="x", pady=(0, 8))
        self.next_round_btn = tk.Button(
            round_nav,
            text="Next round",
            font=normal_font,
            state=tk.DISABLED,
            command=self._next_round,
        )
        self.next_round_btn.pack(side="left", padx=(0, 8))
        self.prev_round_btn = tk.Button(
            round_nav,
            text="Previous round",
            font=normal_font,
            state=tk.DISABLED,
            command=self._prev_round,
        )
        self.prev_round_btn.pack(side="left")

        grid = tk.Frame(root)
        grid.pack(fill="x", pady=(0, 12))

        for i in range(49):
            n = i + 1
            r, c = divmod(i, 7)
            b = tk.Button(
                grid,
                text=str(n),
                width=4,
                height=1,
                font=btn_font,
                relief=tk.RAISED,
                bg=COL_DEFAULT,
                fg=COL_TEXT,
                activebackground=COL_SELECTED,
                command=lambda x=n: self._toggle(x),
            )
            b.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            self.buttons[n] = b

        for c in range(7):
            grid.columnconfigure(c, weight=1)

        pick_bar = tk.Frame(root)
        pick_bar.pack(fill="x", pady=(0, 8))
        tk.Button(
            pick_bar,
            text="Random ticket",
            font=normal_font,
            command=self._random_ticket,
        ).pack(side="left", padx=(0, 10))
        tk.Label(
            pick_bar,
            text="Fills 6 random numbers (replaces your current selection).",
            font=normal_font,
            fg=COL_TEXT,
        ).pack(side="left")

        ctrl = tk.Frame(root)
        ctrl.pack(fill="x", pady=(0, 4))

        tk.Button(ctrl, text="Random pick all tickets", font=normal_font, command=self._quick_pick).pack(
            side="left", padx=(0, 8)
        )
        tk.Button(ctrl, text="Clear", font=normal_font, command=self._clear).pack(side="left", padx=(0, 8))

        tk.Label(ctrl, text="Draws:", font=normal_font, fg=COL_TEXT).pack(side="left", padx=(16, 4))
        self.draw_count_var = tk.StringVar(value="1")
        self.draw_spin = tk.Spinbox(
            ctrl,
            from_=1,
            to=100_000,
            increment=1,
            width=7,
            font=normal_font,
            textvariable=self.draw_count_var,
        )
        self.draw_spin.pack(side="left", padx=(0, 8))
        self.draw_spin.bind("<FocusOut>", self._sync_draw_count_from_spin)
        self.draw_spin.bind("<Return>", self._sync_draw_count_from_spin)

        win_row = tk.Frame(root)
        win_row.pack(fill="x", pady=(0, 8))
        self.draw_btn = tk.Button(
            win_row,
            text="Winning number",
            font=normal_font,
            state=tk.DISABLED,
            command=self._draw,
        )
        self.draw_btn.pack(side="left")

        # Summary directly under Winning number
        result_frame = tk.Frame(root)
        result_frame.pack(fill="both", expand=True, pady=(0, 0))
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            height=14,
            wrap=tk.WORD,
            font=normal_font,
            fg=COL_TEXT,
            state=tk.DISABLED,
        )
        self.result_text.pack(fill="both", expand=True)

        preset_bar = tk.Frame(root)
        preset_bar.pack(fill="x", pady=(8, 0))
        tk.Label(preset_bar, text="Draw presets:", font=normal_font, fg=COL_TEXT).pack(
            side="left", padx=(0, 6)
        )
        for val in DRAW_PRESETS:
            tk.Button(
                preset_bar,
                text=str(val),
                width=4,
                font=normal_font,
                command=lambda v=val: self._apply_draw_preset(v),
            ).pack(side="left", padx=2)

        self.draw_count_var.trace_add("write", lambda *_: self.root.after_idle(self._update_counter))
        self._update_counter()

    def _read_draw_count_silent(self) -> int:
        try:
            return max(1, min(100_000, int(self.draw_spin.get().strip())))
        except ValueError:
            return 1

    def _refresh_round_navigation(self) -> None:
        n = self._read_draw_count_silent()
        if len(self.round_tickets) > n:
            self.round_tickets = self.round_tickets[:n]
        if n <= 1:
            self.round_status_var.set("")
            self.next_round_btn.config(state=tk.DISABLED)
            self.prev_round_btn.config(state=tk.DISABLED)
            return
        nt = len(self.round_tickets)
        can_next = nt < n and len(self.selected) == L.PICK_COUNT
        self.next_round_btn.config(state=tk.NORMAL if can_next else tk.DISABLED)
        self.prev_round_btn.config(state=tk.NORMAL if nt > 0 else tk.DISABLED)
        if nt >= n:
            self.round_status_var.set(
                f"All {n} tickets saved. Run Winning number."
            )
        else:
            self.round_status_var.set(
                f"Round {nt + 1} of {n}: pick 6 numbers, then Next round."
            )

    def _update_counter(self) -> None:
        self.counter_var.set(f"Selected: {len(self.selected)} / {L.PICK_COUNT}")
        n = self._read_draw_count_silent()
        if n <= 1:
            ready = tk.NORMAL if len(self.selected) == L.PICK_COUNT else tk.DISABLED
        else:
            ready = tk.NORMAL if len(self.round_tickets) == n else tk.DISABLED
        self.draw_btn.config(state=ready)
        self._refresh_round_navigation()

    def _next_round(self) -> None:
        n = self._parse_draw_count()
        if n is None or n <= 1:
            return
        if not L.validate_selection(self.selected):
            messagebox.showinfo(
                "Lotto 6/49",
                "Pick exactly 6 numbers for this round before using Next round.",
            )
            return
        if len(self.round_tickets) >= n:
            return
        self._invalidate_draw_display()
        self.round_tickets.append(sorted(self.selected))
        if len(self.round_tickets) >= n:
            self._refresh_all_styles()
            self._update_counter()
            return
        self.selected.clear()
        self._refresh_all_styles()
        self._update_counter()

    def _prev_round(self) -> None:
        n = self._read_draw_count_silent()
        if n <= 1 or not self.round_tickets:
            return
        self._invalidate_draw_display()
        self.selected = set(self.round_tickets.pop())
        self._refresh_all_styles()
        self._update_counter()

    def _write_results(self, content: str) -> None:
        t = self.result_text
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        t.insert("1.0", content)
        t.config(state=tk.DISABLED)

    def _apply_draw_preset(self, n: int) -> None:
        self.draw_count_var.set(str(n))

    @staticmethod
    def _format_hit_summary(hist: dict[int, int], n_rounds: int) -> str:
        """
        Summarize how many rounds had 0..6 numbers correct.
        Only lists categories that occurred; ends with a check that counts add up to n_rounds.
        """
        total = sum(hist.values())
        parts: list[str] = [
            f"Summary for exactly {n_rounds:,} round(s) you ran:",
        ]
        for k in range(7):
            c = hist[k]
            if c:
                parts.append(f"  {c} round(s) with {k} number(s) correct")
        if total != n_rounds:
            parts.append(f"  (internal check failed: {total} != {n_rounds})")
        else:
            parts.append(f"  Total counted rounds: {total:,} (matches your draw count)")
        return "\n".join(parts)

    def _style_button(self, n: int) -> None:
        b = self.buttons[n]
        if self.last_winning is not None and n in self.selected and n in self.last_winning:
            b.config(bg=COL_MATCH, activebackground=COL_MATCH)
        elif n in self.selected:
            b.config(bg=COL_SELECTED, activebackground=COL_SELECTED)
        else:
            b.config(bg=COL_DEFAULT, activebackground=COL_SELECTED)

    def _refresh_all_styles(self) -> None:
        for n in range(L.POOL_MIN, L.POOL_MAX + 1):
            self._style_button(n)

    def _invalidate_draw_display(self) -> None:
        if self.last_winning is None:
            return
        self.last_winning = None
        self._write_results("")
        self._refresh_all_styles()

    def _random_ticket(self) -> None:
        """Replace current selection with six random distinct numbers (manual pick still works on the grid)."""
        self._invalidate_draw_display()
        self.selected = set(L.quick_pick())
        self._refresh_all_styles()
        self._update_counter()

    def _toggle(self, n: int) -> None:
        self._invalidate_draw_display()
        if n in self.selected:
            self.selected.remove(n)
        else:
            if len(self.selected) >= L.PICK_COUNT:
                messagebox.showinfo("Lotto 6/49", "You can only select 6 numbers.")
                return
            self.selected.add(n)
        self._style_button(n)
        self._update_counter()

    def _quick_pick(self) -> None:
        n = self._parse_draw_count()
        if n is None:
            return

        winning, last_ticket, detail_lines, hist, truncated = L.quick_pick_rounds_fixed_winning(
            n, max_listed=500
        )
        self.selected = set(last_ticket)
        self.last_winning = list(winning)

        w_str = ", ".join(str(x) for x in winning)
        if n == 1:
            m = L.matches(last_ticket, winning)
            t_str = ", ".join(str(x) for x in last_ticket)
            self._write_results(
                f"Fixed winning numbers: {w_str}\n"
                f"Your random ticket: {t_str}\n"
                f"Matches: {m} / {L.PICK_COUNT}"
            )
        else:
            omit_note = ""
            if truncated:
                omit_note = (
                    f"\n… ({n - len(detail_lines):,} more rounds not listed; "
                    f"summary counts every one of your {n:,} rounds.)\n"
                )
            body = (
                f"Random pick all tickets — {n:,} random tickets vs the same winning line:\n{w_str}\n\n"
                + "\n"
                + self._format_hit_summary(hist, n)
                + "\n"
                + "\n"
                + "\n".join(detail_lines)
                + "\n"
                + omit_note
                + "\n"
                + "\n\n(Grid shows the last random ticket vs the fixed winning line.)"
            )
            self._write_results(body)

        self._refresh_all_styles()
        self._update_counter()

    def _clear(self) -> None:
        self.last_winning = None
        self.round_tickets.clear()
        self.selected.clear()
        self._write_results("")
        self._refresh_all_styles()
        self._update_counter()

    def _sync_draw_count_from_spin(self, _event: object | None = None) -> None:
        """Clamp spinbox text to 1..100000 and write back so display matches parsed value."""
        raw = self.draw_spin.get().strip()
        try:
            n = int(raw)
        except ValueError:
            self.draw_count_var.set("1")
            return
        n = max(1, min(100_000, n))
        self.draw_count_var.set(str(n))
        self._update_counter()

    def _parse_draw_count(self) -> int | None:
        # Read from the widget: typed values may not yet be synced to StringVar until focus leaves.
        raw = self.draw_spin.get().strip()
        try:
            n = int(raw)
        except ValueError:
            messagebox.showinfo("Lotto 6/49", "Enter a whole number for the number of draws.")
            return None
        if n < 1:
            messagebox.showinfo("Lotto 6/49", "Number of draws must be at least 1.")
            return None
        if n > 100_000:
            messagebox.showinfo("Lotto 6/49", "Maximum number of draws is 100,000.")
            return None
        self.draw_count_var.set(str(n))
        return n

    def _draw(self) -> None:
        n = self._parse_draw_count()
        if n is None:
            return

        if n == 1:
            self.round_tickets.clear()
            if not L.validate_selection(self.selected):
                messagebox.showinfo("Lotto 6/49", "Pick exactly 6 distinct numbers from 1–49.")
                return
            winning = L.draw_winning()
            self.last_winning = winning
            m = L.matches(self.selected, winning)
            w_str = ", ".join(str(x) for x in winning)
            self._write_results(f"Winning numbers: {w_str}\nYou matched: {m} / {L.PICK_COUNT}")
        else:
            if len(self.round_tickets) != n:
                messagebox.showinfo(
                    "Lotto 6/49",
                    f"You set {n} draws. Use \"Next round\" after each ticket until all {n} are saved "
                    f"(currently {len(self.round_tickets)} saved).",
                )
                return
            self.last_winning = None
            hist = L.simulate_histogram_for_tickets(self.round_tickets)
            self._write_results(
                f"Simulated {n:,} draws — a different winning line per round, your ticket for that round.\n\n"
                + self._format_hit_summary(hist, n)
            )

        self._refresh_all_styles()

def main() -> None:
    root = tk.Tk()
    LottoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
