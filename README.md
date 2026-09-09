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
  <img src="https://img.shields.io/badge/Version-2.2.0-38b000?style=flat-square&labelColor=1b1b1b" alt="Version" />
  <img src="https://img.shields.io/badge/AstrBot-v4.0%2B-2b6cb0?style=flat-square&labelColor=1b1b1b" alt="AstrBot" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-38b000?style=flat-square&labelColor=1b1b1b" alt="License" />
  <img src="https://img.shields.io/badge/Modules-OCG%20%7C%20MD%20%7C%20DL%20%7C%20PTCG-69b34c?style=flat-square&labelColor=1b1b1b" alt="Modules" />
</p>

> 游戏王 + 宝可梦 · 四模块独立开关 · 统一指令

---

## ✨ 模块

| 模块 | 开关 | 说明 |
|------|------|------|
| **OCG** | `enable_ocg` | 游戏王查卡 / 裁定 / RoTK 饼图 / 禁卡表 / 随机 |
| **MD** | `enable_md` | 查卡 / 裁定 / T 表（饼图位）/ 随机 |
| **DL** | `enable_dl` | 查卡 / 裁定 / T 表（饼图位）/ 随机 |
| **PTCG** | `enable_ptcg` | 宝可梦查卡 / 随机（饼图与禁卡表预留） |

---

## ⚙️ 配置

| 配置项 | 默认 | 说明 |
|--------|------|------|
| `modules.enable_ocg` | `true` | OCG |
| `modules.enable_md` | `true` | MD |
| `modules.enable_dl` | `true` | DL |
| `modules.enable_ptcg` | `true` | PTCG |
| `ptcg.api_key` | `""` | pokemontcg.io 可选 Key |

`/TCG状态` 查看启用情况。

---

## 🎮 指令（四模块同构）

| 能力 | 说明 |
|------|------|
| 查卡 | 支持**模糊 / 全名 / 卡密**；命中唯一或卡密时自动出详情 + 高清卡图 |
| 序号 / 换页 | 多结果时选用 |
| 裁定 | 须先查到具体卡；OCG/MD/DL 可用 |
| 饼图 / 更新饼图 | OCG=RoTK；MD·DL=T 表 |
| 禁卡表 / 更新 | OCG 可用（首次约 1–3 分钟）；其它模块预留 |
| 随机一卡 | 自动出详情 + 卡图 |

```
/OCG查卡 青眼白龙
/OCG查卡 89631139
/OCG序号 1
/OCG裁定
/OCG饼图更新
/OCG禁卡表
/OCG随机
/TCG帮助
/TCG状态
```

MD / DL / PTCG 将前缀换成 `/MD` `/DL` `/PTCG` 即可。

---

## 📦 安装

1. 放入 AstrBot `data/plugins/`
2. 重启后在管理面板启用
3. 依赖：`aiohttp` `Pillow` `certifi`

```bash
git clone https://github.com/Eason4869/astrbot-plugin-tcg-galatea.git
```

---

## 🗺 ToDo

| 模块 | 代号 | 状态 |
|------|------|------|
| 魔法风云会 | MTG | 📋 规划 |
| Weiss Schwarz | WS | 📋 规划 |
| Vanguard | VG | 📋 规划 |
| PTCG 饼图 / 禁卡表 | — | 💡 想法 |
| MD / DL 禁卡表 | — | 💡 想法 |

---

## 🙏 致谢

- 原插件 [astrbot-plugin-duel-galatea](https://github.com/Noctfom/astrbot-plugin-duel-galatea)
- [AstrBot](https://github.com/AstrBotDevs/AstrBot) · ygocdb · RoTK · duelmeta · TCGdex · pokemontcg.io

## 📄 License

GPL-3.0
