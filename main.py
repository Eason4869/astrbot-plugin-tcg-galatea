# -*- coding: utf-8 -*-
"""
TCG Galatea - 游戏王 + 宝可梦多游戏工具箱
OCG / MD / DL / PTCG 四模块独立开关
"""

import os
import certifi
# === 全局 SSL 补丁  ===
os.environ['SSL_CERT_FILE'] = certifi.where()

import json
import random
import re
import asyncio
from typing import Dict, Any, List
from urllib.parse import quote
import aiohttp
import html


from astrbot.api.star import Star, register, StarTools  # 引入 StarTools
from astrbot.api.event import filter
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.platform.astr_message_event import AstrMessageEvent
import astrbot.api.message_components as Comp
from astrbot.api.all import logger  # 引入 logger

from .ydk_manager import YDKManager

# 确保 generic_tier_manager.py 在同一目录下
from .generic_tier_manager import GameType, TierCommandHandler

#  deck_breakdown.py
from .deck_breakdown import DeckBreakdownManager
from .rotk_manager import RotKManager

from .duel_simulator import DuelSimulator #引入 DuelSimulator

from .banlist_manager import BanlistManager #引入 BanlistManager

from .ptcg_searcher import PTCGSearcher, POKEMON_CN_MAP
from .vg_searcher import VGSearcher


