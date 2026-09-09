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
  <img src="https://img.shields.io/badge/Version-2.3.0-38b000?style=flat-square&labelColor=1b1b1b" alt="Version" />
  <img src="https://img.shields.io/badge/AstrBot-v4.0%2B-2b6cb0?style=flat-square&labelColor=1b1b1b" alt="AstrBot" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-38b000?style=flat-square&labelColor=1b1b1b" alt="License" />
  <img src="https://img.shields.io/badge/Groups-OCG%20%7C%20简中%20%7C%20MD%20%7C%20DL%20%7C%20PTCG-69b34c?style=flat-square&labelColor=1b1b1b" alt="Groups" />
</p>

> 五大指令组 · 独立开关 · 统一子指令

---

## 指令结构

```
全局
  TCG帮助
  TCG状态

指令组（组名 + 空格 + 子指令）
  OCG / 简中 / MD / DL / PTCG
    查卡 <卡名|卡密>     # 模糊/全名/卡密，自动出高清卡图
    序号 <n>
    换页 <n>
    裁定                 # 须先查到具体卡
    饼图 [更新]          # OCG·简中=RoTK；MD·DL=T表
    禁卡表               # OCG=OCG表；简中=简中表
    随机
```

**大小写**：组名与英文子指令均带别名，如 `OCG`/`ocg`/`Ocg`，`查卡`/`search`/`Search`。

**示例**
```
TCG帮助
OCG 查卡 青眼白龙
OCG 查卡 89631139
OCG 序号 1
OCG 裁定
OCG 饼图更新
OCG 禁卡表
简中 禁卡表
md 饼图更新
PTCG 查卡 喷火龙
ptcg random
```

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
