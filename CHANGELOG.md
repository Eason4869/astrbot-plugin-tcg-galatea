# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- 魔法风云会 / Weiss Schwarz / Vanguard 等新游戏模块
- MD / DL 禁卡表数据源
- PTCG 简中卡库

---

## [1.0.0] - 2026-09-09

**首个正式版。**

### Added

- **四大指令组**（AstrBot `command_group` + 子指令）
  - `OCG` · `MD` · `DL` · `PTCG`
  - 统一子指令：`查卡` `序号` `换页` `饼图` `禁卡表` `随机`
  - 组名 / 英文子指令通过别名覆盖大小写（`ocg`/`Ocg`、`search`/`Search` 等）
- **全局指令**：`TCG帮助` · `TCG状态`
- **模块独立开关**（插件配置）
  - `modules.enable_ocg` / `enable_md` / `enable_dl` / `enable_ptcg`
- **游戏王（OCG）**
  - 查卡：模糊 / 全名 / 卡密，自动详情 + 高清卡图（图文同条）
  - RoTK 饼图查看与更新
  - 官方禁卡表同步（OCG / 简中环境）
  - 随机一卡
- **Master Duel / Duel Links**
  - 查卡（复用游戏王卡库）
  - T 表（饼图位）查看与更新（duelmeta）
  - 随机一卡
- **宝可梦 PTCG**
  - 查卡：中英名映射 + 英文检索（TCGdex 主 / pokemontcg.io 备）
  - 多结果列表 → 序号 / 换页 → 详情 + 卡图
  - 随机宝可梦
- 插件 LOGO、`_conf_schema.json` 配置面板

### Changed

- 指令风格统一为 **「组名 + 空格 + 子指令」**
- 插件中文名：**TCG工具箱**
- 插件 ID：`tcg_galatea`，数据目录 `data/plugins/tcg_galatea/`

### Fixed

- `Star` 基类不写入 `self.config` 导致开关失效
- TCGdex 卡图地址需补 `/high.png`
- MD / DL T 表站点 HTML 变更导致解析为空
- PTCG 多结果误直出详情；随机卡图不稳定
- QQ 高速路大图上传失败时的降级发送

### Removed

（相对开发过程中的试验版）

- 全部「裁定」子指令
- 简中独立指令组（`enable_sc`）
- PTCG 饼图 / 禁卡表占位指令
- 构筑模拟、YDK 导入、卡组检查等低频指令
- MD / DL 禁卡表占位指令

---

## [上游基线]

灵感来源：[Noctfom/astrbot-plugin-duel-galatea](https://github.com/Noctfom/astrbot-plugin-duel-galatea)。

---

[Unreleased]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v1.0.0