class YugiohCardSearcher:
    # 将映射表提升为类常量，解决 PEP 8 问题
    ATTRIBUTE_MAP = {1: "地", 2: "水", 4: "炎", 8: "风", 16: "光", 32: "暗", 64: "神"}
    RACE_MAP = {
        1: "战士",
        2: "魔法师",
        4: "天使",
        8: "恶魔",
        16: "不死",
        32: "机械",
        64: "水",
        128: "炎",
        256: "岩石",
        512: "鸟兽",
        1024: "植物",
        2048: "昆虫",
        4096: "雷",
        8192: "龙",
        16384: "兽",
        32768: "兽战士",
        65536: "恐龙",
        131072: "鱼",
        262144: "海龙",
        524288: "爬虫类",
        1048576: "念动力",
        2097152: "幻神兽",
    }

    def __init__(self):
        self.base_url = "https://ygocdb.com/api/v0"
        # 优化资源管理：复用 Session
        self.session = aiohttp.ClientSession(trust_env=True, headers={"User-Agent": "Mozilla/5.0"})

    async def close(self):
        """关闭 Session"""
        if self.session:
            await self.session.close()

    async def _get_json(self, url: str, timeout: int = 15, retries: int = 2) -> Dict[str, Any]:
        """带重试的 JSON GET（兼容代理/偶发超时）。"""
        last_err = ""
        for i in range(retries + 1):
            try:
                to = aiohttp.ClientTimeout(total=timeout)
                async with self.session.get(url, timeout=to, ssl=False) as response:
                    if response.status == 200:
                        return await response.json(content_type=None)
                    last_err = f"HTTP {response.status}"
            except Exception as e:
                last_err = str(e) or e.__class__.__name__
            if i < retries:
                await asyncio.sleep(0.4 * (i + 1))
        return {"error": last_err}

    async def search_card(self, query: str) -> Dict[str, Any]:
        """搜索卡片：支持卡名模糊、卡密、中英文。

        - 纯数字卡密：优先按 ID 精确详情
        - 其它：全库模糊检索
        """
        q = (query or "").strip()
        if not q:
            return {"error": "搜索词为空"}

        # 卡密搜索：纯数字且长度合理
        if q.isdigit() and 4 <= len(q) <= 10:
            detail = await self.get_card_detail(q)
            if "error" not in detail and (detail.get("id") or detail.get("cn_name")):
                # 包装成列表，与搜索结果结构兼容
                item = {
                    "id": detail.get("id", q),
                    "cid": detail.get("cid"),
                    "cn_name": detail.get("cn_name", "未知"),
                    "sc_name": detail.get("sc_name", ""),
                    "type": detail.get("type", ""),
                    "text": detail.get("text", {}),
                    "data": detail.get("data", {}),
                    "detail": detail,
                }
                return {"result": [item], "mode": "id"}
            # 卡密没命中再走名称搜索兜底

        enc = quote(q, safe="")
        url = f"{self.base_url}/?search={enc}"
        data = await self._get_json(url, timeout=15)
        if "error" in data:
            return {"error": f"搜索出错: {data['error']}"}
        results = data.get("result") or []
        # 百鸽已做模糊匹配；若为空再试去空格/更短词
        if not results:
            alt = q.replace(" ", "").replace("-", "")
            if alt and alt != q:
                data2 = await self._get_json(f"{self.base_url}/?search={quote(alt, safe='')}", timeout=15)
                results = (data2 or {}).get("result") or []
                data = data2 if results else data
        data["mode"] = data.get("mode", "fuzzy")
        data.setdefault("result", results)
        return data

    async def get_card_detail(self, card_id: str) -> Dict[str, Any]:
        """获取卡片详情（卡密）。"""
        cid = str(card_id).strip()
        if not cid:
            return {"error": "卡片密码为空"}
        url = f"{self.base_url}/card/{cid}?show=all"
        data = await self._get_json(url, timeout=15, retries=2)
        if "error" in data:
            return {"error": f"获取详情出错: {data['error']}"}
        # 校验是否真是卡片对象
        if not any(k in data for k in ("id", "cn_name", "data", "text")):
            return {"error": f"详情数据异常: {str(data)[:120]}"}
        return data

    def format_card_info(self, card_data: Dict[str, Any]) -> str:
        """格式化卡片信息（重构版，拆分逻辑）"""
        if "error" in card_data:
            return card_data["error"]
        try:
            info = []
            # 1. 基础信息
            self._add_basic_info(card_data, info)

            # 2. 类型判断
            text_data = card_data.get("text", {})
            data = card_data.get("data", {})
            types_str = text_data.get("types", "")

            card_type_value = data.get("type", 0)
            is_monster = (card_type_value & 1) != 0

            if not is_monster:
                # 魔法/陷阱
                desc = text_data.get("desc", "")
                if desc:
                    info.append("🔹 卡片效果:\n{}".format(desc))
            else:
                # 怪兽
                self._add_monster_info(data, types_str, text_data, info)

            return "\n".join(info)
        except Exception as e:
            logger.error(f"格式化出错: {e}")
            return "格式化出错: {}".format(str(e))

    def _add_basic_info(self, card_data: Dict, info: List[str]):
        """辅助方法：添加基础信息"""
        cn_name = card_data.get("cn_name", "未知")
        sc_name = card_data.get("sc_name", "")
        name_display = (
            "{} ({})".format(cn_name, sc_name)
            if sc_name and sc_name != cn_name
            else cn_name
        )
        info.append("🃏 名称: {}".format(name_display))
        info.append("🆔 密码: {}".format(card_data.get("id", "未知")))

        types_str = card_data.get("text", {}).get("types", "")
        if types_str:
            info.append("🏷 卡片类型: {}".format(types_str))

    def _add_monster_info(
        self, data: Dict, types_str: str, text_data: Dict, info: List[str]
    ):
        """辅助方法：添加怪兽详细信息"""
        types_lower = types_str.lower()
        is_link = "连接" in types_lower
        is_xyz = "超量" in types_lower or "xyz" in types_lower
        is_pendulum = "灵摆" in types_lower

        atk = data.get("atk", "?")
        if is_link:
            info.append("攻守值: 攻击力{}/-".format(atk))
        else:
            def_val = data.get("def", "?")
            info.append("攻守值: 攻击力{}/守备力{}".format(atk, def_val))

        level_match = re.search(r"\[(?:★|☆|LINK-)(\d+)\]", types_str)
        if level_match:
            level_value = level_match.group(1)
            if is_link:
                info.append("Link值: {}".format(level_value))
            elif is_xyz:
                info.append("阶级: {}".format(level_value))
            else:
                info.append("等级: {}".format(level_value))

        attribute = data.get("attribute", 0)
        if attribute in self.ATTRIBUTE_MAP:
            info.append("属性: {}".format(self.ATTRIBUTE_MAP[attribute]))

        race = data.get("race", 0)
        if race in self.RACE_MAP:
            info.append("种族: {}".format(self.RACE_MAP[race]))

        if is_pendulum:
            self._add_pendulum_info(types_str, text_data, info)

        desc = text_data.get("desc", "")
        if desc:
            effect_title = "🔹 怪兽效果:" if is_pendulum else "🔹 卡片效果:"
            info.append("{}\n{}".format(effect_title, desc))

    def _add_pendulum_info(self, types_str: str, text_data: Dict, info: List[str]):
        """辅助方法：添加灵摆信息"""
        scale_matches = re.findall(r"(\d+)/(\d+)", types_str)
        if scale_matches and len(scale_matches) >= 1:
            left_scale, right_scale = scale_matches[-1]
            info.append("🔹 灵摆刻度: {}/{}".format(left_scale, right_scale))
        pdesc = text_data.get("pdesc", "")
        if pdesc:
            info.append("🔸 灵摆效果:\n{}".format(pdesc))

    def format_search_results(
        self, results: List[Dict], page: int, user_id: str, cmd: str = "OCG"
    ) -> str:
        page_size = 10
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(results))
        current_results = results[start_idx:end_idx]
        total_results = len(results)
        total_pages = (total_results + page_size - 1) // page_size
        output = [
            "🔍 搜索结果 (第 {}/{} 页，共 {} 个结果):\n".format(
                page, total_pages, total_results
            )
        ]
        for i, card in enumerate(current_results, start=start_idx + 1):
            name = card.get("cn_name", "未知")
            card_type = card.get("type", "")
            type_map = {"monster": "[怪兽]", "spell": "[魔法]", "trap": "[陷阱]"}
            type_tag = type_map.get(card_type, "")
            output.append("{}. {} {}".format(i, name, type_tag))
        output.append(
            "\n💡 /{} 序号 <序号> 查看详情 · /{} 换页 <页码> 切换".format(cmd, cmd)
        )
        return "\n".join(output)
    
    # === 新增：HTML 获取与解析方法 ===

    async def get_card_html(self, card_id: str) -> str:
        """获取百鸽详情页的 HTML 源码"""
        url = f"https://ygocdb.com/card/{card_id}"
        try:
            async with self.session.get(url, timeout=10, ssl=False) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            logger.error(f"HTML fetch error: {e}")
        return ""

    def parse_card_packs(self, html_content: str) -> List[str]:
        """解析卡盒信息 (Date - Code - Name)"""
        # 1. 找到包含 packs 的区域
        pack_list = []
        # 正则匹配 <li class="pack">...</li>
        # 结构: <span>日期</span><span>编号</span><a ...>包名</a>
        pattern = re.compile(
            r'<li class="pack">\s*<span>(.*?)</span><span>(.*?)</span>\s*<a[^>]*>(.*?)</a>',
            re.DOTALL
        )
        
        matches = pattern.findall(html_content)
        for date, code, name in matches:
            # 清理 HTML 转义字符 (如 &#39;)
            clean_name = html.unescape(name.strip())
            pack_list.append(f"[{date}] {code} - {clean_name}")
            
        return pack_list

    def parse_card_faq(self, html_content: str) -> List[Dict[str, str]]:
        """解析 FAQ/裁定 (Q&A Box)"""
        qa_list = []
        
        # 1. 提取所有 qabox
        # <div class="qabox ..."> ... </div>
        box_pattern = re.compile(r'<div class="qabox.*?>(.*?)<div class="info">', re.DOTALL)
        boxes = box_pattern.findall(html_content)
        
        for box in boxes:
            # 提取 Title, Question, Answer
            title_m = re.search(r'<div class="qa title"[^>]*>(.*?)</div>', box, re.DOTALL)
            q_m = re.search(r'<div class="qa question"[^>]*>(.*?)</div>', box, re.DOTALL)
            a_m = re.search(r'<div class="qa answer"[^>]*>(.*?)</div>', box, re.DOTALL)
            
            if q_m and a_m:
                t_str = self._clean_html(title_m.group(1)) if title_m else "Q&A"
                q_str = self._clean_html(q_m.group(1))
                a_str = self._clean_html(a_m.group(1))
                
                qa_list.append({
                    "title": t_str,
                    "q": q_str,
                    "a": a_str
                })
                
        return qa_list

    def _clean_html(self, raw_html: str) -> str:
        """清理 HTML 标签，转义字符，处理换行"""
        if not raw_html: return ""
        # 1. 处理换行: <br> -> \n
        text = re.sub(r'<br\s*/?>', '\n', raw_html, flags=re.IGNORECASE)
        # 2. 去除所有标签: <...>
        text = re.sub(r'<[^>]+>', '', text)
        # 3. 反转义: &lt; -> <
        text = html.unescape(text)
        return text.strip()


