# 🟩 TCG工具箱

<p align="center">
  <a href="https://github.com/Eason4869/astrbot-plugin-tcg-galatea">
    <img src="https://count.getloli.com/@astrbot-plugin-tcg-galatea?theme=moebooru" alt="count" />
    <img src="https://komarev.com/ghpvc/?username=Eason4869.astrbot-plugin-tcg-galatea&label=%F0%9F%9F%A9%20Visitors&color=38b000&style=flat-square&labelColor=1b1b1b" alt="Visitors" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.6--beta-38b000?style=flat-square&labelColor=1b1b1b" alt="Version" />
  <img src="https://img.shields.io/badge/AstrBot-v4.0%2B-2b6cb0?style=flat-square&labelColor=1b1b1b" alt="AstrBot" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&labelColor=1b1b1b" alt="Python" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-38b000?style=flat-square&labelColor=1b1b1b" alt="License" />
  <img src="https://img.shields.io/badge/Groups-OCG%20%7C%20MD%20%7C%20DL%20%7C%20PTCG%20%7C%20VG-69b34c?style=flat-square&labelColor=1b1b1b" alt="Groups" />
</p>

AstrBot 多游戏卡牌工具箱插件。五大指令组 **OCG / MD / DL / PTCG / VG** 独立开关，统一「组名 + 子指令」用法。

> **VG（先导者）目前处于 beta，默认关闭。** 稳定使用请保持关闭；需要试用时在「插件配置」中将 `modules.enable_vg` 设为 `true`。

---

## 功能特性

| 能力 | 说明 |
|------|------|
| 统一指令组 | `OCG` · `MD` · `DL` · `PTCG` · `VG`，空格分隔，大小写不敏感（别名覆盖） |
| 查卡 | 支持**模糊 / 全名 / 卡密**；命中后自动发送详情 + 高清卡图（图文同条） |
| 环境信息 | OCG 饼图（RoTK）；MD / DL 饼图（T 表，可更新） |
| 禁卡表 | OCG 官方禁限表同步（首次约 1–3 分钟） |
| 随机 | 各组随机一卡，自动出图 |
| 模块开关 | 管理面板可分别关闭某一组，关闭后对应指令会提示未启用 |

---

## 指令说明

用法格式：

```text
<组名> <子指令> [参数]
```

### 全局指令

| 指令 | 别名 | 说明 |
|------|------|------|
| `TCG帮助` | `tcghelp` / `TCGHelp` | 功能总览 |
| `TCG状态` | `tcgstatus` / `模块状态` | 查看五模块启用状态 |

### 指令组

| 组名 | 别名（大小写均可） | 配置开关 |
|------|-------------------|----------|
| `OCG` | `ocg` / `Ocg` | `modules.enable_ocg` |
| `MD` | `md` / `Md` / `masterduel` | `modules.enable_md` |
| `DL` | `dl` / `Dl` / `duellinks` | `modules.enable_dl` |
| `PTCG` | `ptcg` / `Ptcg` / `宝可梦` / `pokemon` | `modules.enable_ptcg` |
| `VG` | `vg` / `Vg` / `先导者` / `Vanguard` | `modules.enable_vg`（**beta，默认关闭**） |

### 子指令一览

| 子指令 | 英文别名 | 参数 | OCG | MD | DL | PTCG | VG |
|--------|----------|------|:---:|:--:|:--:|:----:|:--:|
| `查卡` | `search` / `Search` | `<卡名或卡密>` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `序号` | `select` / `Select` | `<序号>` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `换页` | `page` / `Page` | `<页码>` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `饼图` | `meta` / `pie` / `T表` | `[更新]` | RoTK | T 表 | T 表 | — | — |
| **`禁卡表`** | `banlist` / `limited` | — | **✓** | — | — | — | — |
| **`简中禁卡表`** | `scbanlist` / `SC禁卡表` | — | **✓** | — | — | — | — |
| `随机` | `random` / `Random` | — | ✓ | ✓ | ✓ | ✓ | ✓ |

说明：

