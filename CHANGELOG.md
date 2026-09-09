# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- 预留更多 PTCG 中文映射与简中卡包收录
- 预留 `ptcg.prefer_source` 生效逻辑

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

[Unreleased]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.0.0