@register("tcg_galatea", "Eason4869", "TCG工具箱", "1.0.6-beta")
class TCGGalateaPlugin(Star):
    def __init__(self, context=None, config: AstrBotConfig = None):
        super().__init__(context, config)
        # Star 基类不会写 self.config，必须自己保存插件配置
        self.config = config if config is not None else {}
        self.card_searcher = YugiohCardSearcher()
        self.search_sessions = {}
        self.last_viewed_cards = {}
        self.all_card_ids = []  # 全卡片ID池

        # === PTCG ===
        ptcg_cfg = {}
        if isinstance(config, dict):
            ptcg_cfg = config.get("ptcg") or {}
            if not isinstance(ptcg_cfg, dict):
                ptcg_cfg = {}
        self.ptcg_searcher = PTCGSearcher(api_key=ptcg_cfg.get("api_key", ""))
        self._ptcg_cn_to_en = {cn: en for en, cn in POKEMON_CN_MAP.items()}

        # === VG（独立于 OCG / PTCG）===
        self.vg_searcher = VGSearcher()

        # === 修复数据持久化违规 ===
        # 1. 源码目录：仅用于读取随插件附带的静态文件 (如 card_ids.json)
        self.plugin_source_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. 数据目录：使用 StarTools 获取标准数据目录，用于存储缓存、图片等
        # 这会在 data/plugins/tcg_galatea/ 下创建目录
        try:
            self.data_dir = StarTools.get_data_dir()
        except Exception as e:
            logger.warning(
                f"StarTools.get_data_dir() 自动获取失败 ({e})，使用手动路径兜底。"
            )
            # 手动构建路径：data/plugins/tcg_galatea
            self.data_dir = os.path.join(os.getcwd(), "data", "plugins", "tcg_galatea")

        # 确保目录存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        logger.info(f"TCG Galatea 数据目录: {self.data_dir}")

        # 初始化各个 Manager，传入数据目录以便它们在正确的地方写文件
        # 注意：这里假设您的 Manager 构造函数已经更新为接收 data_dir
        self.tier_handler = TierCommandHandler(str(self.data_dir))
        self.rotk_manager = RotKManager(str(self.data_dir))
        # 实例化 YDKManager
        self.ydk_manager = YDKManager(str(self.data_dir), self.plugin_source_dir)

        # 实例化 DeckBreakdownManager (传入 ydk_manager)
        self.deck_breakdown = DeckBreakdownManager(
            str(self.data_dir), self.plugin_source_dir, self.ydk_manager
        )
        # 新增：决斗模拟器
        self.duel_sim = DuelSimulator()
        # 新增：禁限表管理器
        self.banlist_manager = BanlistManager(str(self.data_dir))
        # 加载ID (从源码目录读取)
        self._load_card_ids()

    # ---------- 模块开关 ----------

    def _modules_cfg(self) -> Dict[str, Any]:
        cfg = getattr(self, "config", None)
        if cfg is None:
            return {}
        # AstrBotConfig 是 dict 子类；兼容普通 dict
        try:
            m = cfg.get("modules") if hasattr(cfg, "get") else {}
        except Exception:
            m = {}
        return m if isinstance(m, dict) else {}

    def _mod_enabled(self, key: str) -> bool:
        return bool(self._modules_cfg().get(key, True))

    @property
    def ocg_on(self) -> bool:
        return self._mod_enabled("enable_ocg")

    @property
    def md_on(self) -> bool:
        return self._mod_enabled("enable_md")

    @property
    def dl_on(self) -> bool:
        return self._mod_enabled("enable_dl")

    @property
    def ptcg_on(self) -> bool:
        return self._mod_enabled("enable_ptcg")

    @property
    def vg_on(self) -> bool:
        return self._mod_enabled("enable_vg")

    async def terminate(self): # <--- 必须加 async
        """插件卸载/关闭时的清理工作"""
        # 关闭 aiohttp session
        if self.card_searcher:
            await self.card_searcher.close() # <--- 直接 await，确保资源释放
        if self.ptcg_searcher:
            await self.ptcg_searcher.close()
        if self.vg_searcher:
            await self.vg_searcher.close()

    def _load_card_ids(self):
        """加载纯ID列表到内存"""
        try:
            # 静态资源从源码目录读取
            ids_file_path = os.path.join(self.plugin_source_dir, "card_ids.json")

            if os.path.exists(ids_file_path):
                with open(ids_file_path, "r", encoding="utf-8") as f:
                    # 确保 ID 是字符串
                    self.all_card_ids = [str(x) for x in json.load(f)]
                # === 修复日志违规 ===
                logger.info(
                    f"DuelGalatea: 成功加载 {len(self.all_card_ids)} 个卡片ID到随机池"
                )
            else:
                logger.warning("DuelGalatea: 未找到card_ids.json文件，使用备用列表")
                self._load_backup_ids()

        except Exception as e:
            logger.error(f"DuelGalatea: 加载卡片ID失败: {e}")
            self._load_backup_ids()

    def _load_backup_ids(self):
        """备用ID列表"""
        backup_ids = [
            "16178681",
            "89631139",
            "4064256",
            "74677422",
            "38033121",
            "10000000",
            "53129443",
            "83104731",
            "94192409",
            "53334471",
            "46986414",
            "70828912",
            "36935103",
            "7902349",
            "65741786",
        ]
        self.all_card_ids = backup_ids
        logger.info(f"DuelGalatea: 使用备用ID列表，共 {len(backup_ids)} 个ID")

    def _resolve_deck_name(self, input_name: str) -> str:
        """利用 TierHandler 中的最新数据进行 中->英 转换"""
        # 1. 如果本身就是英文 Key (在翻译字典的键里)，直接返回
        # (不区分大小写比较)
        for en in self.tier_handler.manager.translations.keys():
            if en.lower() == input_name.lower():
                return en

        # 2. 尝试反向查找 (中文 -> 英文)
        # self.tier_handler.manager.translations 结构是 { "Sky Striker": "闪刀姬" }
        for en, cn in self.tier_handler.manager.translations.items():
            # 精确匹配
            if cn == input_name:
                return en
            # 模糊匹配 (可选，比如输入"闪刀"也能查到"闪刀姬")
            if input_name in cn:
                return en

        # 3. 没找到，原样返回，交给 deck_breakdown 自己去处理
        return input_name

    def _get_session_id(self, event: AstrMessageEvent) -> str:
        """
        获取会话ID (文件隔离核心逻辑)
        优先级: 群聊ID > 私聊用户ID > 默认值
        """
        obj = event.message_obj

        # 1. 尝试获取群号 (Group ID)
        # 不同的平台可能用不同的字段，这里做个兼容判断
        if hasattr(obj, "group_id") and obj.group_id:
            return f"group_{obj.group_id}"

        # 2. 如果没有群号，说明是私聊，尝试获取发送者 ID (Sender ID)
        # 写法 A: 直接在 message_obj 上
        if hasattr(obj, "sender_id") and obj.sender_id:
            return f"user_{obj.sender_id}"

        # 写法 B: 在 sender 对象里 (OneBot 标准常见结构)
        if hasattr(obj, "sender") and isinstance(obj.sender, dict):
            user_id = obj.sender.get("user_id")
            if user_id:
                return f"user_{user_id}"
        elif hasattr(obj, "sender") and hasattr(obj.sender, "user_id"):
            if obj.sender.user_id:
                return f"user_{obj.sender.user_id}"

        # 3. 实在获取不到，记录日志并返回 default
        # 这种情况很少见，除非是完全不支持 ID 的平台
        from astrbot.api.all import logger

        logger.warning(f"DuelGalatea: 无法识别会话 ID，使用 default。Obj: {obj}")
        return "default"
    
    async def _download_file(self, session: aiohttp.ClientSession, url: str, dest: str) -> str:
        """下载图片到本地，成功返回路径。"""
        if not url:
            return ""
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            to = aiohttp.ClientTimeout(total=25)
            async with session.get(
                url, timeout=to, ssl=False, allow_redirects=True
            ) as resp:
                if resp.status != 200:
                    logger.debug(f"下载图片 HTTP {resp.status}: {url}")
                    return ""
                ctype = (resp.headers.get("Content-Type") or "").lower()
                # 拒收 HTML 错误页
                if "html" in ctype:
                    logger.debug(f"下载图片得到 HTML: {url}")
                    return ""
                data = await resp.read()
            if not data or len(data) < 100:
                return ""
            # 简单魔数校验
            head = data[:16]
            is_img = (
                head.startswith(b"\xff\xd8")
                or head.startswith(b"\x89PNG")
                or head.startswith(b"GIF8")
                or (head[:4] == b"RIFF" and data[8:12] == b"WEBP")
                or head.startswith(b"<svg")
                or b"<svg" in data[:200].lower()
            )
            if not is_img and len(data) < 1000:
                return ""
            with open(dest, "wb") as f:
                f.write(data)
            return dest
        except Exception as e:
            logger.warning(f"下载图片失败 {url}: {e}")
            return ""

    async def _send_card_detail(
        self,
        event: AstrMessageEvent,
        card_id: str,
        card_name_fallback: str = "未知",
        prefetched: Dict = None,
        cmd: str = "OCG",
    ):
        """与原插件一致：一条消息里 图+文 一起发。"""
        user_id = getattr(event.message_obj, "sender_id", "unknown")
        cid = str(card_id)

        detail = prefetched if (prefetched and "error" not in prefetched) else None
        if not detail:
            detail = await self.card_searcher.get_card_detail(cid)
        if "error" in detail:
            logger.warning(f"详情获取失败 cid={cid}: {detail.get('error')}")
            await event.send(event.plain_result(
                f"⚠️ 详情接口暂时失败: {detail.get('error')}\n卡片密码: {cid}"
            ))
            return

        self.last_viewed_cards[user_id] = {
            "card_id": cid,
            "card_name": detail.get("cn_name", card_name_fallback),
            "card_data": detail,
        }

        formatted_detail = self.card_searcher.format_card_info(detail)
        status_info = self.banlist_manager.get_card_status(cid)
        tags = []
        if status_info.get("sc") and status_info["sc"] != "无限制":
            tags.append(f"🇨🇳简中:{status_info['sc']}")
        if status_info.get("ocg") and status_info["ocg"] != "无限制":
            tags.append(f"🇯🇵OCG:{status_info['ocg']}")
        if status_info.get("genesys", 0) > 0:
            tags.append(f"🧬Genesys:{status_info['genesys']}pt")
        if tags:
            formatted_detail += "\n" + " | ".join(tags)

        # 高清卡图（与原插件同源 CDN），下载后与文字同条发送
        chain = []
        hd_url = f"https://cdn.233.momobako.com/ygopro/pics/{cid}.jpg"
        dest = os.path.join(self.ydk_manager.images_dir, f"detail_{cid}.jpg")
        path = await self._download_file(self.card_searcher.session, hd_url, dest)
        if path:
            chain.append(Comp.Image.fromFileSystem(path))
        chain.append(Comp.Plain(formatted_detail))
        await event.send(event.chain_result(chain))




    # ================= helpers =================

    def _get_uid(self, event: AstrMessageEvent):
        uid = getattr(event.message_obj, "sender_id", None)
        if not uid and hasattr(event.message_obj, "sender"):
            uid = getattr(event.message_obj.sender, "user_id", None)
        return uid if uid is not None else "unknown"

    def _msg(self, event: AstrMessageEvent) -> str:
        return event.get_message_str().strip()

    def _params(self, event: AstrMessageEvent) -> list:
        """取出子命令之后的参数列表。

        指令组消息形如: `OCG 查卡 青眼白龙`
        优先读 AstrBot 解析结果；否则按「去掉组名+子命令」处理。
        """
        extra = None
        try:
            extra = event.get_extra("parsed_params")
        except Exception:
            extra = None
        if isinstance(extra, dict) and extra:
            # GreedyStr / str 等
            vals = []
            for v in extra.values():
                if v is None or v == "":
                    continue
                if isinstance(v, (list, tuple)):
                    vals.extend(str(x) for x in v if str(x))
                else:
                    vals.append(str(v))
            if vals:
                return vals
        parts = self._msg(event).split()
        # 去掉开头的组名（1 段）与子命令（1 段）
        return parts[2:] if len(parts) > 2 else []

    def _query_arg(self, event: AstrMessageEvent) -> str:
        return " ".join(self._params(event)).strip()

    def _int_arg(self, event: AstrMessageEvent):
        params = self._params(event)
        if not params:
            return None
        s = str(params[0]).strip()
        return int(s) if s.isdigit() else None

    # ---------- YGO 共用（OCG / MD / DL） ----------

    async def _ygo_search(self, event: AstrMessageEvent, cmd: str = "OCG"):
        """模糊 / 全名 / 卡密；唯一或卡密直接详情+高清图。"""
        user_id = self._get_uid(event)
        query = self._query_arg(event)
        if not query:
            await event.send(event.plain_result(
                f"用法: /{cmd} 查卡 <卡名或卡密>\n"
                f"• /{cmd} 查卡 青眼\n"
                f"• /{cmd} 查卡 89631139"
            ))
            return
        await event.send(event.plain_result(f"🔍 正在检索「{query}」..."))
        result = await self.card_searcher.search_card(query)
        if "error" in result:
            await event.send(event.plain_result(f"❌ 搜索出错: {result['error']}"))
            return
        results = result.get("result") or []
        if not results:
            await event.send(event.plain_result(f"⚠️ 未找到与「{query}」相关的卡片"))
            return
        if result.get("mode") == "id" or len(results) == 1:
            card = results[0]
            await self._send_card_detail(
                event, card["id"], card.get("cn_name", query),
                prefetched=card.get("detail"), cmd=cmd,
            )
            return
        self.search_sessions[user_id] = {"results": results, "query": query, "cmd": cmd}
        await event.send(event.plain_result(
            self.card_searcher.format_search_results(results, 1, user_id, cmd=cmd)
            + f"\n\n🔎 已全库模糊匹配，共 {len(results)} 条"
        ))

    async def _ygo_select(self, event: AstrMessageEvent, cmd: str = "OCG"):
        user_id = self._get_uid(event)
        num = self._int_arg(event)
        if num is None:
            await event.send(event.plain_result(f"用法: /{cmd} 序号 <序号>"))
            return
        if user_id not in self.search_sessions:
            await event.send(event.plain_result(f"请先 /{cmd} 查卡"))
            return
        results = self.search_sessions[user_id]["results"]
        if 1 <= num <= len(results):
            await self._send_card_detail(
                event, results[num - 1]["id"], results[num - 1].get("cn_name"), cmd=cmd
            )
        else:
            await event.send(event.plain_result("序号超出范围"))

    async def _ygo_page(self, event: AstrMessageEvent, cmd: str = "OCG"):
        user_id = self._get_uid(event)
        page = self._int_arg(event)
        if page is None:
            await event.send(event.plain_result(f"用法: /{cmd} 换页 <页码>"))
            return
        if user_id not in self.search_sessions:
            await event.send(event.plain_result("没有进行中的搜索"))
            return
        results = self.search_sessions[user_id]["results"]
        await event.send(event.plain_result(
            self.card_searcher.format_search_results(results, page, user_id, cmd=cmd)
        ))

    async def _ygo_random(self, event: AstrMessageEvent):
        if not self.all_card_ids:
            await event.send(event.plain_result("卡片数据库未加载"))
            return
        for _ in range(3):
            try:
                cid = random.choice(self.all_card_ids)
                detail = await self.card_searcher.get_card_detail(str(cid))
                if "error" not in detail and "data" in detail:
                    await self._send_card_detail(event, cid, detail.get("cn_name", "未知"))
                    return
            except Exception as e:
                logger.error(f"随机一卡异常: {e}")
        await event.send(event.plain_result("抽取失败，请稍后再试"))

    async def _ygo_pie_ocg(self, event: AstrMessageEvent):
        """OCG 饼图：带「更新」则抓取 RoTK。"""
        if "更新" in self._msg(event):
            await event.send(event.plain_result("🔍 正在抓取 RoTK 饼图..."))
            try:
                result = await self.rotk_manager.fetch_latest_report()
                if not result or "error" in result:
                    err = result.get("error", "Unknown") if result else "Empty"
                    await event.send(event.plain_result(f"⚠️ 更新失败: {err}"))
                    return
                if self.rotk_manager.save_local_data(result):
                    await event.send(event.plain_result(f"✅ 更新完毕: {result['title']}"))
                else:
                    await event.send(event.plain_result("⚠️ 保存失败"))
            except Exception as e:
                logger.error(f"饼图更新: {e}")
                await event.send(event.plain_result(f"⚠️ 内部错误: {e}"))
            return
        data = self.rotk_manager.load_local_data()
        if not data:
            await event.send(event.plain_result("⚠️ 本地无数据，请先 饼图更新"))
            return
        chain = []
        for p in data.get("local_paths", [])[:9]:
            if os.path.exists(p):
                chain.append(Comp.Image.fromFileSystem(p))
        chain.append(Comp.Plain(f"📊 {data.get('title','')}\n📅 {data.get('date','')}"))
        await event.send(event.chain_result(chain))

    async def _ygo_banlist_env(self, event: AstrMessageEvent, env: str, display: str):
        await event.send(event.plain_result(
            f"⏳ 正在获取 {display} 禁卡表...\n首次更新需解析卡名，约 1–3 分钟。"
        ))
        success, info, changes = await self.banlist_manager.update_banlist(
            env, self.card_searcher
        )
        if not success:
            await event.send(event.plain_result(f"❌ {info}"))
            return
        lines = [f"✅ {display} 禁卡表 {info}"]
        if changes:
            lines.append("\n📊 本期变动:")
            lines.extend(f"• {c}" for c in changes)
        else:
            lines.append("\n(本期无卡片状态变动)")
        await event.send(event.plain_result("\n".join(lines)))

    async def _ygo_tier(self, event: AstrMessageEvent, game: GameType, tag: str, display: str):
        if "更新" in self._msg(event):
            await self.tier_handler.update_tier_list(event, game, display)
        else:
            await self.tier_handler.query_tier_list(event, game, display)

    # ================= 指令组：OCG =================
    # 用法: OCG 查卡 / ocg 查卡 / Ocg 查卡（大小写靠别名）

    @filter.command_group("OCG", alias={"ocg", "Ocg"})
    def group_ocg(self):
        """OCG 游戏王指令组"""

    @group_ocg.command("查卡", alias={"search", "Search"})
    async def ocg_search(self, event: AstrMessageEvent):
        """模糊/全名/卡密查卡，自动高清图"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        await self._ygo_search(event, cmd="OCG")

    @group_ocg.command("序号", alias={"select", "Select"})
    async def ocg_select(self, event: AstrMessageEvent):
        """选中搜索结果"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        await self._ygo_select(event, cmd="OCG")

    @group_ocg.command("换页", alias={"page", "Page"})
    async def ocg_page(self, event: AstrMessageEvent):
        """切换搜索页"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        await self._ygo_page(event, cmd="OCG")

    @group_ocg.command("饼图", alias={"meta", "Meta", "pie", "Pie"})
    async def ocg_pie(self, event: AstrMessageEvent):
        """RoTK 饼图；参数带「更新」则抓取"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        await self._ygo_pie_ocg(event)

    @group_ocg.command("禁卡表", alias={"banlist", "Banlist", "limited", "Limited"})
    async def ocg_banlist(self, event: AstrMessageEvent):
        """OCG 禁卡表（较慢）"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        await self._ygo_banlist_env(event, "ocg", "OCG")

    @group_ocg.command(
        "简中禁卡表",
        alias={"scbanlist", "ScBanlist", "SC禁卡表", "scban", "ScBan"},
    )
    async def ocg_sc_banlist(self, event: AstrMessageEvent):
        """简中禁卡表（较慢）"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        await self._ygo_banlist_env(event, "sc", "简中")

    @group_ocg.command("随机", alias={"random", "Random"})
    async def ocg_random(self, event: AstrMessageEvent):
        """随机一卡"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        await self._ygo_random(event)

    # ================= 指令组：MD =================

    @filter.command_group("MD", alias={"md", "Md", "masterduel", "MasterDuel"})
    def group_md(self):
        """Master Duel 指令组"""

    @group_md.command("查卡", alias={"search", "Search"})
    async def md_search(self, event: AstrMessageEvent):
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self._ygo_search(event, cmd="MD")

    @group_md.command("序号", alias={"select", "Select"})
    async def md_select(self, event: AstrMessageEvent):
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self._ygo_select(event, cmd="MD")

    @group_md.command("换页", alias={"page", "Page"})
    async def md_page(self, event: AstrMessageEvent):
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self._ygo_page(event, cmd="MD")

    @group_md.command("饼图", alias={"meta", "Meta", "tier", "Tier", "T表"})
    async def md_pie(self, event: AstrMessageEvent):
        """MD 环境 = T表；参数带「更新」则抓取"""
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self._ygo_tier(event, GameType.MASTER_DUEL, "MD", "Master Duel")


    @group_md.command("随机", alias={"random", "Random"})
    async def md_random(self, event: AstrMessageEvent):
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self._ygo_random(event)

    # ================= 指令组：DL =================

    @filter.command_group("DL", alias={"dl", "Dl", "duellinks", "DuelLinks"})
    def group_dl(self):
        """Duel Links 指令组"""

    @group_dl.command("查卡", alias={"search", "Search"})
    async def dl_search(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self._ygo_search(event, cmd="DL")

    @group_dl.command("序号", alias={"select", "Select"})
    async def dl_select(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self._ygo_select(event, cmd="DL")

    @group_dl.command("换页", alias={"page", "Page"})
    async def dl_page(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self._ygo_page(event, cmd="DL")

    @group_dl.command("饼图", alias={"meta", "Meta", "tier", "Tier", "T表"})
    async def dl_pie(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self._ygo_tier(event, GameType.DUEL_LINKS, "DL", "Duel Links")


    @group_dl.command("随机", alias={"random", "Random"})
    async def dl_random(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self._ygo_random(event)

    # ================= 指令组：PTCG =================

    @filter.command_group(
        "PTCG",
        alias={"ptcg", "Ptcg", "宝可梦", "Pokemon", "pokemon", "Pokémon"},
    )
    def group_ptcg(self):
        """宝可梦 PTCG 指令组"""

    def _resolve_ptcg_query(self, query: str) -> str:
        q = query.strip()
        if not q:
            return q
        if q in self._ptcg_cn_to_en:
            return self._ptcg_cn_to_en[q]
        for cn, en in self._ptcg_cn_to_en.items():
            if cn == q or cn in q or q in cn:
                return en
        return q

    async def _send_ptcg_detail(self, event: AstrMessageEvent, card_id: str):
        """图文同条发送（与原插件链式消息一致）。"""
        user_id = self._get_uid(event)
        detail = await self.ptcg_searcher.get_detail(card_id)
        if "error" in detail:
            await event.send(event.plain_result(detail["error"]))
            return
        self.ptcg_searcher.last_viewed[user_id] = {
            "card_id": detail.get("id", card_id),
            "card_name": detail.get("name", "未知"),
            "card_data": detail,
        }
        text = self.ptcg_searcher.format_detail(detail)
        img = self.ptcg_searcher.image_url(detail)
        chain = []
        if img:
            # 优先本地文件（QQ 上传更稳），失败则 URL 直发
            safe = re.sub(r"[^A-Za-z0-9_-]", "_", str(detail.get("id", "card")))
            dest = os.path.join(self.data_dir, "ptcg_img", f"{safe}.png")
            path = await self._download_file(self.ptcg_searcher.session, img, dest)
            if path and os.path.exists(path):
                chain.append(Comp.Image.fromFileSystem(path))
            else:
                chain.append(Comp.Image.fromURL(img))
        chain.append(Comp.Plain(text))
        try:
            await event.send(event.chain_result(chain))
        except Exception as e:
            logger.warning(f"PTCG 图文同发失败，降级纯文本: {e}")
            if img:
                text += f"\n🖼 {img}"
            await event.send(event.plain_result(text))

    @group_ptcg.command("查卡", alias={"search", "Search"})
    async def ptcg_search(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        user_id = self._get_uid(event)
        raw = self._query_arg(event)
        if not raw:
            await event.send(event.plain_result("用法: 查卡 <中/英卡名>\n例如: 查卡 喷火龙"))
            return
        query = self._resolve_ptcg_query(raw)
        if query != raw:
            await event.send(event.plain_result(f"🔍 中文识别: {raw} → {query}"))
        result = await self.ptcg_searcher.search(query, page=1)
        if "error" in result:
            await event.send(event.plain_result(f"❌ {result['error']}"))
            return
        results = result["all_results"]
        # 仅唯一结果才直出详情；多结果一律列表，便于 /PTCG 序号
        if len(results) == 1:
            await self._send_ptcg_detail(event, results[0]["id"])
            return
        self.ptcg_searcher.search_sessions[user_id] = {"results": results, "query": query}
        await event.send(event.plain_result(self.ptcg_searcher.format_search_page(result)))

    @group_ptcg.command("序号", alias={"select", "Select"})
    async def ptcg_select(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        user_id = self._get_uid(event)
        num = self._int_arg(event)
        if num is None:
            await event.send(event.plain_result("用法: 序号 <序号>"))
            return
        if user_id not in self.ptcg_searcher.search_sessions:
            await event.send(event.plain_result("请先查卡"))
            return
        results = self.ptcg_searcher.search_sessions[user_id]["results"]
        if 1 <= num <= len(results):
            await self._send_ptcg_detail(event, results[num - 1]["id"])
        else:
            await event.send(event.plain_result("序号超出范围"))

    @group_ptcg.command("换页", alias={"page", "Page"})
    async def ptcg_page(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        user_id = self._get_uid(event)
        page = self._int_arg(event)
        if page is None:
            await event.send(event.plain_result("用法: 换页 <页码>"))
            return
        if user_id not in self.ptcg_searcher.search_sessions:
            await event.send(event.plain_result("没有进行中的搜索"))
            return
        all_r = self.ptcg_searcher.search_sessions[user_id]["results"]
        page_size = 10
        total_pages = max(1, (len(all_r) + page_size - 1) // page_size)
        if page < 1 or page > total_pages:
            await event.send(event.plain_result(f"页码超出范围 (1-{total_pages})"))
            return
        page_data = {
            "results": all_r[(page - 1) * page_size : page * page_size],
            "page": page,
            "page_size": page_size,
            "total": len(all_r),
            "total_pages": total_pages,
            "source": "cache",
            "query": self.ptcg_searcher.search_sessions[user_id].get("query", ""),
        }
        await event.send(event.plain_result(self.ptcg_searcher.format_search_page(page_data)))

    @group_ptcg.command("随机", alias={"random", "Random"})
    async def ptcg_random(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        # 用高可用常见名，保证有稳定卡图
        pool = [
            "Pikachu", "Charizard", "Eevee", "Mewtwo", "Gengar",
            "Gyarados", "Snorlax", "Lucario", "Greninja", "Dragonite",
            "Bulbasaur", "Squirtle", "Umbreon", "Rayquaza", "Arceus",
        ]
        random.shuffle(pool)
        for name in pool:
            try:
                result = await self.ptcg_searcher.search(name, page=1)
                results = result.get("all_results") or []
                if "error" in result or not results:
                    continue
                pick = next(
                    (c for c in results if (c.get("name") or "") == name),
                    results[0],
                )
                await self._send_ptcg_detail(event, pick["id"])
                return
            except Exception as e:
                logger.warning(f"PTCG随机 {name}: {e}")
                continue
        await event.send(event.plain_result("随机失败，请稍后再试"))

    # ================= 指令组：VG（独立） =================

    @filter.command_group(
        "VG",
        alias={"vg", "Vg", "先导者", "Vanguard", "vanguard"},
    )
    def group_vg(self):
        """Cardfight!! Vanguard 指令组"""

    async def _send_vg_detail(self, event: AstrMessageEvent, page_title: str):
        """图文同条发送（风格对齐 PTCG）。优先 CDN 直链本地下载。"""
        user_id = self._get_uid(event)
        detail = await self.vg_searcher.get_detail(page_title)
        if "error" in detail:
            await event.send(event.plain_result(detail["error"]))
            return
        self.vg_searcher.last_viewed[user_id] = {
            "card_id": detail.get("id", page_title),
            "card_name": detail.get("name", "未知"),
            "card_data": detail,
        }
        text = self.vg_searcher.format_detail(detail)

        # 候选图：已解析直链 → FilePath 兜底
        candidates = []
        direct = (detail.get("image_url") or "").strip()
        if direct:
            candidates.append(direct)
        fallback = self.vg_searcher.image_url(detail)
        if fallback and fallback not in candidates:
            candidates.append(fallback)

        chain = []
        img_attached = False
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", str(detail.get("id", "vgcard"))[:80])
        dest = os.path.join(self.data_dir, "vg_img", f"{safe}.png")
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
        except Exception:
            pass

        for img in candidates:
            path = await self._download_file(self.vg_searcher.session, img, dest)
            if path and os.path.exists(path):
                chain.append(Comp.Image.fromFileSystem(path))
                img_attached = True
                break
        if not img_attached and direct:
            # 本地失败再试 URL 直发（部分适配器可拉 CDN）
            chain.append(Comp.Image.fromURL(direct))
            img_attached = True

        if not img_attached and detail.get("url"):
            text += f"\n🖼 {detail.get('url')}"

        chain.append(Comp.Plain(text))
        try:
            await event.send(event.chain_result(chain))
        except Exception as e:
            logger.warning(f"VG 图文同发失败，降级纯文本: {e}")
            if direct:
                text += f"\n🖼 {direct}"
            elif detail.get("url"):
                text += f"\n🖼 {detail.get('url')}"
            await event.send(event.plain_result(text))

    @group_vg.command("查卡", alias={"search", "Search"})
    async def vg_search(self, event: AstrMessageEvent):
        if not self.vg_on:
            return await self._deny_module(event, "VG")
        raw = self._query_arg(event)
        if not raw:
            await event.send(
                event.plain_result(
                    "用法: 查卡 <英文卡名|日文假名|卡包编号>\n"
                    "例如: 查卡 Blaster Blade\n例如: 查卡 TD01-005"
                )
            )
            return
        result = await self.vg_searcher.search(raw, page=1)
        if "error" in result:
            await event.send(event.plain_result(f"❌ {result['error']}"))
            return
        results = result["all_results"]
        # 唯一结果直出详情；多结果出列表
        if len(results) == 1:
            await self._send_vg_detail(event, results[0]["id"])
            return
        user_id = self._get_uid(event)
        self.vg_searcher.search_sessions[user_id] = {
            "results": results,
            "query": raw,
        }
        await event.send(event.plain_result(self.vg_searcher.format_search_page(result)))

    @group_vg.command("序号", alias={"select", "Select"})
    async def vg_select(self, event: AstrMessageEvent):
        if not self.vg_on:
            return await self._deny_module(event, "VG")
        user_id = self._get_uid(event)
        num = self._int_arg(event)
        if num is None:
            await event.send(event.plain_result("用法: 序号 <序号>"))
            return
        if user_id not in self.vg_searcher.search_sessions:
            await event.send(event.plain_result("请先查卡"))
            return
        results = self.vg_searcher.search_sessions[user_id]["results"]
        if 1 <= num <= len(results):
            await self._send_vg_detail(event, results[num - 1]["id"])
        else:
            await event.send(event.plain_result("序号超出范围"))

    @group_vg.command("换页", alias={"page", "Page"})
    async def vg_page(self, event: AstrMessageEvent):
        if not self.vg_on:
            return await self._deny_module(event, "VG")
        user_id = self._get_uid(event)
        page = self._int_arg(event)
        if page is None:
            await event.send(event.plain_result("用法: 换页 <页码>"))
            return
        if user_id not in self.vg_searcher.search_sessions:
            await event.send(event.plain_result("没有进行中的搜索"))
            return
        all_r = self.vg_searcher.search_sessions[user_id]["results"]
        page_size = 10
        total_pages = max(1, (len(all_r) + page_size - 1) // page_size)
        if page < 1 or page > total_pages:
            await event.send(event.plain_result(f"页码超出范围 (1-{total_pages})"))
            return
        page_data = {
            "results": all_r[(page - 1) * page_size : page * page_size],
            "page": page,
            "page_size": page_size,
            "total": len(all_r),
            "total_pages": total_pages,
            "source": "Fandom",
            "query": self.vg_searcher.search_sessions[user_id].get("query", ""),
        }
        await event.send(event.plain_result(self.vg_searcher.format_search_page(page_data)))

    @group_vg.command("随机", alias={"random", "Random"})
    async def vg_random(self, event: AstrMessageEvent):
        if not self.vg_on:
            return await self._deny_module(event, "VG")
        detail = await self.vg_searcher.random_card()
        if "error" in detail:
            await event.send(event.plain_result(f"❌ {detail['error']}"))
            return
        await self._send_vg_detail(event, detail["id"])

    # ================= 全局 =================

    @filter.command("TCG状态", alias={"/TCG状态", "/模块状态", "/tcgstatus", "tcgstatus", "TCGStatus", "tcgStatus"})
    async def cmd_status(self, event: AstrMessageEvent):
        rows = [
            ("OCG", self.ocg_on),
            ("MD", self.md_on),
            ("DL", self.dl_on),
            ("PTCG", self.ptcg_on),
            ("VG", self.vg_on),
        ]
        lines = ["📦 TCG工具箱 · 模块状态"]
        lines += [f"  {'✅' if on else '❌'} {n}" for n, on in rows]
        lines.append("\n开关在 管理面板 → 插件配置 中修改")
        await event.send(event.plain_result("\n".join(lines)))

    @filter.command(
        "TCG帮助",
        alias={"/TCG帮助", "/游戏王帮助", "/tcghelp", "tcghelp", "TCGHelp", "tcgHelp", "/helpTCG", "帮助TCG"},
    )
    async def cmd_help(self, event: AstrMessageEvent):
        ocg = "✅" if self.ocg_on else "❌"
        md = "✅" if self.md_on else "❌"
        dl = "✅" if self.dl_on else "❌"
        pt = "✅" if self.ptcg_on else "❌"
        vg = "✅" if self.vg_on else "❌"
        text = f"""TCG工具箱 v1.0.6-beta
================================
全局
• TCG帮助  TCG状态

指令组（空格分隔；大小写均可）
OCG [{ocg}]
• OCG 查卡 <卡名|卡密>
• OCG 序号 <n>   OCG 换页 <n>
• OCG 饼图 [更新]
• OCG 禁卡表
• OCG 简中禁卡表
• OCG 随机

MD [{md}]
• MD 查卡 / 序号 / 换页
• MD 饼图 [更新]（T表）
• MD 随机

DL [{dl}]
• DL 查卡 / 序号 / 换页
• DL 饼图 [更新]（T表）
• DL 随机

PTCG [{pt}]
• PTCG 查卡 <中/英>
• PTCG 序号 / 换页
• PTCG 随机

VG [{vg}]  先导者（Fandom，英/日/编号）
• VG 查卡 <en|假名|编号>
• VG 序号 / 换页
• VG 随机

查卡自动出高清卡图
================================"""
        await event.send(event.plain_result(text))
