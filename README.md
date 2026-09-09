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
  <img src="https://img.shields.io/badge/Version-2.4.0-38b000?style=flat-square&labelColor=1b1b1b" alt="Version" />
  <img src="https://img.shields.io/badge/AstrBot-v4.0%2B-2b6cb0?style=flat-square&labelColor=1b1b1b" alt="AstrBot" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-38b000?style=flat-square&labelColor=1b1b1b" alt="License" />
  <img src="https://img.shields.io/badge/Groups-OCG%20%7C%20MD%20%7C%20DL%20%7C%20PTCG-69b34c?style=flat-square&labelColor=1b1b1b" alt="Groups" />
</p>

> 四大指令组 · 独立开关 · 统一子指令

---

## 指令结构

用法：`<组名> <子指令> [参数]`。

### 全局

| 指令 | 别名 | 说明 |
|------|------|------|
| `TCG帮助` | `tcghelp` | 功能总览 |
| `TCG状态` | `tcgstatus` / `模块状态` | 查看四模块开关 |

### 指令组

| 组名 | 常用别名 | 配置开关 |
|------|----------|----------|
| `OCG` | `ocg` / `Ocg` | `modules.enable_ocg` |
| `MD` | `md` / `Md` / `masterduel` | `modules.enable_md` |
| `DL` | `dl` / `Dl` / `duellinks` | `modules.enable_dl` |
| `PTCG` | `ptcg` / `Ptcg` / `宝可梦` / `pokemon` | `modules.enable_ptcg` |

### 子指令

| 子指令 | 英文别名 | 参数 | OCG | MD | DL | PTCG |
|--------|----------|------|-----|----|----|------|
| `查卡` | `search` | `<卡名或卡密>` | ✓ | ✓ | ✓ | ✓ |
| `序号` | `select` | `<n>` | ✓ | ✓ | ✓ | ✓ |
| `换页` | `page` | `<页码>` | ✓ | ✓ | ✓ | ✓ |
| `饼图` | `meta` / `T表` | `[更新]` | RoTK | T表 | T表 | — |
| `禁卡表` | `banlist` | — | ✓ | 预留 | 预留 | — |
| `随机` | `random` | — | ✓ | ✓ | ✓ | ✓ |

查卡支持模糊 / 全名 / 卡密，命中后自动出详情 + 高清卡图。

### 示例

| 输入 | 作用 |
|------|------|
| `TCG帮助` | 查看帮助 |
| `OCG 查卡 青眼白龙` | 查卡 |
| `OCG 查卡 89631139` | 卡密查卡 |
| `OCG 序号 1` | 列表第 1 张 |
| `OCG 饼图更新` | 抓取 RoTK 饼图 |
| `OCG 禁卡表` | 更新 OCG 禁卡表 |
| `md 饼图更新` | 更新 MD T 表 |
| `PTCG 查卡 喷火龙` | 宝可梦查卡 |
| `ptcg random` | 随机宝可梦 |

---

## 配置

| 配置项 | 默认 | 说明 |
|--------|------|------|
| `modules.enable_ocg` | true | OCG 组 |
| `modules.enable_md` | true | MD 组 |
| `modules.enable_dl` | true | DL 组 |
| `modules.enable_ptcg` | true | PTCG 组 |
| `ptcg.api_key` | "" | pokemontcg.io 可选 Key |

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
| MD/DL 禁卡表 | — | 💡 想法 |

---

## 致谢

- 原插件 [astrbot-plugin-duel-galatea](https://github.com/Noctfom/astrbot-plugin-duel-galatea)
- [AstrBot](https://github.com/AstrBotDevs/AstrBot) · ygocdb · RoTK · duelmeta · TCGdex · pokemontcg.io

## License

GPL-3.0
