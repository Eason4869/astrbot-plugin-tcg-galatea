# -*- coding: utf-8 -*-
"""PTCG 查卡：TCGdex GraphQL 为主，pokemontcg.io 为备用。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import aiohttp

from astrbot.api.all import logger


# 常见宝可梦中英对照（简体），便于英文主库结果做中文提示
POKEMON_CN_MAP: Dict[str, str] = {
    "Charizard": "喷火龙",
    "Pikachu": "皮卡丘",
    "Bulbasaur": "妙蛙种子",
    "Ivysaur": "妙蛙草",
    "Venusaur": "妙蛙花",
    "Squirtle": "杰尼龟",
    "Wartortle": "卡咪龟",
    "Blastoise": "水箭龟",
    "Eevee": "伊布",
    "Vaporeon": "水伊布",
    "Jolteon": "雷伊布",
    "Flareon": "火伊布",
    "Espeon": "太阳伊布",
    "Umbreon": "月亮伊布",
    "Leafeon": "叶伊布",
    "Glaceon": "冰伊布",
    "Sylveon": "仙子伊布",
    "Mewtwo": "超梦",
    "Mew": "梦幻",
    "Lugia": "洛奇亚",
    "Ho-Oh": "凤王",
    "Rayquaza": "烈空坐",
    "Giratina": "骑拉帝纳",
    "Arceus": "阿尔宙斯",
    "Greninja": "甲贺忍蛙",
    "Lucario": "路卡利欧",
    "Garchomp": "烈咬陆鲨",
    "Dragonite": "快龙",
    "Tyranitar": "班基拉斯",
    "Metagross": "巨金怪",
    "Salamence": "暴飞龙",
    "Gengar": "耿鬼",
    "Snorlax": "卡比兽",
    "Gyarados": "暴鲤龙",
    "Machamp": "怪力",
    "Alakazam": "胡地",
    "Ninetales": "九尾",
    "Arcanine": "风速狗",
    "Sableye": "勾魂眼",
    "Roaring Moon": "轰鸣月",
    "Iron Valiant": "铁武者",
    "Koraidon": "故勒顿",
    "Miraidon": "密勒顿",
    "Ogerpon": "厄诡椪",
    "Terapagos": "太乐巴戈斯",
    "Raging Bolt": "猛雷鼓",
    "Walking Wake": "波荡水",
    "Iron Leaves": "铁树叶",
    "Chi-Yu": "古玉鱼",
    "Ting-Lu": "古鼎鹿",
    "Wo-Chien": "古简蜗",
    "Chien-Pao": "古剑豹",
    "Tatsugiri": "米立龙",
    "Dondozo": "吃吼霸",
    "Gholdengo": "赛富豪",
    "Glimmora": "晶光花",
    "Ceruledge": "苍炎刃鬼",
    "Armarouge": "红莲铠骑",
    "Meowscarada": "魔幻假面喵",
    "Skeledirge": "骨纹巨声鳄",
    "Quaquaval": "狂欢浪舞鸭",
    "Sprigatito": "新叶喵",
    "Fuecoco": "呆火鳄",
    "Quaxly": "润水鸭",
    "Mabosstiff": "獒教父",
    "Grafaiai": "涂标客",
    "Kingambit": "仆刀将军",
    "Annihilape": "弃世猴",
    "Clodsire": "土王",
    "Farigiraf": "奇麒麟",
    "Dudunsparce": "土龙节节",
    "Cetitan": "冻原熊",
    "Baxcalibur": "戟脊龙",
    "Dragapult": "多龙巴鲁托",
    "Cinderace": "闪焰王牌",
    "Rillaboom": "轰擂金刚猩",
    "Inteleon": "千面避役",
    "Zacian": "苍响",
    "Zamazenta": "藏玛然特",
    "Eternatus": "无极汰那",
    "Calrex-Shadow Rider": "骑拉帝纳",
    "Rapid Strike Urshifu": "连击武道熊师",
    "Single Strike Urshifu": "一击武道熊师",
    "Shadow Rider Calyrex": "白马蕾冠王",
    "Ice Rider Calyrex": "黑马蕾冠王",
    "Regieleki": "雷吉艾勒奇",
    "Regidrago": "雷吉铎拉戈",
    "Glastrier": "雪暴马",
    "Spectrier": "灵幽马",
    "Kyogre": "盖欧卡",
    "Groudon": "固拉多",
    "Dialga": "帝牙卢卡",
    "Palkia": "帕路奇亚",
    "Darkrai": "达克莱伊",
    "Genesect": "盖诺赛克特",
    "Deoxys": "代欧奇希斯",
    "Xerneas": "哲尔尼亚斯",
    "Yveltal": "伊裴尔塔尔",
    "Solgaleo": "索尔迦雷欧",
    "Lunaala": "露奈雅拉",
    "Necrozma": "奈克洛兹玛",
    "Zacian-Crowned": "剑之王苍响",
    "Zamazenta-Crowned": "盾之王藏玛然特",
}


TYPE_CN = {
    "Fire": "火",
    "Water": "水",
    "Grass": "草",
    "Lightning": "雷",
    "Psychic": "超能",
    "Fighting": "斗",
    "Darkness": "恶",
    "Metal": "钢",
    "Dragon": "龙",
    "Fairy": "妖精",
    "Colorless": "无色",
    "None": "无色",
}

STAGE_CN = {
    "Basic": "基础",
    "Stage1": "一阶进化",
    "Stage2": "二阶进化",
    "VMAX": "VMAX",
    "VSTAR": "VSTAR",
    "V-UNION": "V-UNION",
    "BREAK": "BREAK",
}

CATEGORY_CN = {
    "Pokemon": "宝可梦",
    "Trainer": "训练家",
    "Energy": "能量",
}

RARITY_CN = {
    "Common": "普通",
    "Uncommon": "非普通",
    "Rare": "稀有",
    "Rare Holo": "稀有闪",
    "Rare Holo EX": "稀有闪EX",
    "Rare Holo GX": "稀有闪GX",
    "Rare Holo V": "稀有闪V",
    "Rare Holo VMAX": "稀有闪VMAX",
    "Rare Holo VSTAR": "稀有闪VSTAR",
    "Rare Rainbow": "稀有彩虹",
    "Rare Secret": "稀有秘稀",
    "Rare Ultra": "稀有Ultra",
    "Amazing Rare": "特别稀有",
    "Radiant Rare": "光泽稀有",
    "ACE SPEC Rare": "ACE SPEC",
    "Promo": "宣传卡",
    "LEGEND": "LEGEND",
}


def _cn_or_self(en: Optional[str]) -> str:
    if not en:
        return "-"
    return f"{en} ({POKEMON_CN_MAP[en]})" if en in POKEMON_CN_MAP else en


class PTCGSearcher:
    """基于 TCGdex GraphQL / pokemontcg.io 的宝可梦卡牌查询器。"""

    TCGDEX_GQL = "https://api.tcgdex.net/v2/graphql"
    TCGDEX_REST = "https://api.tcgdex.net/v2/en"
    POKEMONTCG = "https://api.pokemontcg.io/v2"

    CARD_GQL_FIELDS = """
    id name hp types rarity category illustrator stage evolveFrom
    description retreat trainerType energyType effect
    attacks { name damage cost effect }
    abilities { name type effect }
    weaknesses { type value }
    resistances { type value }
    set { id name cardCount { official total } }
    image legal { standard expanded }
    """

    def __init__(self, api_key: str = ""):
        self.api_key = (api_key or "").strip()
        headers = {"User-Agent": "AstrBot-TCG-Galatea/2.0"}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        self.session = aiohttp.ClientSession(
            trust_env=True,
            headers=headers,
        )
        self.search_sessions: Dict[str, Dict[str, Any]] = {}
        self.last_viewed: Dict[str, Dict[str, Any]] = {}

    async def close(self):
        if self.session:
            await self.session.close()

    # ---------- 公共入口 ----------

    async def search(self, query: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """按名称模糊搜索，返回 {results, page, total_pages, total, source}"""
        results = await self._search_tcgdex(query)
        source = "TCGdex"
        if not results:
            results = await self._search_pokemontcg(query)
            source = "PokémonTCG"
        if not results:
            return {"error": f"未找到与「{query}」相关的宝可梦卡牌"}

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
            "source": source,
            "query": query,
        }

    async def get_detail(self, card_id: str) -> Dict[str, Any]:
        detail = await self._detail_tcgdex(card_id)
        if not detail:
            detail = await self._detail_pokemontcg(card_id)
        return detail or {"error": f"获取卡片 {card_id} 详情失败"}

    def format_search_page(self, data: Dict[str, Any], cmd: str = "PTCG") -> str:
        results = data["results"]
        lines = [
            f"🔍 PTCG 搜索结果 (第 {data['page']}/{data['total_pages']} 页，共 {data['total']} 个)",
            f"📦 数据源: {data['source']}",
            "",
        ]
        base = (data["page"] - 1) * data["page_size"]
        for i, card in enumerate(results, start=base + 1):
            cn = POKEMON_CN_MAP.get(card.get("name", ""), "")
            name = card.get("name", "?")
            if cn:
                name = f"{name}/{cn}"
            cat = CATEGORY_CN.get(card.get("category", ""), card.get("category", ""))
            set_name = (card.get("set") or {}).get("name", "")
            local = card.get("localId") or card.get("number") or ""
            lines.append(f"{i}. {name} [{cat}] {set_name} #{local}")
        lines.append("")
        lines.append(f"💡 /{cmd} 序号 <序号> 查看详情 · /{cmd} 换页 <页码> 切换")
        return "\n".join(lines)

    def format_detail(self, card: Dict[str, Any]) -> str:
        if "error" in card:
            return card["error"]
        try:
            name_en = card.get("name", "未知")
            cn = POKEMON_CN_MAP.get(name_en, "")
            name_disp = f"{name_en} ({cn})" if cn else name_en
            info: List[str] = []
            info.append(f"🃏 名称: {name_disp}")
            info.append(f"🆔 ID: {card.get('id', '未知')}")

            category = card.get("category", "")
            if category:
                info.append(
                    f"🏷 分类: {CATEGORY_CN.get(category, category)}"
                )

            types = card.get("types") or []
            if types:
                t_disp = "/".join(TYPE_CN.get(t, t) for t in types)
                info.append(f"⚡ 属性: {t_disp}")

            if card.get("hp"):
                info.append(f"❤️ HP: {card['hp']}")

            stage = card.get("stage")
            if stage:
                stage_disp = STAGE_CN.get(stage, stage)
                if card.get("evolveFrom"):
                    stage_disp += f" (进化自 {card['evolveFrom']})"
                info.append(f"📈 进化: {stage_disp}")

            if card.get("trainerType"):
                info.append(f"🎓 训练家类型: {card['trainerType']}")

            if card.get("energyType"):
                info.append(f"🔋 能量类型: {card['energyType']}")

            retreat = card.get("retreat")
            if retreat is not None:
                info.append(f"👣 撤退费: {retreat}")

            rarity = card.get("rarity")
            if rarity:
                info.append(f"💎 稀有度: {RARITY_CN.get(rarity, rarity)}")

            abilities = card.get("abilities") or []
            if abilities:
                info.append("")
                info.append("✨ 特性:")
                for ab in abilities:
                    info.append(
                        f"  · [{ab.get('type', '')}] {ab.get('name', '')}: {ab.get('effect', '')}"
                    )

            attacks = card.get("attacks") or []
            if attacks:
                info.append("")
                info.append("💥 招式:")
                for at in attacks:
                    cost = at.get("cost") or []
                    cost_s = "/".join(TYPE_CN.get(c, c) for c in cost) if cost else "无"
                    dmg = at.get("damage") or "-"
                    effect = at.get("effect") or ""
                    line = f"  · {at.get('name', '?')} [{cost_s}] 伤害{dmg}"
                    if effect:
                        line += f"\n    {effect}"
                    info.append(line)

            weaknesses = card.get("weaknesses") or []
            if weaknesses:
                w = ", ".join(f"{TYPE_CN.get(x.get('type', ''), x.get('type', ''))}{x.get('value', '')}" for x in weaknesses)
                info.append(f"🔻 弱点: {w}")

            resistances = card.get("resistances") or []
            if resistances:
                r = ", ".join(f"{TYPE_CN.get(x.get('type', ''), x.get('type', ''))}{x.get('value', '')}" for x in resistances)
                info.append(f"🔺 抵抗: {r}")

            desc = card.get("description") or card.get("flavorText") or ""
            if desc:
                info.append(f"\n📖 描述:\n{desc}")

            effect = card.get("effect")
            if effect:
                info.append(f"\n📜 效果:\n{effect}")

            s = card.get("set") or {}
            if s.get("name"):
                info.append(f"\n📦 卡包: {s.get('name')} ({s.get('id', '')})")

            legal = card.get("legal") or {}
            legal_tags = []
            if legal.get("standard"):
                legal_tags.append("标准")
            if legal.get("expanded"):
                legal_tags.append("扩展")
            if legal_tags:
                info.append(f"⚖️ 赛制: {'/'.join(legal_tags)}")

            if card.get("illustrator"):
                info.append(f"🎨 画师: {card['illustrator']}")

            return "\n".join(info)
        except Exception as e:
            logger.error(f"PTCG 格式化出错: {e}")
            return f"格式化出错: {e}"

    def format_search_results_alias(self, results: List[Dict], page: int) -> str:
        """兼容原插件风格的分页输出。"""
        page_size = 10
        total = len(results)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, total)
        lines = [
            f"🔍 PTCG 搜索结果 (第 {page}/{total_pages} 页，共 {total} 个):\n"
        ]
        for i, card in enumerate(results[start:end], start=start + 1):
            name = card.get("name", "?")
            cn = POKEMON_CN_MAP.get(name, "")
            tag = f"/{cn}" if cn else ""
            cat = CATEGORY_CN.get(card.get("category", ""), card.get("category", ""))
            lines.append(f"{i}. {name}{tag} [{cat}]")
        lines.append(
            "\n💡 /PTCG 序号 [序号] 查看详情，/PTCG 换页 [页码] 切换页面"
        )
        return "\n".join(lines)

    def image_url(self, card: Dict[str, Any]) -> Optional[str]:
        """返回可直接打开的图片地址。

        TCGdex 资产无扩展名无法访问，需补 /high.png 或 /low.png。
        """
        url = (card.get("image") or "").strip()
        if not url:
            # pokemontcg 风格兜底
            card_id = card.get("id", "")
            number = card.get("localId") or card.get("number")
            if card_id and "-" in card_id and number:
                set_id = card_id.rsplit("-", 1)[0]
                return f"https://images.pokemontcg.io/{set_id}/{number}.png"
            return None
        if not url.startswith("http"):
            return None
        # 已是可访问的完整文件
        if url.endswith((".png", ".jpg", ".jpeg", ".webp")):
            return url
        # TCGdex assets: .../en/swsh/xxx/1 -> .../high.png
        if "assets.tcgdex.net" in url:
            return url.rstrip("/") + "/high.png"
        return url

    # ---------- TCGdex ----------

    async def _search_tcgdex(self, query: str) -> List[Dict[str, Any]]:
        q = query.strip()
        if not q:
            return []
        # 先精确，再取前缀通配（pokemontcg 风格兼容）
        candidates = [q]
        if not q.endswith("*"):
            candidates.append(f"{q}*")

        seen: Dict[str, Dict] = {}
        for term in candidates:
            gql = (
                "{ cards(filters: { name: %s }, pagination: { page: 1, itemsPerPage: 25 }) {"
                " id name hp types rarity category set { id name } localId image "
                "} }"
            ) % _gql_str(term)
            data = await self._gql(gql)
            if not data:
                continue
            for c in data.get("cards") or []:
                cid = c.get("id")
                if cid and cid not in seen:
                    c.setdefault("localId", _local_id_from_set_and_id(c))
                    seen[cid] = c
        return list(seen.values())

    async def _detail_tcgdex(self, card_id: str) -> Optional[Dict[str, Any]]:
        gql = (
            "{ card(id: %s) { %s } }"
        ) % (_gql_str(card_id), self.CARD_GQL_FIELDS.strip())
        data = await self._gql(gql)
        if not data:
            return None
        card = data.get("card")
        if not card:
            return None
        card["source"] = "TCGdex"
        return card

    async def _gql(self, query: str) -> Optional[Dict[str, Any]]:
        payload = {"query": query}
        try:
            async with self.session.post(
                self.TCGDEX_GQL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"TCGdex GraphQL HTTP {resp.status}")
                    return None
                body = await resp.json(content_type=None)
                if body.get("errors"):
                    logger.warning(f"TCGdex GraphQL errors: {body['errors']}")
                return body.get("data")
        except Exception as e:
            logger.warning(f"TCGdex GraphQL 请求失败: {e}")
            return None

    # ---------- pokemontcg.io ----------

    async def _search_pokemontcg(self, query: str) -> List[Dict[str, Any]]:
        q = query.strip().strip('"')
        if not q:
            return []
        # 无 key 时精确 name 查询易 500，优先用前缀通配
        query_strategies = [
            f'name:"{q}"',
            f"name:{q}*",
            f"name:{q.replace(' ', '-')}*",
        ]
        for qs in query_strategies:
            try:
                url = f"{self.POKEMONTCG}/cards"
                params = {
                    "q": qs,
                    "pageSize": 25,
                    "select": "id,name,hp,types,rarity,supertype,subtypes,set,number,images",
                }
                async with self.session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=25),
                    ssl=False,
                ) as resp:
                    if resp.status != 200:
                        continue
                    body = await resp.json(content_type=None)
                    items = body.get("data") or []
                    if items:
                        return [
                            {
                                "id": c.get("id"),
                                "name": c.get("name"),
                                "hp": _to_int(c.get("hp")),
                                "types": c.get("types") or [],
                                "rarity": c.get("rarity") or "",
                                "category": _map_supertype(c.get("supertype")),
                                "set": {
                                    "id": (c.get("set") or {}).get("id"),
                                    "name": (c.get("set") or {}).get("name"),
                                },
                                "localId": c.get("number"),
                                "image": ((c.get("images") or {}).get("small"))
                                or ((c.get("images") or {}).get("large")),
                                "source": "PokémonTCG",
                            }
                            for c in items
                        ]
            except Exception as e:
                logger.warning(f"pokemontcg 搜索失败 ({qs}): {e}")
                continue
        return []

    async def _detail_pokemontcg(self, card_id: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.POKEMONTCG}/cards/{card_id}"
            async with self.session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=25),
                ssl=False,
            ) as resp:
                if resp.status != 200:
                    return None
                body = await resp.json(content_type=None)
                c = body.get("data")
                if not c:
                    return None
                attacks = []
                for a in c.get("attacks") or []:
                    attacks.append(
                        {
                            "name": a.get("name"),
                            "damage": a.get("damage") or "",
                            "cost": a.get("cost") or [],
                            "effect": a.get("text") or "",
                        }
                    )
                abilities = []
                for a in c.get("abilities") or []:
                    abilities.append(
                        {
                            "name": a.get("name"),
                            "type": a.get("type") or "",
                            "effect": a.get("text") or "",
                        }
                    )
                weaknesses = [
                    {"type": w.get("type"), "value": w.get("value") or ""}
                    for w in c.get("weaknesses") or []
                ]
                resistances = [
                    {"type": w.get("type"), "value": w.get("value") or ""}
                    for w in c.get("resistances") or []
                ]
                s = c.get("set") or {}
                images = c.get("images") or {}
                legal = c.get("legalities") or {}
                return {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "hp": _to_int(c.get("hp")),
                    "types": c.get("types") or [],
                    "rarity": c.get("rarity") or "",
                    "category": _map_supertype(c.get("supertype")),
                    "illustrator": c.get("artist"),
                    "stage": _map_stage(c.get("subtypes") or []),
                    "evolveFrom": c.get("evolvesFrom") or "",
                    "description": c.get("flavorText") or "",
                    "retreat": c.get("convertedRetreatCost"),
                    "attacks": attacks,
                    "abilities": abilities,
                    "weaknesses": weaknesses,
                    "resistances": resistances,
                    "set": {"id": s.get("id"), "name": s.get("name")},
                    "image": images.get("large") or images.get("small"),
                    "legal": {
                        "standard": str(legal.get("standard", "")).lower() == "legal",
                        "expanded": str(legal.get("expanded", "")).lower() == "legal",
                    },
                    "source": "PokémonTCG",
                }
        except Exception as e:
            logger.warning(f"pokemontcg 详情失败: {e}")
            return None


def _gql_str(s: str) -> str:
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _to_int(v: Any) -> Optional[int]:
    try:
        return int(str(v).strip())
    except Exception:
        return None


def _map_supertype(st: Optional[str]) -> str:
    if not st:
        return ""
    st = st.lower()
    if "pok" in st:
        return "Pokemon"
    if "trainer" in st:
        return "Trainer"
    if "energy" in st:
        return "Energy"
    return st


def _map_stage(subtypes: List[str]) -> str:
    for s in subtypes:
        sl = s.lower().replace(" ", "")
        if sl in ("basic", "stage1", "stage2", "vmax", "vstar", "v-union", "break"):
            return sl.replace("stage1", "Stage1").replace("stage2", "Stage2").replace(
                "basic", "Basic"
            ).replace("vmax", "VMAX").replace("vstar", "VSTAR").replace(
                "v-union", "V-UNION"
            ).replace("break", "BREAK")
    return ""


def _local_id_from_set_and_id(card: Dict[str, Any]) -> str:
    cid = card.get("id") or ""
    if "-" in cid:
        return cid.rsplit("-", 1)[-1]
    return card.get("localId") or ""