- **查卡**：模糊、全名、卡密（纯数字）均可；唯一结果直接出详情+卡图，多结果出列表。
- **PTCG 查卡**：受 [TCGdex](https://www.tcgdex.dev) 接口语言覆盖限制，目前**仅支持英文卡名 / 英文卡组代码查询**，**暂不支持简体中文**卡名（简中卡库仍在规划中，见 ToDo）。
- **VG 查卡**（**beta，默认不启用**）：数据源 [Cardfight!! Vanguard Wiki (Fandom)](https://cardfight.fandom.com)，支持**英文卡名 / 日文假名 / 卡包编号**（如 `TD01-005`）；**暂无简中卡名**。代码与 OCG / PTCG 完全隔离。需要时在插件配置中打开 `modules.enable_vg`。
- **序号 / 换页**：对上一次查卡列表操作。
- **饼图**：不带参数为本地缓存；参数含「更新」则重新抓取。
  - OCG：RoTK 环境饼图  
  - MD / DL：duelmeta 的 T 表  
- **禁卡表**：`OCG 禁卡表` 为日版 OCG 官方禁限表；`OCG 简中禁卡表` 为简体中文官方表（数据来自 gameking 官方接口，卡名经百鸽解析）。两者相互独立，首次更新各需约 1–3 分钟。查卡详情里会附带简中状态标签（`🇨🇳简中:…`）。
- **随机**：随机一卡，自动发送详情与卡图。

### 常用示例

```text
TCG帮助
TCG状态

OCG 查卡 青眼白龙
OCG 查卡 89631139
OCG 序号 1
OCG 饼图更新
OCG 禁卡表
OCG 简中禁卡表
OCG 随机

MD 饼图更新
MD 饼图

DL 饼图更新

# PTCG 目前仅支持英文查询（见上方说明）
PTCG 查卡 Pikachu
PTCG 查卡 Charizard
PTCG 序号 1
PTCG 随机

# VG 先导者（英文 / 假名 / 卡包编号）
VG 查卡 Blaster Blade
VG 查卡 ブラスター・ブレード
VG 查卡 TD01-005
VG 序号 1
VG 随机

# 小写与英文子指令同样可用
ocg search 89631139
ptcg random
vg random
```

---

## 配置

在 AstrBot **管理面板 → 插件配置** 中修改：

| 配置项 | 默认 | 说明 |
|--------|------|------|
| `modules.enable_ocg` | `true` | 是否启用 OCG 指令组 |
| `modules.enable_md` | `true` | 是否启用 MD 指令组 |
| `modules.enable_dl` | `true` | 是否启用 DL 指令组 |
| `modules.enable_ptcg` | `true` | 是否启用 PTCG 指令组 |
| `modules.enable_vg` | `false` | 是否启用 VG 指令组（先导者·**beta，默认关闭**） |
| `ptcg.api_key` | `""` | pokemontcg.io 可选 API Key（提高频率限制） |
| `ptcg.prefer_source` | `tcgdex` | 预留数据源偏好 |

### 兼容性（metadata）

| 项 | 值 |
|----|-----|
| AstrBot 版本 | `>=4.0` |
| 支持平台 | `aiocqhttp`（QQ） |
| 标签 | 游戏王 · 宝可梦 · 先导者 · 查卡 · 卡牌 · 工具箱 |

> 其它平台未实测，保守不声明；若你在非 QQ 适配器上验证通过，可自行扩展 `support_platforms`。

---

## 数据源

| 游戏 | 来源 |
|------|------|
| 游戏王卡片 | [ygocdb](https://ygocdb.com)（百鸽） |
| OCG 饼图 | RoTK |
| OCG 禁卡表 | 官方禁限表接口 |
| MD / DL T 表 | masterduelmeta / duellinksmeta |
| 宝可梦 | [TCGdex](https://www.tcgdex.dev)（主）→ [pokemontcg.io](https://pokemontcg.io)（备）·**仅英文，暂无简中** |
| 先导者 VG | [Cardfight!! Vanguard Wiki (Fandom)](https://cardfight.fandom.com)·**英/日/编号，暂无简中** |

---

## 安装

1. 将本仓库目录放入 AstrBot 的 `data/plugins/`
2. 重启 AstrBot
3. 在管理面板启用插件，并按需开关五个模块

```bash
git clone https://github.com/Eason4869/astrbot-plugin-tcg-galatea.git
```

依赖（`requirements.txt`）：

- `aiohttp`
- `Pillow`
- `certifi`

---

## ToDo / 规划

| 模块 | 代号 | 状态 |
|------|------|------|
| Vanguard（查卡/随机） | VG | **beta，默认关闭**（`enable_vg`） |
| 魔法风云会 | MTG | 规划中 |
| Weiss Schwarz | WS | 规划中 |
| PTCG 简中卡名 | — | 想法（TCGdex 无简中字段） |
| VG 简中卡名 / 饼图 / 禁卡表 | — | 想法（暂无稳定数据源） |
| MD / DL 禁卡表 | — | 想法 |

欢迎 Issue / PR 认领。

---

## 致谢

- 灵感来源：[Noctfom/astrbot-plugin-duel-galatea](https://github.com/Noctfom/astrbot-plugin-duel-galatea)
- [AstrBot](https://github.com/AstrBotDevs/AstrBot)
- ygocdb · RoTK · duelmeta · TCGdex · pokemontcg.io · Cardfight!! Vanguard Wiki (Fandom)

---

## License

[GPL-3.0](./LICENSE)
