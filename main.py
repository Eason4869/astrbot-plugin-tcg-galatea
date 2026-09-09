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

    async def search_card(self, query: str) -> Dict[str, Any]:
        """异步搜索卡片"""
        try:
            url = f"{self.base_url}/?search={query}"
            async with self.session.get(url, timeout=10, ssl=False) as response:
                if response.status == 200:
                    # 修复：必须返回解析后的 JSON
                    return await response.json(content_type=None)
                else:
                    return {"error": f"API请求失败: {response.status}"}
        except Exception as e:
            return {"error": f"搜索出错: {str(e)}"}

    async def get_card_detail(self, card_id: str) -> Dict[str, Any]:
        """异步获取卡片详情"""
        try:
            url = f"{self.base_url}/card/{card_id}?show=all"
            async with self.session.get(url, timeout=10, ssl=False) as response:
                if response.status == 200:
                    # 修复：必须返回解析后的 JSON
                    return await response.json(content_type=None)
                else:
                    return {"error": f"获取详情失败: {response.status}"}
        except Exception as e:
            return {"error": f"获取详情出错: {str(e)}"}

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
        self, results: List[Dict], page: int, user_id: str
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
            "\n💡 /OCG序号 <序号> 查看详情 · /OCG换页 <页码> 切换"
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


