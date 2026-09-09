# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- 规划：MTG / WS / VG 等新卡牌游戏模块
- PTCG / MD / DL 的饼图与禁卡表数据源

---

## [2.3.1] - 2026-09-09

### Fixed
- **`NameError: name 'quote' is not defined`**：补上 `from urllib.parse import quote`
- **PTCG 卡图 QQ 上传失败**（highway error 921）：改为先发文本再发图；优先下载本地/TCGdex low 图；失败回退为文字链接
- OCG/简中/MD/DL 查卡发图同样改为「文本优先 + 图失败不炸」

---

## [2.3.0] - 2026-09-09

### Added
- **五大指令组**（AstrBot `command_group` + 子指令）
  - `OCG` · `简中` · `MD` · `DL` · `PTCG`（宝可梦）
  - 统一子指令：`查卡` `序号` `换页` `裁定` `饼图` `禁卡表` `随机`
- **简中独立模块开关** `modules.enable_sc`（与 OCG 分离；简中走 `sc` 禁卡表）
- 组名与常用英文子指令通过 **alias** 覆盖大小写（`ocg`/`Ocg`、`search`/`Search` 等）
- 仅保留 2 个全局指令：`TCG帮助` · `TCG状态`

### Changed
- 用法示例：`OCG 查卡 青眼白龙` · `简中 禁卡表` · `MD 饼图更新` · `PTCG 查卡 喷火龙`
- 版本 `2.2.1` → `2.3.0`

### Removed
- 扁平指令（`/OCG查卡`、`/MD查卡` 等）改为组内子指令，避免指令表膨胀

---

## [2.2.1] - 2026-09-09
