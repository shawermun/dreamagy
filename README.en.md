<div align="center">

# DREAMAGY

**Minimalist Floating Quota Widget and Desktop Companion for Google Antigravity**

`Python 3.10+` • `PyQt5` • `Windows` • `MIT License`

[Русский](README.md) • [English](README.en.md) • [中文](README.zh.md)

<br />

<img src="assets/demo.gif" alt="Dreamagy Widget Demo" width="680" />

<br />
<br />

**Dreamagy** is a lightweight floating desktop widget that tracks real-time model quotas and rate limits for **Google Antigravity** (Gemini 3.8 Flash, Gemini 3.1 Pro, Claude Sonnet/Opus, GPT-OSS). Inspired by [Quotty](https://github.com/confeden/Quotty) and **Mr. Robot**.

</div>

---

## Visual Effects and Animations

<div align="center">
<table>
  <tr>
    <td align="center" width="55%">
      <b>Quota Bar</b><br /><br />
      <img src="assets/quota_bars.gif" alt="Quota Bar Animation" width="100%" /><br />
      <sub>Light sweep shimmer, floating particles, and status colors</sub>
    </td>
    <td align="center" width="45%">
      <b>Companion: Elliot Alderson</b><br /><br />
      <img src="assets/elliot.gif" alt="Elliot Alderson Companion" width="100%" /><br />
      <sub>Live video sequence, breathing, click reactions, and typing focus</sub>
    </td>
  </tr>
</table>
</div>

### Quota Bar
- **Shimmer Light Sweep**: A soft light wave glides across the progress bar track.
- **Floating Particles**: Luminous micro-bubbles gently drift inside the filled portion of the capsule.
- **Color Indicators**:
  - `> 40%` - Green (`#34d399`): Healthy quota reserve.
  - `15% - 40%` - Amber (`#f59e0b`): Moderate consumption warning.
  - `< 15%` - Red (`#ef4444`): Critical quota level.
- **Reset Timers**: Clean countdowns for weekly renewal (Mondays) and rolling 5-hour windows.

### Interactive Companion: Elliot Alderson
- **Live Video Animation**: Real Elliot sequence from Mr. Robot with fluid motion, head turns, and natural breathing.
- **Typing Focus**: Global keystroke detection (`GetAsyncKeyState`) shifts Elliot into a concentrated hacking posture while you write code.
- **Click Interactions**: Clicking the character triggers responsive posture changes or classic fsociety quotes like `"hello, friend."`.
- **Docked and Detached Modes**: Keep Elliot docked to the quota pill or detach him into an independent floating window (scale 0.75x, 1.0x, 1.25x, 1.5x).
- **Custom Companions**: Load any custom avatar or image directly through the right-click menu.

### Adding Your Own Pet
Not a fan of Elliot? You can use any character you want:
- **Static image**: Drop a PNG, JPG, or WebP file into the `assets/pets/` folder and select it via right-click -> "Change Pet".
- **Live animation**: Create a subfolder inside `assets/pets/` (e.g. `assets/pets/my_character/`), fill it with numbered frames (`frame_000.png`, `frame_001.png`, ...) and the app will play them as a video sequence.
- Scaling, detach mode, and all visual effects work the same for any pet.

---

## Key Features

- **Zero Config & No API Keys**: Automatically discovers the local Antigravity Language Server, grabs the CSRF token, and reads quotas via local HTTPS.
- **100% Offline & Private**: All communication happens strictly over `127.0.0.1`. No telemetry, no remote servers.
- **Floating Glassmorphism UI**: Dark semi-transparent pill that stays on top, supports free drag-and-drop, and saves coordinates automatically.
- **Settings Dialog**:
  - **Appearance**: Custom background and quota threshold colors.
  - **Typography**: Select system fonts (`Segoe UI`, `JetBrains Mono`, etc.) and font size.
  - **Animations**: Independent toggles for particles, shimmer, and companion motion to save resources if needed.
  - **Language**: Instant 1-click switching between Russian, English, and Chinese.
- **Configurable Quota Rows**: Switch between 2 rows, 3 rows, or custom pools (Gemini Weekly, Gemini 5h, Claude & GPT).
- **System Tray Integration**: Tray menu, minimize/hide, opacity slider (50%-100%), and 1-click center reset.

---

## Installation and Quick Start

### Requirements
- Windows 10 or 11
- Python 3.10 or newer
- Running Google Antigravity instance

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/shawermun/dreamagy.git
   cd dreamagy
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the widget:
   ```bash
   python main.py
   ```
   *Or simply double-click `run.bat`.*

### Windows Startup Setup (Optional)
1. Press `Win + R`, type `shell:startup`, and hit Enter.
2. Create a shortcut to `run.bat` and drop it into the startup folder.

---

## License

Distributed under the MIT License. See `LICENSE` for details.

<div align="center">
<sub>Inspired by Quotty and Mr. Robot. Built for developers using Google Antigravity.</sub>
</div>
