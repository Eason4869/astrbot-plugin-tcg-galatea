"""VG 查卡：Cardfight!! Vanguard Fandom MediaWiki API。

与 OCG / PTCG 完全隔离：独立 aiohttp session、独立会话缓存、独立格式化。
不 import 也不依赖 YugiohCardSearcher / PTCGSearcher。
"""

from __future__ import annotations

import asyncio
import random
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import aiohttp

from astrbot.api.all import logger


# 常用卡（随机指令稳定池），英文页面标题
VG_POPULAR = [
    "Blaster Blade",
    "Blaster Dark",
    "Dragon Knight, Altmile",
    "Star-vader, Chaos Break Dragon",
    "Dragonic Overlord",
    "Seeker, Thing Saver Dragon",
    "Golden Dragon, Ezel",
    "Monarch, Alfred Holy",
    "Meteokaiser, Vic-Ten",
    "Super Deletor, Greion",
    "Chronojet Dragon",
    "Ahsha",
    "Luard",
    "Shirayuki",
    "Bastion",
    "Youthberk",
    "Viamance Bellijaziel",
    "Flagburg Dragon",
    "Lianorn",
    "Zorga",
]


CLAN_HINT = {
    "royal paladin": "皇家骑士",
    "shadow paladin": "暗影骑士",
    "gold paladin": "黄金骑士",
    "keter sanctuary": "天轮圣域",
    "dragon empire": "龙帝",
    "dark states": "暗邦",
    "brandt gate": "布兰特之门",
    "stoicheia": "树角",
    "lyrical monasterio": "里里卡尔",
    "angel feather": "天使羽翼",
    "nova grappler": "新星",
    "dimension police": "次元警察",
    "narukami": "鸣神",
    "tachikaze": "太刀风",
    "murakumo": "丛云",
    "nubatama": "努巴塔",
    "aqua force": "水波骑士",
    "aqua force blue wave": "水波骑士",
    "genesis": "创世",
    "oracle think tank": "智慧女神",
    "link joker": "连接者",
    "gear chronicle": "齿轮编年史",
    "great nature": "大天然",
    "mega colony": "超级殖民地",
    "spike brothers": "尖钉兄弟",
    "dark irregulars": "黑暗不法者",
    "bermuda triangle": "百慕大三角",
    "granblue": "骸骨",
    "pale moon": "苍白之月",
    "gold paladin liberation": "黄金骑士",
    "zoo": "动物园",
    "star gate": "星门",
    "dragon empire nation": "龙帝",
}


def _strip_wiki(text: str) -> str:
    if not text:
        return ""
    s = text
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = s.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("'''''", "").replace("'''", "").replace("''", "")
    s = re.sub(r"\{\{[^}]+\}\}", "", s)
    return s.strip()


