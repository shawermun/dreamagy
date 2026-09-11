<div align="center">

# DREAMAGY

**Minimalist floating widget and interactive companion for Google Antigravity**

`Python 3.10+` • `PyQt5` • `Windows 10/11` • `MIT License`

[Русский](../README.md) • [English](README.en.md) • [中文](README.zh.md)

<br />

<img src="../assets/demo.gif" alt="Dreamagy Widget Demo" width="680" />

<br />
<br />

**Dreamagy** is a lightweight desktop widget that tracks real-time model quotas and reset cooldowns for **Google Antigravity** (Gemini 3.8 Flash, 3.1 Pro, Claude Sonnet/Opus).

</div>

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/High%20Voltage.png" alt="Voltage" width="28" height="28" /> Visual Effects

<div align="center">
<table>
  <tr>
    <td align="center" width="52%">
      <b>Quota Bars</b><br /><br />
      <img src="../assets/quota_bars.gif" alt="Quota Bar Animation" width="100%" /><br />
      <sub>Light sweep shimmer, floating micro-particles, and status colors</sub>
    </td>
    <td align="center" width="48%">
      <b>Companion: Elliot (Mr. Robot)</b><br /><br />
      <img src="../assets/elliot.gif" alt="Elliot Alderson Companion" width="100%" /><br />
      <sub>Live video sequence, breathing, and typing focus reactions</sub>
    </td>
  </tr>
</table>
</div>

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Alien%20Monster.png" alt="Companion" width="28" height="28" /> Interactive Companions

<div align="center">
  <img src="../assets/pets_showcase.gif" alt="Dreamagy Characters Showcase" width="680" />
</div>

Features a built-in roster of interactive companions that bring your workspace to life:
* **9 animated characters**: Elliot Alderson (*Mr. Robot*), Clippy, Tux (Linux), YoRHa 2B (*NieR:Automata*), Shigure Ui, Dario Amodei, Donald Trump, and Slavik.
* **Keystroke reactions**: companions sprint or inspect code when you type, while Elliot leans forward into hacking focus.
* **Interactive quotes**: left-clicking a companion triggers witty remarks in a glowing speech bubble.
* **Dual modes**: dock beside the widget or detach into a free-floating window with scaling (0.75x to 1.5x).

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="Features" width="28" height="28" /> Features

* **Zero configuration & no API keys**: automatically detects local Antigravity Language Server via `127.0.0.1`.
* **100% private**: no external network requests, telemetry, or remote servers.
* **Obsidian glassmorphism**: sleek semi-transparent floating pill with drag-and-drop coordinate persistence.
* **Full customization**: adjust opacity, system fonts (`Segoe UI`, `JetBrains Mono`), quota rows, and system tray menu.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Rocket.png" alt="Launch" width="28" height="28" /> Installation & Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/shawermun/dreamagy.git
cd dreamagy

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python main.py
```

> **Tip**: On Windows, simply double-click **`run.bat`**. To auto-start with Windows, place a shortcut of `run.bat` into `shell:startup`.

---

<div align="center">
<sub>MIT License • Built for developers using Google Antigravity</sub>
</div>