@register("tcg_galatea", "Noctfom, Eason4869", "TCG工具箱", "2.1.0")
class TCGGalateaPlugin(Star):
    def __init__(self, context=None, config: AstrBotConfig = None):
        super().__init__(context, config)
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
        if not isinstance(self.config, dict):
            return {}
        m = self.config.get("modules")
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

    async def _deny_module(self, event: AstrMessageEvent, name: str):
        await event.send(event.plain_result(f"⚠️ {name} 模块当前未启用，请在插件配置中打开。"))

    def _tier_any_on(self) -> bool:
        return self.md_on or self.dl_on

    async def terminate(self): # <--- 必须加 async
        """插件卸载/关闭时的清理工作"""
        # 关闭 aiohttp session
        if self.card_searcher:
            await self.card_searcher.close() # <--- 直接 await，确保资源释放
        if self.ptcg_searcher:
            await self.ptcg_searcher.close()

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
    
    async def _send_card_detail(self, event: AstrMessageEvent, card_id: str, card_name_fallback: str = "未知"):
        """获取详情、更新缓存、拼接G点信息并发送"""
        user_id = getattr(event.message_obj, "sender_id", "unknown") # 获取用户ID用于缓存
        
        # 1. 获取详情
        detail = await self.card_searcher.get_card_detail(str(card_id))
        if "error" in detail:
            await event.send(event.plain_result(f"获取详情失败: {detail['error']}"))
            return

        # 2. === 关键：更新最后查看的卡片缓存 ===
        # 这样 /发送高清卡图、/查裁定 都能用了
        self.last_viewed_cards[user_id] = {
            "card_id": str(card_id),
            "card_name": detail.get("cn_name", card_name_fallback),
            "card_data": detail,
        }

        # 3. 格式化基础文本
        formatted_detail = self.card_searcher.format_card_info(detail)

        # 4. 拼接禁卡/Genesys信息
        status_info = self.banlist_manager.get_card_status(str(card_id))
        tags = []
        if status_info["sc"] != "无限制": tags.append(f"🇨🇳简中:{status_info['sc']}")
        if status_info["ocg"] != "无限制": tags.append(f"🇯🇵OCG:{status_info['ocg']}")
        if status_info["genesys"] > 0: tags.append(f"🧬Genesys:{status_info['genesys']}pt")
            
        if tags:
            formatted_detail += "\n" + " | ".join(tags)

        # 5. 下载图片并发送
        chain = []
        local_img = await self.ydk_manager._download_image(self.card_searcher.session, str(card_id))
        if local_img:
            temp_path = os.path.join(self.ydk_manager.images_dir, f"temp_{card_id}.jpg")
            local_img.save(temp_path)
            chain.append(Comp.Image.fromFileSystem(temp_path))
        
        chain.append(Comp.Plain(formatted_detail))
        await event.send(event.chain_result(chain))


    # ================= 统一指令层：/模块 + 动词 =================

    def _get_uid(self, event: AstrMessageEvent):
        uid = getattr(event.message_obj, "sender_id", None)
        if not uid and hasattr(event.message_obj, "sender"):
            uid = getattr(event.message_obj.sender, "user_id", None)
        return uid if uid is not None else "unknown"

    # ---------- OCG 查卡 ----------

    @filter.command("OCG查卡", alias=["/OCG查卡", "/查卡"])
    async def handle_ocg_search(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        user_id = self._get_uid(event)
        parts = event.get_message_str().strip().split()
        if len(parts) <= 1:
            await event.send(event.plain_result("用法: /OCG查卡 <卡名>\n例如: /OCG查卡 青眼白龙"))
            return
        query = " ".join(parts[1:])
        result = await self.card_searcher.search_card(query)
        if "error" in result:
            await event.send(event.plain_result(f"❌ 搜索出错: {result['error']}"))
            return
        results = result.get("result") or []
        if not results:
            await event.send(event.plain_result(f"⚠️ 未找到与「{query}」相关的卡片"))
            return
        if len(results) == 1:
            await self._send_card_detail(event, results[0]["id"], results[0].get("cn_name", query))
            return
        self.search_sessions[user_id] = {"results": results, "current_page": 1}
        await event.send(
            event.plain_result(self.card_searcher.format_search_results(results, 1, user_id))
        )

    @filter.command("OCG序号", alias=["/OCG序号", "/查卡序号"])
    async def handle_ocg_select(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        user_id = self._get_uid(event)
        parts = event.get_message_str().strip().split()
        if len(parts) < 2 or not parts[1].isdigit():
            await event.send(event.plain_result("用法: /OCG序号 <序号>"))
            return
        if user_id not in self.search_sessions:
            await event.send(event.plain_result("请先 /OCG查卡 搜索"))
            return
        num = int(parts[1])
        results = self.search_sessions[user_id]["results"]
        if 1 <= num <= len(results):
            await self._send_card_detail(event, results[num - 1]["id"], results[num - 1].get("cn_name"))
        else:
            await event.send(event.plain_result("序号超出范围"))

    @filter.command("OCG换页", alias=["/OCG换页", "/查卡换页"])
    async def handle_ocg_page(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        user_id = self._get_uid(event)
        parts = event.get_message_str().strip().split()
        if len(parts) < 2 or not parts[1].isdigit():
            await event.send(event.plain_result("用法: /OCG换页 <页码>"))
            return
        if user_id not in self.search_sessions:
            await event.send(event.plain_result("没有进行中的搜索"))
            return
        results = self.search_sessions[user_id]["results"]
        await event.send(
            event.plain_result(self.card_searcher.format_search_results(results, int(parts[1]), user_id))
        )

    @filter.command("OCG卡图", alias=["/OCG卡图", "/发送高清卡图"])
    async def handle_ocg_image(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        user_id = self._get_uid(event)
        parts = event.get_message_str().strip().split()
        if len(parts) > 1:
            if not parts[1].isdigit():
                await event.send(event.plain_result("卡片密码必须是数字"))
                return
            card_id = parts[1]
        elif user_id in self.last_viewed_cards:
            card_id = self.last_viewed_cards[user_id]["card_id"]
        else:
            await event.send(event.plain_result("请先 /OCG查卡，或 /OCG卡图 <密码>"))
            return
        url = f"https://cdn.233.momobako.com/ygopro/pics/{card_id}.jpg"
        try:
            await event.send(event.image_result(url))
        except Exception:
            await event.send(event.plain_result(url))

    @filter.command("OCG随机", alias=["/OCG随机", "/随机一卡"])
    async def handle_ocg_random(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
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
                logger.error(f"OCG随机异常: {e}")
        await event.send(event.plain_result("抽取失败，请稍后再试"))

    # ---------- OCG 环境 ----------

    @filter.command("OCG饼图", alias=["/OCG饼图", "/OCG饼图更新", "OCG饼图更新"])
    async def handle_ocg_pie(self, event: AstrMessageEvent):
        """带「更新」则抓取，否则发送本地饼图。"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        msg = event.get_message_str().strip()
        want_update = "更新" in msg
        if want_update:
            await event.send(event.plain_result("🔍 正在连接 RotK 抓取数据..."))
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
                logger.error(f"OCG饼图更新出错: {e}")
                await event.send(event.plain_result(f"⚠️ 内部错误: {e}"))
            return
        data = self.rotk_manager.load_local_data()
        if not data:
            await event.send(event.plain_result("⚠️ 本地无数据，请先发送 /OCG饼图更新"))
            return
        chain = []
        for p in data.get("local_paths", [])[:9]:
            if os.path.exists(p):
                chain.append(Comp.Image.fromFileSystem(p))
        chain.append(Comp.Plain(f"📊 {data.get('title','')}\\n📅 {data.get('date','')}"))
        await event.send(event.chain_result(chain))

    @filter.command("OCG禁卡表", alias=["/OCG禁卡表", "/禁卡表更新", "/OCG禁卡表更新"])
    async def handle_ocg_banlist(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        parts = event.get_message_str().strip().upper().split()
        # /OCG禁卡表 [更新] [OCG|简中]
        target_env, target_name = "ocg", "OCG"
        do_update = True
        for p in parts[1:]:
            if "简中" in p or p == "SC":
                target_env, target_name = "sc", "简中"
            elif "OCG" in p:
                target_env, target_name = "ocg", "OCG"
        await event.send(event.plain_result(f"⏳ 正在获取最新 {target_name} 禁卡表..."))
        success, info, changes = await self.banlist_manager.update_banlist(target_env, self.card_searcher)
        if not success:
            await event.send(event.plain_result(f"❌ {info}"))
            return
        lines = [f"✅ {target_name} 禁卡表 {info}"]
        if changes:
            lines.append("\\n📊 本期变动:")
            lines.extend(f"• {c}" for c in changes)
        else:
            lines.append("\\n(本期无卡片状态变动)")
        await event.send(event.plain_result("\\n".join(lines)))

    @filter.command("OCG卡组检查", alias=["/OCG卡组检查", "/卡组检查"])
    async def handle_ocg_deck_check(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        parts = event.get_message_str().strip().upper().split()
        target_env, env_display = "ocg", "OCG"
        if len(parts) > 1:
            if "简中" in parts[1] or "SC" in parts[1]:
                target_env, env_display = "sc", "简中"
        session = f"user_{self._get_uid(event)}"
        main, extra, side = self.ydk_manager.load_last_ydk(session)
        if not main:
            await event.send(event.plain_result("⚠️ 未找到卡组，请先 /OCG导入卡组"))
            return
        res = self.banlist_manager.check_deck_legality(target_env, main, extra, side)
        lines = [f"📊 卡组检查 ({env_display})"]
        if not res["banlist_issues"]:
            lines.append("✅ 禁限表: 合规")
        else:
            lines.append("❌ 禁限表违规:")
            for cid, status, count, limit in res["banlist_issues"]:
                d = await self.card_searcher.get_card_detail(cid)
                lines.append(f"  • [{status}] {d.get('cn_name', cid)}: {count}/{limit}")
        lines.append(f"\\n🧬 Genesys: {res['genesys_points']} pt")
        await event.send(event.plain_result("\\n".join(lines)))

    @filter.command("OCG点数更新", alias=["/OCG点数更新", "/Genesys更新"])
    async def handle_ocg_points(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        await event.send(event.plain_result("⏳ 正在抓取 Genesys 点数..."))
        ok, msg, report = await self.banlist_manager.update_genesys(self.card_searcher)
        if not ok:
            await event.send(event.plain_result(f"❌ {msg}"))
            return
        lines = [f"✅ {msg}"]
        if report:
            lines.extend(f"• {x}" for x in report[:10])
        await event.send(event.plain_result("\\n".join(lines)))

    # ---------- OCG 构筑 ----------

    @filter.command("OCG导入卡组", alias=["/OCG导入卡组", "/接收卡组链接", "/接收ydk文本"])
    async def handle_ocg_import(self, event: AstrMessageEvent):
        """导入 ourocg/ydke 链接，或换行粘贴 YDK 文本。"""
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        session_id = self._get_session_id(event)
        text = event.get_message_str().strip()
        # strip first token (command)
        if "\\n" in text:
            head, rest = text.split("\\n", 1)
            parts0 = head.strip().split()
            url_or_none = parts0[1] if len(parts0) > 1 else None
            main, extra, side = [], [], []
            source = "YDK"
            if url_or_none and (url_or_none.startswith("ydke://") or "ourygo" in url_or_none or "ourocg" in url_or_none):
                main, extra, side, source = await self._parse_deck_source(url_or_none)
            else:
                main, extra, side = self.ydk_manager.parse_ydk(rest)
        else:
            parts = text.split()
            url = parts[1] if len(parts) > 1 else ""
            if not url:
                await event.send(event.plain_result(
                    "用法:\\n1) /OCG导入卡组 <ourocg或ydke链接>\\n2) /OCG导入卡组\\n<粘贴YDK文本>"
                ))
                return
            main, extra, side, source = await self._parse_deck_source(url)
        if not main and not extra:
            await event.send(event.plain_result("❌ 解析结果为空，请检查格式"))
            return
        self.ydk_manager.save_ydk(main, extra, side, session_id)
        await event.send(event.plain_result(
            f"✅ [{source}] 导入成功 (M:{len(main)} E:{len(extra)} S:{len(side)})\\n可用 /OCG卡组图 查看"
        ))

    async def _parse_deck_source(self, url: str):
        if url.startswith("ydke://"):
            return (*self.ydk_manager.parse_ydke_url(url), "YDKe")
        if "ourygo" in url or "ourocg" in url:
            try:
                return (*self.ydk_manager.parse_ourocg_url(url), "Ourocg")
            except Exception as e:
                return [], [], [], f"ERR:{e}"
        return [], [], [], "UNKNOWN"

    @filter.command("OCG卡组图", alias=["/OCG卡组图", "/发送卡组图片"])
    async def handle_ocg_deck_image(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        session_id = self._get_session_id(event)
        ydk_path = os.path.join(self.ydk_manager.cache_dir, f"deck_{session_id}.ydk")
        if not os.path.exists(ydk_path):
            await event.send(event.plain_result("⚠️ 当前会话无卡组，请先 /OCG导入卡组"))
            return
        await event.send(event.plain_result("🎨 正在生成构筑图..."))
        img = await self.ydk_manager.draw_deck_image(session_id, "Deck")
        if img:
            await event.send(event.image_result(img))
        else:
            await event.send(event.plain_result("⚠️ 图片生成失败"))

    @filter.command("OCG起手", alias=["/OCG起手", "/卡组起手"])
    async def handle_ocg_hand_start(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        sender_id = self._get_uid(event)
        user_session = f"user_{sender_id}"
        main, _, _ = self.ydk_manager.load_last_ydk(user_session)
        if not main:
            group_id = getattr(event.message_obj, "group_id", None)
            if group_id and self.ydk_manager.copy_ydk_from_session(f"group_{group_id}", user_session):
                main, _, _ = self.ydk_manager.load_last_ydk(user_session)
                await event.send(event.plain_result("💡 已自动载入当前群聊卡组"))
        if not main:
            await event.send(event.plain_result("⚠️ 请先 /OCG导入卡组"))
            return
        self.duel_sim.init_duel(str(sender_id), main)
        hand = self.duel_sim.draw_card(str(sender_id), 5)
        img = await self.ydk_manager.draw_cards_image(hand, f"Hand ({len(hand)})")
        chain = [Comp.Plain(f"🎲 起手 5 张 (卡组 {len(main)})")]
        if img:
            chain.append(Comp.Image.fromFileSystem(img))
        await event.send(event.chain_result(chain))

    @filter.command("OCG抽卡", alias=["/OCG抽卡", "/卡组抽卡"])
    async def handle_ocg_draw(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        key = str(self._get_uid(event))
        state = self.duel_sim.get_state(key)
        if not state:
            await event.send(event.plain_result("请先 /OCG起手"))
            return
        if not state["deck"]:
            await event.send(event.plain_result("卡组已抽干"))
            return
        drawn = self.duel_sim.draw_card(key, 1)
        detail = await self.card_searcher.get_card_detail(drawn[0])
        name = detail.get("cn_name", "未知")
        img = await self.ydk_manager.draw_cards_image(drawn, name)
        chain = [Comp.Plain(f"🎴 抽到: {name} (剩余 {len(state['deck'])})")]
        if img:
            chain.append(Comp.Image.fromFileSystem(img))
        await event.send(event.chain_result(chain))

    @filter.command("OCG手牌", alias=["/OCG手牌", "/卡组状态"])
    async def handle_ocg_hand(self, event: AstrMessageEvent):
        if not self.ocg_on:
            return await self._deny_module(event, "OCG")
        key = str(self._get_uid(event))
        state = self.duel_sim.get_state(key)
        if not state:
            await event.send(event.plain_result("请先 /OCG起手"))
            return
        hand = state["hand"]
        img = await self.ydk_manager.draw_cards_image(hand, f"Hand {len(hand)} | Deck {len(state['deck'])}")
        chain = [Comp.Plain(f"📊 手牌 {len(hand)} · 卡组 {len(state['deck'])}")]
        if img:
            chain.append(Comp.Image.fromFileSystem(img))
        await event.send(event.chain_result(chain))

    # ---------- MD / DL（同一套动词） ----------

    def _game_and_mod(self, which: str):
        which = which.upper()
        if which == "MD":
            return GameType.MASTER_DUEL, "MD", self.md_on
        return GameType.DUEL_LINKS, "DL", self.dl_on

    @filter.command("MD更新T表", alias=["/MD更新T表"])
    async def handle_md_tier_update(self, event: AstrMessageEvent):
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self.tier_handler.update_tier_list(event, GameType.MASTER_DUEL, "Master Duel")

    @filter.command("MD查T表", alias=["/MD查T表", "/MD查询T表"])
    async def handle_md_tier_query(self, event: AstrMessageEvent):
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self.tier_handler.query_tier_list(event, GameType.MASTER_DUEL, "Master Duel")

    @filter.command("DL更新T表", alias=["/DL更新T表"])
    async def handle_dl_tier_update(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self.tier_handler.update_tier_list(event, GameType.DUEL_LINKS, "Duel Links")

    @filter.command("DL查T表", alias=["/DL查T表", "/DL查询T表"])
    async def handle_dl_tier_query(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self.tier_handler.query_tier_list(event, GameType.DUEL_LINKS, "Duel Links")

    @filter.command("MD翻译T表", alias=["/MD翻译T表"])
    async def handle_md_tier_translate(self, event: AstrMessageEvent):
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self.tier_handler.translate_tier_list(event, GameType.MASTER_DUEL)

    @filter.command("DL翻译T表", alias=["/DL翻译T表"])
    async def handle_dl_tier_translate(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self.tier_handler.translate_tier_list(event, GameType.DUEL_LINKS)

    @filter.command("MD查卡组", alias=["/MD查卡组"])
    async def handle_md_deck(self, event: AstrMessageEvent):
        if not self.md_on:
            return await self._deny_module(event, "MD")
        await self._deck_breakdown(event, GameType.MASTER_DUEL, "MD")

    @filter.command("DL查卡组", alias=["/DL查卡组"])
    async def handle_dl_deck(self, event: AstrMessageEvent):
        if not self.dl_on:
            return await self._deny_module(event, "DL")
        await self._deck_breakdown(event, GameType.DUEL_LINKS, "DL")

    async def _deck_breakdown(self, event, game_type: GameType, tag: str):
        parts = event.get_message_str().strip().split(maxsplit=1)
        if len(parts) < 2:
            await event.send(event.plain_result(f"用法: /{tag}查卡组 <卡组名>\\n可先 /{tag}查T表 看名字"))
            return
        raw = parts[1]
        deck_name = self._resolve_deck_name(raw)
        if deck_name != raw:
            await event.send(event.plain_result(f"🔍 {raw} → {deck_name}"))
        else:
            await event.send(event.plain_result(f"🔍 [{tag}] 正在抓取【{deck_name}】..."))
        session_id = self._get_session_id(event)
        try:
            result = await self.deck_breakdown.fetch_deck_breakdown(deck_name, game_type, session_id)
            chain = []
            img = result.get("image_path")
            if img and os.path.exists(img):
                chain.append(Comp.Image.fromFileSystem(img))
            chain.append(Comp.Plain(result.get("text", "无数据")))
            await event.send(event.chain_result(chain))
        except Exception as e:
            logger.error(f"{tag}查卡组出错: {e}")
            await event.send(event.plain_result("查询过程中发生内部错误"))

    # ---------- PTCG ----------

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
        chain = []
        img = self.ptcg_searcher.image_url(detail)
        if img:
            try:
                chain.append(Comp.Image.fromURL(img))
            except Exception:
                pass
        chain.append(Comp.Plain(self.ptcg_searcher.format_detail(detail)))
        await event.send(event.chain_result(chain))

    @filter.command("PTCG查卡", alias=["/PTCG查卡", "/宝可梦查卡", "/查宝可梦"])
    async def handle_ptcg_search(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        user_id = self._get_uid(event)
        parts = event.get_message_str().strip().split()
        if len(parts) <= 1:
            await event.send(event.plain_result("用法: /PTCG查卡 <卡名>\\n例如: /PTCG查卡 喷火龙"))
            return
        raw = " ".join(parts[1:])
        query = self._resolve_ptcg_query(raw)
        if query != raw:
            await event.send(event.plain_result(f"🔍 中文识别: {raw} → {query}"))
        result = await self.ptcg_searcher.search(query, page=1)
        if "error" in result:
            await event.send(event.plain_result(f"❌ {result['error']}"))
            return
        results = result["all_results"]
        if len(results) == 1:
            await self._send_ptcg_detail(event, results[0]["id"])
            return
        self.ptcg_searcher.search_sessions[user_id] = {"results": results, "query": query}
        await event.send(event.plain_result(self.ptcg_searcher.format_search_page(result)))

    @filter.command("PTCG序号", alias=["/PTCG序号", "/宝可梦序号"])
    async def handle_ptcg_select(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        user_id = self._get_uid(event)
        parts = event.get_message_str().strip().split()
        if len(parts) < 2 or not parts[1].isdigit():
            await event.send(event.plain_result("用法: /PTCG序号 <序号>"))
            return
        if user_id not in self.ptcg_searcher.search_sessions:
            await event.send(event.plain_result("请先 /PTCG查卡"))
            return
        results = self.ptcg_searcher.search_sessions[user_id]["results"]
        num = int(parts[1])
        if 1 <= num <= len(results):
            await self._send_ptcg_detail(event, results[num - 1]["id"])
        else:
            await event.send(event.plain_result("序号超出范围"))

    @filter.command("PTCG换页", alias=["/PTCG换页", "/宝可梦换页"])
    async def handle_ptcg_page(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        user_id = self._get_uid(event)
        parts = event.get_message_str().strip().split()
        if len(parts) < 2 or not parts[1].isdigit():
            await event.send(event.plain_result("用法: /PTCG换页 <页码>"))
            return
        if user_id not in self.ptcg_searcher.search_sessions:
            await event.send(event.plain_result("没有进行中的搜索"))
            return
        all_r = self.ptcg_searcher.search_sessions[user_id]["results"]
        page = int(parts[1])
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

    @filter.command("PTCG卡图", alias=["/PTCG卡图", "/宝可梦高清卡图"])
    async def handle_ptcg_image(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        user_id = self._get_uid(event)
        if user_id not in self.ptcg_searcher.last_viewed:
            await event.send(event.plain_result("请先 /PTCG查卡"))
            return
        detail = self.ptcg_searcher.last_viewed[user_id].get("card_data") or {}
        img = self.ptcg_searcher.image_url(detail)
        if not img:
            await event.send(event.plain_result("未找到卡图"))
            return
        try:
            await event.send(event.image_result(img))
        except Exception:
            await event.send(event.plain_result(img))

    @filter.command("PTCG随机", alias=["/PTCG随机", "/随机宝可梦"])
    async def handle_ptcg_random(self, event: AstrMessageEvent):
        if not self.ptcg_on:
            return await self._deny_module(event, "PTCG")
        name = random.choice(list(POKEMON_CN_MAP.keys()))
        result = await self.ptcg_searcher.search(name, page=1)
        if "error" in result or not result.get("all_results"):
            await event.send(event.plain_result("随机失败，请稍后再试"))
            return
        pick = result["all_results"][0]
        for c in result["all_results"]:
            if c.get("name") == name:
                pick = c
                break
        await self._send_ptcg_detail(event, pick["id"])

    # ---------- 全局 ----------

    @filter.command("TCG状态", alias=["/TCG状态", "/模块状态", "/tcgstatus"])
    async def handle_status(self, event: AstrMessageEvent):
        rows = [
            ("OCG", self.ocg_on),
            ("MD", self.md_on),
            ("DL", self.dl_on),
            ("PTCG", self.ptcg_on),
        ]
        lines = ["📦 TCG工具箱 · 模块状态"]
        lines += [f"  {'✅' if on else '❌'} {n}" for n, on in rows]
        lines.append("\\n开关在 管理面板 → 插件配置 中修改")
        await event.send(event.plain_result("\\n".join(lines)))

    @filter.command("TCG帮助", alias=["/TCG帮助", "/游戏王帮助", "/tcghelp", "/帮助TCG"])
    async def handle_help(self, event: AstrMessageEvent):
        ocg = " ✅" if self.ocg_on else " ❌"
        md = " ✅" if self.md_on else " ❌"
        dl = " ✅" if self.dl_on else " ❌"
        pt = " ✅" if self.ptcg_on else " ❌"
        text = f"""TCG工具箱 v2.1.0
================================
全局
• /TCG帮助  /TCG状态

OCG 游戏王{ocg}
• /OCG查卡 <卡名>
• /OCG序号 <n>  /OCG换页 <n>
• /OCG卡图 [CID]  /OCG随机
• /OCG饼图[更新]
• /OCG禁卡表 [OCG|简中]
• /OCG点数更新
• /OCG卡组检查 [OCG|简中]
• /OCG导入卡组 <链接或YDK>
• /OCG卡组图
• /OCG起手  /OCG抽卡  /OCG手牌

MD Master Duel{md}
• /MD更新T表  /MD查T表
• /MD查卡组 <名>  /MD翻译T表

DL Duel Links{dl}
• /DL更新T表  /DL查T表
• /DL查卡组 <名>  /DL翻译T表

PTCG 宝可梦{pt}
• /PTCG查卡 <中/英卡名>
• /PTCG序号 <n>  /PTCG换页 <n>
• /PTCG卡图  /PTCG随机

风格: /模块 + 动词，四模块对齐
================================"""
        await event.send(event.plain_result(text))
