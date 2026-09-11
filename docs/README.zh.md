<div align="center">

# DREAMAGY

**适用于 Google Antigravity 的极简悬浮配额监控挂件与桌面伴侣**

`Python 3.10+` • `PyQt5` • `Windows` • `MIT License`

[Русский](README.md) • [English](README.en.md) • [中文](README.zh.md)

<br />

<img src="assets/demo.gif" alt="Dreamagy Widget Demo" width="680" />

<br />
<br />

**Dreamagy** 是一款轻量级桌面悬浮小部件，可实时精准显示 **Google Antigravity** 模型配额与速率限制（Gemini 3.8 Flash、Gemini 3.1 Pro、Claude Sonnet/Opus、GPT-OSS）。

</div>

---

## 视觉效果与动画

<div align="center">
<table>
  <tr>
    <td align="center" width="55%">
      <b>配额进度条 (Quota Bar)</b><br /><br />
      <img src="assets/quota_bars.gif" alt="Quota Bar Animation" width="100%" /><br />
      <sub>平滑扫描光束 (shimmer)、浮动发光微粒子与自适应状态色彩</sub>
    </td>
    <td align="center" width="45%">
      <b>桌面伴侣：埃利奥特·奥尔德森</b><br /><br />
      <img src="assets/elliot.gif" alt="Elliot Alderson Companion" width="100%" /><br />
      <sub>真实视频动画序列、呼吸、摇头思考及键盘打字交互</sub>
    </td>
  </tr>
</table>
</div>

### 动态配额进度条 (Quota Bar)
- **平滑扫描光束 (Shimmer)**: 带有柔和渐变的高光波束定期掠过已填充的进度条区域。
- **发光微粒子 (Particles)**: 遵循物理特性的微粒子与气泡在胶囊轨道内部平滑游弋。
- **色彩分级**:
  - `> 40%` - 翡翠绿 (`#34d399`): 配额充裕。
  - `15% - 40%` - 琥珀黄 (`#f59e0b`): 中度消耗警告。
  - `< 15%` - 珊瑚红 (`#ef4444`): 配额临界告急。
- **重置倒计时**: 动态显示配额恢复时间（每周一重置的周配额及 5 小时滚动窗口）。

### 🐾 互动桌面伴侣与角色阵容

<div align="center">
  <img src="assets/pets_showcase.gif" alt="Dreamagy Characters Showcase" width="680" />
  <br />
  <sub>⚡ 互动伴侣展示：埃利奥特实时视频与 Codex 8×9 像素精灵动画图集</sub>
</div>

<br />

Dreamagy 现已提供包含 **9 款独具特色** 的桌面互动伴侣，每位角色都具备专属的动作状态、键盘交互、气泡语录与个性行为：

| 伴侣角色 | 描述与个性 | 动画与行为状态 |
| :--- | :--- | :--- |
| 🎬 **Elliot Alderson** | 《黑客军团》(Mr. Robot) 主角，fsociety 核心黑客。 | 真实视频序列播放、呼吸起伏、代码输入时的黑客前倾专注姿态、故障抖动与经典台词 *“hello, friend.”*。 |
| 📎 **Clippy (回形针助手)** | 微软 Office 经典回形针助手，立于便签纸之上。 | 热情招手、携带文件奔跑、跳跃、驻足思考以及趣味编程提示。 |
| 🐧 **Tux (Linux 企鹅)** | 传奇的 Linux 官方吉祥物，稳健与开源的象征。 | 摇摆小跑、挥翅致意、安坐沉思，并提醒你 `sudo make install`。 |
| ⚔️ **YoRHa 2B** | 尼尔:机械纪元 (NieR:Automata) 战斗人形 2B 与悬浮埃米尔。 | 悬浮 Pod 伴飞、轻盈跳跃、静坐冥想与充满哲理的情感独白。 |
| 🐱 **Shigure Ui (Nyako)** | 佩戴猫耳耳机的二次元可爱萌系吉祥物。 | 欢快弹跳、挥手问候、萌系摇摆与招牌必杀技 *“Ui-beam!”*。 |
| 👔 **Dario Amodei** | Anthropic 首席执行官兼 Claude 系列模型总架构师。 | 代码审查模式、沉稳姿态以及关于 *Scaling Laws* 与 *Claude 3.7* 的箴言。 |
| 📢 **Yelling Dario** | 充满激情的能量版 Dario，极度渴望更多计算算力。 | 疾速冲刺、夸张手势与标志性呼喊 *“MORE COMPUTE!”*。 |
| 👱 **Donald Trump** | 神态生动的像素风格特朗普，标志性金发造型。 | 节奏行进、丰富肢体语言与口号 *“Make Code Great Again!”*。 |
| 🧢 **Slavik** | 穿着运动服、头戴棒球帽的个性街头黑客。 | 霸气蹲姿、疾步奔跑与全天候严谨监控配额剩余。 |

