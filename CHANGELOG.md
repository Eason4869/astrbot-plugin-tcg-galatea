# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- 规划：MTG / WS / VG 等新卡牌游戏模块
- MD / DL 禁卡表数据源

---

## [2.4.0] - 2026-09-09

### Removed
- **全部「裁定」子指令**（OCG / MD / DL / PTCG）
- **简中指令组**与 `modules.enable_sc` 开关
- **PTCG 饼图 / 禁卡表** 占位指令（无对应数据源）

### Fixed
- **`PTCG 随机`**：改为多候选重试 + 详情校验，降低单次检索失败

### Changed
- 四模块指令组：`OCG` · `MD` · `DL` · `PTCG`
- 版本 `2.3.2` → `2.4.0`

---

## [2.3.2] - 2026-09-09

### Fixed
- 搜索列表提示统一为 `/OCG 序号 <n>` · `/PTCG 序号 <n>` 等组+子指令格式
- TCGdex 卡图地址补全 `/high.png`（原先无扩展名打不开）
- 详情改为 **一条消息内图文同发**（对齐原 duel-galatea 的 `chain_result`）
- OCG 高清图改用完整 CDN jpg 下载后本地发送

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

### Fixed
- 查卡详情 URL 编码与重试；详情失败时回退 CDN 图
- 禁卡表首次更新文案标明约 1–3 分钟

### Added
- 查卡支持模糊 / 全名 / 卡密；自动高清卡图

### Removed
- 独立 `/OCG卡图` 等指令

---

## [2.2.0] - 2026-09-09

### Fixed
- `self.config` 未保存导致 `/TCG帮助` 报错

### Changed
- 指令统一为「模块 + 动词」；LOGO 重做

### Removed
- 构筑/模拟等低频指令

---

## [2.1.0] - 2026-09-09

### Added
- 插件 LOGO；README ToDo

### Changed
- 中文名改为 **TCG工具箱**；指令风格统一

---

## [2.0.0] - 2026-09-09

### Added
- OCG/MD/DL/PTCG 四模块开关；PTCG 查卡

### Fixed
- DL 查卡组误用 MD 环境

---

[Unreleased]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/compare/v2.4.0...HEAD
[2.4.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.4.0
[2.3.2]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.3.2
[2.3.1]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.3.1
[2.3.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.3.0
[2.2.1]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.2.1
[2.2.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.2.0
[2.1.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.1.0
[2.0.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v2.0.0
