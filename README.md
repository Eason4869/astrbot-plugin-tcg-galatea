# 🟩 TCG工具箱

<p align="center">
  <img src="https://raw.githubusercontent.com/Eason4869/astrbot-plugin-tcg-galatea/main/logo.png" width="128" height="128" alt="TCG工具箱 Logo" />
</p>

<p align="center">
  <a href="https://github.com/Eason4869/astrbot-plugin-tcg-galatea">
    <img src="https://count.getloli.com/@astrbot-plugin-tcg-galatea?theme=moebooru&no-badge=true" alt="Visitors" />
    <img src="https://komarev.com/ghpvc/?username=Eason4869.astrbot-plugin-tcg-galatea&label=%F0%9F%9F%A9%20Visitors&color=38b000&style=flat-square&labelColor=1b1b1b" alt="Visitors" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.3.2-38b000?style=flat-square&labelColor=1b1b1b" alt="Version" />
  <img src="https://img.shields.io/badge/AstrBot-v4.0%2B-2b6cb0?style=flat-square&labelColor=1b1b1b" alt="AstrBot" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-38b000?style=flat-square&labelColor=1b1b1b" alt="License" />
  <img src="https://img.shields.io/badge/Groups-OCG%20%7C%20简中%20%7C%20MD%20%7C%20DL%20%7C%20PTCG-69b34c?style=flat-square&labelColor=1b1b1b" alt="Groups" />
</p>

> 五大指令组 · 独立开关 · 统一子指令

---

## 指令结构

用法：`<组名> <子指令> [参数]`（组名与子指令之间用空格）。

### 全局

| 指令 | 别名 | 说明 |
|------|------|------|
| `TCG帮助` | `tcghelp` / `TCGHelp` | 功能总览 |
| `TCG状态` | `tcgstatus` / `模块状态` | 查看五模块开关 |

### 指令组

| 组名 | 常用别名（大小写均可） | 配置开关 |
|------|------------------------|----------|
| `OCG` | `ocg` / `Ocg` | `modules.enable_ocg` |
| `简中` | `sc` / `SC` / `简體` / `simplified` | `modules.enable_sc` |
| `MD` | `md` / `Md` / `masterduel` | `modules.enable_md` |
| `DL` | `dl` / `Dl` / `duellinks` | `modules.enable_dl` |
| `PTCG` | `ptcg` / `Ptcg` / `宝可梦` / `pokemon` | `modules.enable_ptcg` |

### 子指令（五组同构）

| 子指令 | 英文别名 | 参数 | 说明 |
|--------|----------|------|------|
| `查卡` | `search` / `Search` | `<卡名或卡密>` | 支持模糊、全名、卡密；命中后自动出详情 + 高清卡图 |
| `序号` | `select` / `Select` | `<n>` | 选中搜索列表第 n 条 |
| `换页` | `page` / `Page` | `<页码>` | 切换搜索结果页 |
| `裁定` | `ruling` / `faq` | — | 须先 `查卡` 到具体卡 |
| `饼图` | `meta` / `pie` / `T表` | `[更新]` | 带「更新」则抓取；OCG·简中=RoTK，MD·DL=T 表 |
| `禁卡表` | `banlist` / `limited` | — | OCG=OCG 表，简中=简中 表（首次约 1–3 分钟）；MD/DL/PTCG 预留 |
| `随机` | `random` / `Random` | — | 随机一卡，自动出图 |

### 示例

| 输入 | 作用 |
|------|------|
| `TCG帮助` | 查看帮助 |
| `OCG 查卡 青眼白龙` | 模糊/全名查卡，自动出图 |
| `OCG 查卡 89631139` | 按卡密查卡 |
| `OCG 序号 1` | 查看列表第 1 张 |
| `OCG 裁定` | 查当前卡裁定 |
| `OCG 饼图更新` | 抓取 RoTK 饼图 |
| `简中 禁卡表` | 更新简中禁卡表 |
| `md 饼图更新` | 更新 MD T 表（小写组名） |
| `PTCG 查卡 喷火龙` | 宝可梦查卡 |
| `ptcg random` | 随机宝可梦（英文子指令） |
---

## 配置

| 配置项 | 默认 | 说明 |
|--------|------|------|
| `modules.enable_ocg` | true | OCG 组 |
| `modules.enable_sc` | true | 简中组（与 OCG 分离） |
| `modules.enable_md` | true | MD 组 |
| `modules.enable_dl` | true | DL 组 |
| `modules.enable_ptcg` | true | PTCG 组 |
| `ptcg.api_key` | "" | pokemontcg.io 可选 Key |

`TCG状态` 查看启用情况。

---

## 安装

1. 放入 AstrBot `data/plugins/`
2. 重启后在管理面板启用
3. 依赖：`aiohttp` `Pillow` `certifi`

```bash
git clone https://github.com/Eason4869/astrbot-plugin-tcg-galatea.git
```

---

## ToDo

| 模块 | 代号 | 状态 |
|------|------|------|
| 魔法风云会 | MTG | 📋 规划 |
| Weiss Schwarz | WS | 📋 规划 |
| Vanguard | VG | 📋 规划 |
| PTCG 饼图/禁卡表 | — | 💡 想法 |
| MD/DL 禁卡表 | — | 💡 想法 |

---

## 致谢

- 原插件 [astrbot-plugin-duel-galatea](https://github.com/Noctfom/astrbot-plugin-duel-galatea)
- [AstrBot](https://github.com/AstrBotDevs/AstrBot) · ygocdb · RoTK · duelmeta · TCGdex · pokemontcg.io

## License

GPL-3.0
