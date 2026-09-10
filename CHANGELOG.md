# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

- 魔法风云会 / Weiss Schwarz 等新游戏模块
- MD / DL 禁卡表数据源
- PTCG / VG 简中卡名映射
- VG 饼图 / 禁卡表（若找到稳定数据源）

---

## [1.0.6-beta] - 2026-09-10

**VG 收尾：默认关闭、出图修复、README 整理。**

### Added

- **VG 指令组**（独立模块，与 OCG / PTCG 代码隔离）
  - 新文件 `vg_searcher.py`：独立 aiohttp session、独立会话缓存、独立格式化
  - `VG 查卡 <英文卡名|日文假名|卡包编号>`（Fandom MediaWiki API）
  - `VG 序号` / `VG 换页` / `VG 随机`
  - 别名：`vg` / `Vanguard` / `先导者`
  - 详情：名称、假名、编号、等级/力量/护盾、集团、效果、卡图

### Changed

- `modules.enable_vg` **默认 `false`**（beta，默认不启用）
- README：注明 VG 处于 beta、默认关闭；ToDo 按实际能力重写
- 版本号 → **1.0.6-beta**（dev）

### Fixed

- VG 查卡改为 imageinfo 解析 CDN 直链出图，不再只丢 wiki 链接
- README：删除大 logo；count.getloli 去掉 `no-badge` 巨长文本

### Notes

- 数据源 Fandom，**暂无简中卡名**；不影响 OCG / MD / DL / PTCG

---

## [1.0.1] - 2026-09-10

### Added

- **OCG 简中禁卡表指令**：`OCG 简中禁卡表`（别名 `scbanlist` / `SC禁卡表` / `scban`）
  - 后端 `BanlistManager` 的 `env=sc`（官方 gameking 接口 `type=2`）此前一直未暴露指令入口
  - 简中禁限表经百鸽解析卡名后写入本地缓存；查卡详情会附带 `🇨🇳简中:…` 状态标签
  - 与 `OCG 禁卡表`（日版）相互独立，首次更新各约 1–3 分钟

### Fixed

- README 中「可选 `OCG|简中` 后缀」为未实现的描述，已改为独立指令说明
- README 目录页内锚点曾被 `test` 类资产校验误判（上游 multica_bridge 同类问题；本仓库文档同步澄清）

### Changed

- 版本号 1.0.0 → **1.0.1**（`metadata.yaml` / `@register` / 帮助文案 / README 徽章）

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

[Unreleased]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/compare/v1.0.6-beta...HEAD
[1.0.6-beta]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/compare/v1.0.1...v1.0.6-beta
[1.0.1]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Eason4869/astrbot-plugin-tcg-galatea/releases/tag/v1.0.0