def _parse_cardtable(wikidata: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    for m in re.finditer(r"\|\s*([a-zA-Z0-9_]+)\s*=\s*([^|\n]+)", wikidata or ""):
        k = m.group(1).strip().lower()
        v = m.group(2).strip()
        if k and k not in fields:
            fields[k] = v
    return fields


def _first_set_id(fields: Dict[str, str]) -> str:
    for i in range(1, 12):
        raw = fields.get(f"set{i}") or ""
        if not raw:
            continue
        first = re.split(r"<br\s*/?>", raw, maxsplit=1)[0]
        first = first.strip()
        # e.g. TD01/005EN or BT01/002 (RRR)
        first = re.sub(r"\s*\(.*\)$", "", first).strip()
        if first:
            return first
    return ""


def _clan_cn(clan: str) -> str:
    if not clan:
        return ""
    low = clan.lower()
    for en, cn in CLAN_HINT.items():
        if en in low:
            return f"{clan}（{cn}）"
    return clan


class VGSearcher:
    """Cardfight!! Vanguard 查询器（Fandom Wiki API）。"""

    API = "https://cardfight.fandom.com/api.php"
    IMG_BASE = "https://static.wikia.nocookie.net/cardfight/images/"

    def __init__(self):
        self.session = aiohttp.ClientSession(
            trust_env=True,
            headers={"User-Agent": "AstrBot-TCG-Galatea/1.0.5"},
        )
        self.search_sessions: Dict[str, Dict[str, Any]] = {}
        self.last_viewed: Dict[str, Dict[str, Any]] = {}
        # page title -> cached parse payload
        self._detail_cache: Dict[str, Dict[str, Any]] = {}

    async def close(self):
        if self.session:
            await self.session.close()

    # ---------- HTTP ----------

    async def _api(self, params: Dict[str, Any], timeout: int = 15) -> Optional[dict]:
        q = {"format": "json", **params}
        try:
            async with self.session.get(
                self.API, params=q, timeout=aiohttp.ClientTimeout(total=timeout), ssl=False
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"VG fandom API HTTP {resp.status}")
                    return None
                return await resp.json(content_type=None)
        except Exception as e:
            logger.warning(f"VG fandom API 失败: {e}")
            return None

    async def search(self, query: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        q = (query or "").strip()
        if not q:
            return {"error": "搜索词为空"}
        data = await self._api(
            {"action": "query", "list": "search", "srsearch": q, "srlimit": 50}
        )
        if not data:
            return {"error": "Fandom 接口请求失败"}
        hits = (data.get("query") or {}).get("search") or []
        results: List[Dict[str, Any]] = []
        for h in hits:
            title = h.get("title") or ""
            if not title:
                continue
            # 过滤明显非卡表页
            low = title.lower()
            if low.startswith("card trivia") or low.startswith("card gallery"):
                continue
            if low.startswith("episode") or low.startswith("chapter"):
                continue
            snippet = _strip_wiki(h.get("snippet") or "")
            results.append(
                {
                    "id": title,  # fandom page title 作为稳定 id
                    "name": title,
                    "snippet": snippet[:80],
                }
            )
        if not results:
            return {"error": f"未找到与「{q}」相关的先导者卡牌"}

        total = len(results)
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "results": results[start:end],
            "all_results": results,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "source": "Fandom",
            "query": q,
        }

    async def get_detail(self, page_title: str) -> Dict[str, Any]:
        title = (page_title or "").strip()
        if not title:
            return {"error": "卡片标题为空"}
        if title in self._detail_cache:
            return dict(self._detail_cache[title])

        data = await self._api(
            {"action": "parse", "page": title, "prop": "wikitext|images"}
        )
        if not data or "parse" not in data:
            return {"error": f"获取「{title}」详情失败"}
        parse = data["parse"]
        wt = (parse.get("wikitext") or {}).get("*") or ""
        fields = _parse_cardtable(wt)
        if not fields and "CardTable" not in wt:
            # 可能是消歧义 / 角色页
            return {"error": f"「{title}」不是卡片页，请用更精确的卡名或卡包编号搜索"}

        images = parse.get("images") or []
        en_img_name = (fields.get("enimage") or "").strip()
        jp_img_name = (fields.get("jpimage") or "").strip()
        pick_img = en_img_name or jp_img_name
        if not pick_img:
            for im in images:
                low = im.lower()
                if low.endswith((".png", ".jpg", ".jpeg", ".webp")) and "logo" not in low:
                    pick_img = im
                    break
            if not pick_img and images:
                pick_img = images[0]

        direct_img = ""
        if pick_img:
            direct_img = await self._resolve_image_url(pick_img)

        detail = {
            "id": title,
            "name": title,
            "kana": fields.get("kana", ""),
            "phonetic": fields.get("phonetic", ""),
            "grade": fields.get("grade", ""),
            "power": fields.get("power", ""),
            "shield": fields.get("shield", ""),
            "clan": fields.get("clan", ""),
            "race": fields.get("race", ""),
            "arch": fields.get("arch", ""),
            "effect": _strip_wiki(fields.get("effect", "")),
            "flavor": _strip_wiki(fields.get("flavor", "")),
            "set_id": _first_set_id(fields),
            "image_file": pick_img,
            "image_url": direct_img,
            "source": "Fandom",
            "url": f"https://cardfight.fandom.com/wiki/{quote(title.replace(' ', '_'))}",
        }
        self._detail_cache[title] = detail
        return dict(detail)

    async def _resolve_image_url(self, filename: str) -> str:
        """File: 名 → static.wikia.nocookie.net 直链（QQ 侧更稳）。"""
        fname = (filename or "").strip()
        if not fname:
            return ""
        data = await self._api(
            {
                "action": "query",
                "titles": "File:" + fname,
                "prop": "imageinfo",
                "iiprop": "url",
            }
        )
        if not data:
            return ""
        pages = (data.get("query") or {}).get("pages") or {}
        for p in pages.values():
            infos = p.get("imageinfo") or []
            if infos:
                url = (infos[0] or {}).get("url") or ""
                if url:
                    return url
        return ""

    def image_url(self, card: Dict[str, Any]) -> Optional[str]:
        # 1) 已解析的 CDN 直链
        direct = (card.get("image_url") or "").strip()
        if direct:
            return direct
        # 2) 按文件名再拼 FilePath（会 302，作兜底）
        fname = (card.get("image_file") or "").strip()
        if not fname:
            return None
        return (
            "https://cardfight.fandom.com/wiki/Special:FilePath/"
            + quote(fname.replace(" ", "_"))
        )

    # ---------- 展示 ----------

    def format_search_page(self, data: Dict[str, Any], cmd: str = "VG") -> str:
        results = data["results"]
        lines = [
            f"🔍 VG 搜索结果 (第 {data['page']}/{data['total_pages']} 页，共 {data['total']} 个)",
            f"📦 数据源: {data.get('source', 'Fandom')}",
            "",
        ]
        base = (data["page"] - 1) * data["page_size"]
        for i, card in enumerate(results, start=base + 1):
            name = card.get("name", "?")
            snip = card.get("snippet") or ""
            extra = f" · {snip}" if snip else ""
            lines.append(f"{i}. {name}{extra}")
        lines.append("")
        lines.append(f"💡 /{cmd} 序号 <序号> 查看详情 · /{cmd} 换页 <页码> 切换")
        return "\n".join(lines)

    def format_detail(self, card: Dict[str, Any]) -> str:
        if "error" in card:
            return card["error"]
        try:
            info: List[str] = []
            name = card.get("name", "未知")
            info.append(f"🃏 名称: {name}")
            if card.get("kana"):
                info.append(f"🇯🇵 假名: {card['kana']}")
            if card.get("set_id"):
                info.append(f"🆔 编号: {card['set_id']}")

            if card.get("grade"):
                info.append(f"📊 等级: G{card['grade']}")
            if card.get("power"):
                info.append(f"💪 力量: {card['power']}")
            if card.get("shield"):
                info.append(f"🛡 护盾: {card['shield']}")

            clan = card.get("clan") or ""
            if clan:
                info.append(f"🏛 集团: {_clan_cn(clan)}")
            if card.get("race"):
                info.append(f"🐾 种族: {card['race']}")
            if card.get("arch"):
                info.append(f"🔖 字段: {card['arch']}")

            effect = card.get("effect") or ""
            if effect:
                info.append("")
                info.append("📜 效果:")
                info.append(effect)

            flavor = card.get("flavor") or ""
            if flavor:
                info.append("")
                info.append(f"📖 风味:\n{flavor}")

            return "\n".join(info)
        except Exception as e:
            logger.error(f"VG 格式化出错: {e}")
            return f"格式化出错: {e}"

    async def random_card(self) -> Dict[str, Any]:
        """从常用卡池随机一张，保证详情可解析。"""
        pool = list(VG_POPULAR)
        random.shuffle(pool)
        for name in pool:
            try:
                detail = await self.get_detail(name)
                if "error" not in detail:
                    return detail
                # 精确标题失败则搜索再取第一条
                result = await self.search(name, page=1)
                results = result.get("all_results") or []
                if results:
                    detail = await self.get_detail(results[0]["id"])
                    if "error" not in detail:
                        return detail
            except Exception as e:
                logger.warning(f"VG 随机 {name}: {e}")
            await asyncio.sleep(0.15)
        return {"error": "随机失败，请稍后再试"}