- **Codex 8×9 精灵图集 (Sprite Atlas) 兼容**: 深度适配 `pet-companion` 与 `vscode-pets` 标准，支持静止、奔跑、跳跃、等待、代码审查与挥手等多种动态状态。
- **一键在线目录下载**: 直接通过右键上下文菜单快速在线下载并激活新伴侣，告别繁琐的文件解压与手动配置。
- **Mr. Robot 真实视频动画**: 细腻还原剧中面部表情与自然呼吸起伏。
- **键盘打字全局联动**: 当你在 IDE 中敲击代码时，伴侣会同步进入奔跑或审查状态，埃利奥特则自动进入黑客前倾对焦模式。
- **互动点击与发光对话气泡 (Speech Bubble)**: 鼠标左键轻点角色即可触发问候、动作反馈或幽默语录。
- **停靠与独立双模式 (Docked & Detached)**: 可吸附于配额胶囊旁，亦可脱离为自由移动的独立置顶小窗（支持 0.75x、1.0x、1.25x、1.5x 四档缩放）。

### 添加自定义宠物
- **Codex 8×9 精灵图集**: 将包含 `pet.json` 与 `spritesheet.webp`（或 `.png`）的文件夹放入 `assets/pets/`，软件将自动识别其全部动作。
- **连续图像序列**: 在子文件夹中放入连续编号的帧图像（`frame_000.png`、`frame_001.png` 等），即可以视频形式流畅循环播放。
- **静态图像**: 放置单张 PNG/WebP 图片，即可自动获得程序生成的呼吸与眨眼微动效果。

---

## 核心特性

- **免配置与无需 API 密钥**: 自动定位本地运行的 Antigravity 语言服务进程，提取 CSRF 令牌，通过本地 HTTPS Connect RPC 协议读取配额。
- **100% 离线与隐私保护**: 所有请求均严格限定于本地地址 `127.0.0.1`。无任何外部服务器通信或遥测上报。
- **暗色毛玻璃悬浮界面 (Dark Glassmorphism)**: 磨砂黑曜石胶囊设计，置顶显示 (`Always on Top`)，支持平滑拖拽并在重启后自动恢复坐标。
- **完整设置面板 (Settings Dialog)**:
  - **外观**: 自定义窗口背景色及各区间配额警示色。
  - **排版**: 自定义字体族（`Segoe UI`、`JetBrains Mono` 等）及字号大小。
  - **动画**: 粒子、扫光光束与角色动作的独立开关控制。
  - **语言**: 俄语 (RU)、英语 (EN)、中文 (ZH) 一键即时切换。
- **灵活的配额行显示**: 支持在 2 行、3 行或自定义模型池（Gemini Weekly、Gemini 5h、Claude & GPT）间切换。
- **Windows 系统托盘集成**: 托盘快捷菜单、最小化显示、透明度调节（50%-100%）及一键屏幕居中复位。

---

## 安装与启动

### 环境要求
- Windows 10 或 Windows 11
- Python 3.10 或更高版本
- 已安装并正在运行的 Google Antigravity

### 快速启动

1. 克隆代码仓库:
   ```bash
   git clone https://github.com/shawermun/dreamagy.git
   cd dreamagy
   ```

2. 安装依赖项:
   ```bash
   pip install -r requirements.txt
   ```

3. 运行程序:
   ```bash
   python main.py
   ```
   *或直接双击运行 `run.bat` 脚本。*

### Windows 开机自启设置 (可选)
1. 按下 `Win + R` 键，输入 `shell:startup` 并回车。
2. 为 `run.bat` 创建快捷方式，将其放入打开的启动文件夹即可。

---

## 许可证

本项目遵循 MIT License 开源许可协议。详情请参阅 `LICENSE` 文件。

<div align="center">
<sub>专为 Google Antigravity 开发者打造。</sub>
</div>
