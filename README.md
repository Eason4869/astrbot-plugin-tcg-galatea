# 🟩 TCG Galatea · 多游戏王 / 宝可梦工具箱

<p align="center">
  <!-- Minecraft 主题浏览量（像素绿） -->
  <a href="https://github.com/Eason4869/astrbot-plugin-tcg-galatea">
    <img src="https://count.getloli.com/@astrbot-plugin-tcg-galatea?theme=moebooru&no-badge=true" alt="Visitors" />
    <img src="https://komarev.com/ghpvc/?username=Eason4869.astrbot-plugin-tcg-galatea&label=%F0%9F%9F%A9%20Visitors&color=38b000&style=flat-square&labelColor=1b1b1b" alt="Minecraft Visitors" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0.0-38b000?style=flat-square&labelColor=1b1b1b" alt="Version" />
  <img src="https://img.shields.io/badge/AstrBot-v4.0%2B-2b6cb0?style=flat-square&labelColor=1b1b1b" alt="AstrBot" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&labelColor=1b1b1b" alt="Python" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-38b000?style=flat-square&labelColor=1b1b1b" alt="License" />
  <img src="https://img.shields.io/badge/Modules-OCG%20%7C%20MD%20%7C%20DL%20%7C%20PTCG-69b34c?style=flat-square&labelColor=1b1b1b" alt="Modules" />
</p>

> 基于 [astrbot-plugin-duel-galatea](https://github.com/Noctfom/astrbot-plugin-duel-galatea) 扩展  
> 将 **OCG / MD / DL** 拆成独立开关，并新增 **PTCG 宝可梦查卡**。

---

## ✨ 功能一览

| 模块 | 开关 | 能力 |
|------|------|------|
| **OCG** | `enable_ocg` | 游戏王查卡、高清卡图、裁定 / 卡盒、禁卡表、RoTK 饼图、YDK 构筑、决斗模拟 |
| **MD** | `enable_md` | Master Duel T 表、MD 查卡组构筑图 |
| **DL** | `enable_dl` | Duel Links T 表、DL 查卡组构筑图 |
| **PTCG** | `enable_ptcg` | 宝可梦查卡（中/英）、序号 / 换页、高清卡图、随机宝可梦 |

四模块在 **管理面板 → 插件配置** 中可独立启停；也可用 `/模块状态` 查看。

---

## ⚙️ 配置说明

| 配置项 | 默认 | 说明 |
|--------|------|------|
| `modules.enable_ocg` | `true` | 启用 OCG 游戏王模块 |
| `modules.enable_md` | `true` | 启用 Master Duel 模块 |
| `modules.enable_dl` | `true` | 启用 Duel Links 模块 |
| `modules.enable_ptcg` | `true` | 启用宝可梦 PTCG 模块 |
| `ptcg.api_key` | `""` | pokemontcg.io 可选 API Key（提高频率限制） |
| `ptcg.prefer_source` | `tcgdex` | 预留数据源偏好 |

关闭某模块后，对应指令会提示「模块当前未启用」。

---

## 🐢 PTCG 宝可梦

```
/宝可梦查卡 喷火龙
/宝可梦查卡 Charizard
/宝可梦序号 1
/宝可梦换页 2
/宝可梦高清卡图
/随机宝可梦
```

**数据源**

1. **TCGdex GraphQL**（主）— 免费、无需 Key，名称检索 + 详情 + 卡图  
2. **pokemontcg.io**（备）— REST API，可选 Key 提高配额  

内置约 100 个常见宝可梦中英映射（喷火龙、皮卡丘、超梦…）。中文输入会自动转英文检索；完整简中官方卡库仍有限，结果以英文卡面为主。

---

## 🃏 游戏王 OCG

```
/查卡 <卡名>
/查卡序号 <n>     /查卡换页 <p>
/发送高清卡图 [CID]
/查询裁定         /查询卡盒
/随机一卡         /发动王牌圣杯
/OCG饼图更新      /OCG饼图
/禁卡表更新 [OCG/简中]
/Genesys更新
/卡组检查 [OCG/简中]
/接收卡组链接 /接收ydk文本
/发送ydk /发送卡组图片
/卡组转存 /卡组分享
/卡组起手 /卡组抽卡 /卡组检索 /卡组状态 /卡组状态重置
```

## ⚔️ Master Duel / Duel Links

```
/MD更新T表   /MD查询T表   /MD查卡组 <名>
/DL更新T表   /DL查询T表   /DL查卡组 <名>
/翻译T表 [DL|MD]
/查询卡组翻译 <英文>
/修改卡组翻译 <英文> <中文>
```

## 📖 帮助

```
/游戏王帮助
/TCG帮助
/模块状态
```

---

## 📦 安装

1. 将本仓库放入 AstrBot 的 `data/plugins/` 目录  
2. 重启 AstrBot  
3. 管理面板启用插件，按需开关模块  
4. 依赖：`aiohttp`、`Pillow`、`certifi`（`requirements.txt`）

```bash
# 或通过 AstrBot 插件市场 / Git 安装
git clone https://github.com/Eason4869/astrbot-plugin-tcg-galatea.git
```

---

## 🆚 与原插件的差异

| 项目 | 原 duel-galatea | 本插件 |
|------|-----------------|--------|
| 模块开关 | 无 | OCG / MD / DL / PTCG 独立配置 |
| PTCG | 无 | TCGdex + pokemontcg.io 双源查卡 |
| DL 查卡组 | 误用 MD 环境 | 已修复为 `DUEL_LINKS` |
| 插件 ID | `duel_galatea` | `tcg_galatea` |
| 数据目录 | `data/plugins/duel_galatea/` | `data/plugins/tcg_galatea/` |

---

## 🙏 致谢

- 原作者 [Noctfom](https://github.com/Noctfom/astrbot-plugin-duel-galatea) · [AstrBot](https://github.com/AstrBotDevs/AstrBot)
- 数据源：[ygocdb](https://ygocdb.com) · [RoTK](https://roadoftheking.com) · duelmeta · [TCGdex](https://www.tcgdex.dev) · [pokemontcg.io](https://pokemontcg.io)

---

## 📄 License

GPL-3.0（继承原插件）

---

<p align="center">
  <sub>Made with 💚 · Minecraft style visitors · TCG Galatea v2.0.0</sub>
</p>
