# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- 规划：MTG / WS / VG 等新卡牌游戏模块
- 预留 `ptcg.prefer_source` 生效逻辑

---

## [2.1.0] - 2026-09-09

### Added
- 插件 LOGO（Minecraft 像素风 `logo.png`）
- README **ToDo** 规划区：MTG / Weiss Schwarz / Vanguard 等
- 统一全局指令：`/TCG帮助` · `/TCG状态`

### Changed
- **中文名**：游戏王工具箱 → **TCG工具箱**
- **指令风格统一为「模块 + 动词」**
  - OCG：`/OCG查卡` `/OCG序号` `/OCG换页` `/OCG卡图` `/OCG随机` `/OCG饼图` `/OCG禁卡表` `/OCG卡组检查` `/OCG导入卡组` `/OCG卡组图` `/OCG起手` `/OCG抽卡` `/OCG手牌`
  - MD：`/MD更新T表` `/MD查T表` `/MD查卡组` `/MD翻译T表`
  - DL：`/DL更新T表` `/DL查T表` `/DL查卡组` `/DL翻译T表`
  - PTCG：`/PTCG查卡` `/PTCG序号` `/PTCG换页` `/PTCG卡图` `/PTCG随机`
- 版本 `2.0.0` → `2.1.0`
- 帮助页按模块对齐展示

### Removed
精简低频 / 冗余指令（核心能力仍在，旧别名尽量兼容）：
- `/发动王牌圣杯`
- `/查询裁定` · `/查询卡盒`
- `/发送ydk`（文件）
- `/卡组转存` · `/卡组分享`
- `/卡组检索`
- `/卡组状态重置`（用 `/OCG起手` 重开）
- `/查询卡组翻译` · `/修改卡组翻译`（由 `/MD翻译T表` 等覆盖）
- 独立 `/翻译T表`（拆成 `/MD翻译T表` `/DL翻译T表`）
- 独立 `/接收ydk文本` `/接收卡组链接`（合并为 `/OCG导入卡组`）

---

## [2.0.0] - 2026-09-09

### Added
- **四模块独立开关**（插件配置 `modules.enable_ocg` / `enable_md` / `enable_dl` / `enable_ptcg`）
- **PTCG 宝可梦模块**
  - `/宝可梦查卡`（中/英文卡名）
  - `/宝可梦序号` · `/宝可梦换页`
  - `/宝可梦高清卡图` · `/随机宝可梦`
  - 数据源：TCGdex GraphQL（主）+ pokemontcg.io（备）
  - 可选 `ptcg.api_key` 提高 pokemontcg.io 配额
  - 内置常见宝可梦中英对照映射
- `/模块状态` 查看当前启用模块
- `/TCG帮助`（与 `/游戏王帮助` 等价）
- 新增 `_conf_schema.json` 配置 schema
- 新增 `CHANGELOG.md`

### Changed
- 插件 ID：`duel_galatea` → **`tcg_galatea`**
- 数据目录：`data/plugins/duel_galatea/` → **`data/plugins/tcg_galatea/`**
- 版本：`1.4.1` → **`2.0.0`**
- 基于原插件能力拆分为 OCG / MD / DL 三套可独立启停的环境模块
- README 重写：增加 Minecraft 主题浏览量头、模块对照表、安装说明

### Fixed
- **DL 查卡组**误用 `GameType.MASTER_DUEL` 的问题，改为 `GameType.DUEL_LINKS`

### Removed
- 无（功能兼容原 OCG / MD / DL 指令集，仅受开关控制）

---

## [1.4.1] - 上游

上游 [astrbot-plugin-duel-galatea](https://github.com/Noctfom/astrbot-plugin-duel-galatea) 基线，主要能力包括：

- 百鸽 API 游戏王查卡 / 高清卡图 / 裁定 / 卡盒
- duelmeta：DL / MD T 表与关键卡
- RoTK：OCG 饼图
- YDK 构筑、会话隔离、决斗模拟
- 禁卡表与 Genesys 点数
- 随机一卡、王牌圣杯

### 参考版本脉络（上游）
- `1.4.0` 禁卡表爬取、卡组模拟
- `1.3.0` YDK 读取、会话隔离
- `1.2.0` 全面 aiohttp、RoTK 爬取
- `1.1.0` 娱乐功能、duelmeta
- `1.0.0` 查卡组件

---

[Unreleased]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.1.0
[2.0.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.0.0
