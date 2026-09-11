<div align="center">

# DREAMAGY

**Minimalist Floating Quota Widget and Desktop Companion for Google Antigravity**

`Python 3.10+` • `PyQt5` • `Windows` • `MIT License`

[Русский](README.md) • [English](README.en.md) • [中文](README.zh.md)

<br />

<img src="assets/demo.gif" alt="Dreamagy Widget Demo" width="680" />

<br />
<br />

**Dreamagy** is a lightweight floating desktop widget that tracks real-time model quotas and rate limits for **Google Antigravity** (Gemini 3.8 Flash, Gemini 3.1 Pro, Claude Sonnet/Opus, GPT-OSS).

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

### 🐾 Interactive Companions & Pets Roster

<div align="center">
  <img src="assets/pets_showcase.gif" alt="Dreamagy Characters Showcase" width="680" />
  <br />
  <sub>⚡ Interactive companion showcase: Elliot Alderson live video and animated Codex 8×9 sprite atlases</sub>
</div>

<br />

Dreamagy features a diverse collection of **9 animated desktop companions**, each with unique character traits, typing reactions, speech quotes, and behaviors:

| Companion | Description & Personality | Animations & States |
| :--- | :--- | :--- |
| 🎬 **Elliot Alderson** | Protagonist of *Mr. Robot*, fsociety hacker. | Live video sequence, breathing, concentrated hacking focus while typing, glitch effects, and quotes like *“hello, friend.”*. |
| 📎 **Clippy (Paperclip)** | Nostalgic Microsoft Office assistant perched on a paper notepad. | Friendly hand-wave, running with papers, jumps, idle glances, and coding tips. |
| 🐧 **Tux (Linux Penguin)** | Legendary mascot of Linux and server compilation. | Waddling run, waving, calm idle, and reminders like `sudo make install`. |
| ⚔️ **YoRHa 2B** | Chibi battle android from *NieR:Automata* with hovering Emil head. | Pod floating, jumps, contemplative seated idle, and philosophical observations. |
| 🐱 **Shigure Ui (Nyako)** | Cute anime mascot wearing cyber cat-ear headphones. | Bouncing jumps, cheerful waves, idle tail swish, and the iconic *“Ui-beam!”*. |
| 👔 **Dario Amodei** | CEO of Anthropic and architect of the Claude family of models. | Code reviews, steady posture, and quotes on *Scaling Laws* and *Claude 3.7*. |
| 📢 **Yelling Dario** | High-energy Dario urgently demanding more compute power. | Charging run, dynamic hand gestures, and shouts of *“MORE COMPUTE!”*. |
| 👱 **Donald Trump** | Expressive animated pixel Trump with iconic golden hair. | Animated marching, expressive gesturing, and *“Make Code Great Again!”*. |
| 🧢 **Slavik** | Charismatic street hacker in a tracksuit and cap. | Squatting stance, brisk sprint, and strict quota monitoring. |

- **Codex 8×9 Sprite Atlas Support**: Full compatibility with `pet-companion` and `vscode-pets` standards — animated states including idle, running, jumping, waiting, review, and waving.
- **One-Click Online Catalog**: Download and activate extra companions directly from the context menu without manual file handling.
- **Mr. Robot Live Video**: Fluid sequence featuring genuine facial expressions, natural breathing, and micro-movements.
- **Keystroke Activity Reactions**: Typing code immediately triggers companions to run or review, while Elliot leans forward into terminal hacking focus.
- **Interactive Speech Bubbles**: Left-clicking a companion triggers a greeting, wave, or witty quote in a glowing neon pill.
- **Docked & Floating Windows**: Dock seamlessly beside the quota capsule or detach into an independent floating companion (scales 0.75x, 1.0x, 1.25x, 1.5x).

### Adding Your Own Pet
- **Codex 8×9 Sprite Atlas**: Place a folder with `pet.json` and `spritesheet.webp` (or `.png`) in `assets/pets/` — Dreamagy automatically detects all states and animations.
- **Image Sequence**: Place a folder with numbered frames (`frame_000.png`, `frame_001.png`, ...) for fluid video playback.
- **Static Image**: Drop any PNG/WebP into `assets/pets/` for procedural breathing, blinking, and tilting.

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
<sub>Built for developers using Google Antigravity.</sub>
</div>
