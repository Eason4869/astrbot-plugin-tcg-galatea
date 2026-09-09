# 🟩 TCG工具箱

<p align="center">
  <img src="./logo.png" width="128" height="128" alt="TCG工具箱 Logo" />
</p>

<p align="center">
  <!-- Minecraft 主题浏览量 -->
  <a href="https://github.com/Eason4869/astrbot-plugin-tcg-galatea">
    <img src="https://count.getloli.com/@astrbot-plugin-tcg-galatea?theme=moebooru&no-badge=true" alt="Visitors" />
    <img src="https://komarev.com/ghpvc/?username=Eason4869.astrbot-plugin-tcg-galatea&label=%F0%9F%9F%A9%20Visitors&color=38b000&style=flat-square&labelColor=1b1b1b" alt="Minecraft Visitors" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.1.0-38b000?style=flat-square&labelColor=1b1b1b" alt="Version" />
  <img src="https://img.shields.io/badge/AstrBot-v4.0%2B-2b6cb0?style=flat-square&labelColor=1b1b1b" alt="AstrBot" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&labelColor=1b1b1b" alt="Python" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-38b000?style=flat-square&labelColor=1b1b1b" alt="License" />
  <img src="https://img.shields.io/badge/Modules-OCG%20%7C%20MD%20%7C%20DL%20%7C%20PTCG-69b34c?style=flat-square&labelColor=1b1b1b" alt="Modules" />
</p>

> 游戏王 + 宝可梦多游戏卡牌工具箱  
> 四大模块独立开关 · 统一 **「模块 + 动词」** 指令风格

---

## ✨ 模块一览

| 模块 | 开关 | 能力 |
|------|------|------|
| **OCG** | `enable_ocg` | 查卡 / 卡图 / 随机、RoTK 饼图、禁卡表与点数、卡组导入与构筑图、起手抽卡 |
| **MD** | `enable_md` | Master Duel T 表、查卡组、翻译 T 表 |
| **DL** | `enable_dl` | Duel Links T 表、查卡组、翻译 T 表 |
| **PTCG** | `enable_ptcg` | 宝可梦查卡（中/英）、序号 / 换页、卡图、随机 |

---

## ⚙️ 配置

| 配置项 | 默认 | 说明 |
|--------|------|------|
| `modules.enable_ocg` | `true` | OCG 模块 |
| `modules.enable_md` | `true` | MD 模块 |
| `modules.enable_dl` | `true` | DL 模块 |
| `modules.enable_ptcg` | `true` | PTCG 模块 |
| `ptcg.api_key` | `""` | pokemontcg.io 可选 Key |
| `ptcg.prefer_source` | `tcgdex` | 预留数据源偏好 |

`/TCG状态` 查看当前启用情况。

---

## 🎮 指令速查

统一风格：`/模块 + 动词`（查卡 / 序号 / 换页 / 卡图 / 随机 …）

### 全局

```
/TCG帮助
/TCG状态
```

### OCG 游戏王

```
/OCG查卡 <卡名>
/OCG序号 <n>     /OCG换页 <n>
/OCG卡图 [CID]   /OCG随机
/OCG饼图[更新]
/OCG禁卡表 [OCG|简中]
/OCG点数更新
/OCG卡组检查 [OCG|简中]
/OCG导入卡组 <ourocg/ydke 链接>
/OCG导入卡组
<换行粘贴 YDK>
/OCG卡组图
/OCG起手  /OCG抽卡  /OCG手牌
```

### MD Master Duel

```
/MD更新T表   /MD查T表
/MD查卡组 <名>
/MD翻译T表
```

### DL Duel Links

```
/DL更新T表   /DL查T表
/DL查卡组 <名>
/DL翻译T表
```

### PTCG 宝可梦

```
/PTCG查卡 <中/英卡名>
/PTCG序号 <n>   /PTCG换页 <n>
/PTCG卡图       /PTCG随机
```

数据源：TCGdex GraphQL（主）+ pokemontcg.io（备）。内置常见中英映射。

---

## 📦 安装

1. 将本仓库放入 AstrBot `data/plugins/`
2. 重启 AstrBot
3. 管理面板启用插件，按需开关模块
4. 依赖：`aiohttp`、`Pillow`、`certifi`

```bash
git clone https://github.com/Eason4869/astrbot-plugin-tcg-galatea.git
```

---

## 🗺 ToDo / 规划

> 未来可能扩展的卡牌游戏模块（同样走「模块开关 + 统一指令」）

| 模块 | 代号 | 状态 | 说明 |
|------|------|------|------|
| 魔法风云会 | MTG | 📋 规划中 | 查卡、禁限表、构筑 |
| Weiss Schwarz | WS | 📋 规划中 | 卡查、卡组 |
| Vanguard | VG | 📋 规划中 | 卡查、T 环境 |
| 游戏王简中深绑 | SC | 💡 想法 | 简中卡盒 / 价格 |
| PTCG 简中卡库 | PTCG-CN | 💡 想法 | 依赖可用数据源 |
| 模块热切换命令 | — | 💡 想法 | `/TCG模块 开关 OCG` |

欢迎提 Issue / PR 认领模块。

---

## 🆚 与 duel-galatea 差异

| 项目 | duel-galatea 1.4.x | TCG工具箱 2.1.x |
|------|--------------------|-----------------|
| 中文名 | 游戏王工具箱 | **TCG工具箱** |
| 模块开关 | 无 | OCG / MD / DL / PTCG |
| 指令风格 | 混杂 | **/模块 + 动词** 统一 |
| PTCG | 无 | 双源查卡 |
| 冗余指令 | 较多 | 已精简（圣杯/裁定/卡盒/转存分享等） |
| DL 环境 | 曾误用 MD | 已修复 |

**已移除（低频/冗余）**：发动王牌圣杯、查询裁定、查询卡盒、发送ydk、卡组转存/分享、卡组检索、卡组状态重置 等。核心能力保留，旧别名尽量兼容。

---

## 🙏 致谢

- 原作者 [Noctfom](https://github.com/Noctfom/astrbot-plugin-duel-galatea) · [AstrBot](https://github.com/AstrBotDevs/AstrBot)
- ygocdb · RoTK · duelmeta · [TCGdex](https://www.tcgdex.dev) · [pokemontcg.io](https://pokemontcg.io)

---

## 📄 License

GPL-3.0

---

<p align="center">
  <sub>Made with 💚 · TCG工具箱 v2.1.0</sub>
</p>
