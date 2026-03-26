# Lotto 6/49 (Windows)

A small **desktop simulator** for a 6-out-of-49 style lottery: pick six distinct numbers from 1–49, draw winning numbers, and see how many match. **For entertainment only**; randomness is not cryptographically secure.

The application can be downloaded at: 
https://drive.google.com/file/d/1NhQfwME7vHmVOa1r1087RjeJG0BpAY8C/view?usp=sharing


## Requirements

- **Python 3** (3.12+ recommended; the project has been used with 3.14)
- **tkinter** (included with the standard Windows installer for Python)

No third-party packages are required to run the app.

## Run from source

```powershell
cd path\to\lotto_game
py main.py
```

Or:

```powershell
python main.py
```

## Project layout

| File | Role |
|------|------|
| `main.py` | Tkinter UI, buttons, number grid, results area |
| `lotto_logic.py` | Draw logic, validation, histograms, “random pick all tickets” simulation |

## Using the app

1. **Number grid** — Click digits to select exactly six (toggle on/off). Blue = selected; after a single draw, green = hit on the winning line.
2. **Random ticket** — Replaces the current selection with six random numbers (you can still edit on the grid).
3. **Draws** — How many rounds (1–100,000). Used by **Random pick all tickets**, **Winning number** (multi-round), and **Next round**.
4. **Draw presets** — Sets **Draws** to 1, 3, or 5 in one click.
5. **Next round / Previous round** — When **Draws** is more than 1, save one ticket per round before **Winning number** (manual or random tickets each round).
6. **Winning number** — With **Draws = 1**, one draw vs your current grid. With **Draws** greater than 1, one new winning line per saved round, with a summary histogram.
7. **Random pick all tickets** — Draws **one** fixed winning line, then **Draws** random player lines against it; lists up to 500 detail lines plus a summary (does not use your manually saved multi-round list).
8. **Clear** — Clears selection, saved rounds, and results.
9. **Results** — Shown in the scrollable text below **Winning number**.

## Build a Windows `.exe`

1. Install build tools (once):

   ```powershell
   py -m pip install -r requirements-build.txt
   ```

2. Run **`build_exe.bat`** (or `py -m PyInstaller --noconfirm --clean Lotto_6_49.spec`).

Output: **`dist\Lotto_6_49.exe`** (single file, no console window). Rebuild on the machine or Python version you want to target; 64-bit Windows is assumed.

## License

Personal / hobby project; use and modify as you like.
