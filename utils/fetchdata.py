from cachetools import TTLCache
import aiohttp
from fake_useragent import UserAgent
import discord
from math import ceil
from io import BytesIO
from utils.fetchimage import merge_icons #自製模組

cache = TTLCache(maxsize=100, ttl=60)

async def fetchdata(url: str, ignorecache: bool):  
    headers = {"User-Agent": UserAgent().random}
    if url in cache and not ignorecache:
        print(f"從快取中讀取資料: {url}")
        return cache[url]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=5) as response:
                data = await response.json()
                if not data.get("success", True):
                    error_msg = data.get("error").get("msg")
                    print(f"API 回應錯誤: {error_msg}")
                    return None
                cache[url] = data
                return data
    except Exception as e:
        print(f"fetchdata炸了: {e}")
        raise

async def create_embed(record_data: dict, user_data: dict, gamemode: str, username: str):
    try:
        entries = record_data.get("data").get("entries")
        replayid = entries[0].get("replayid")
        user_id = user_data.get("data").get("_id")
        avatar_revision = user_data.get("data").get("avatar_revision")

        embed = discord.Embed(
            title=f"{username}'s {gamemode} record", 
            url=f"https://tetr.io/#R:{replayid}", 
            description="click title to watch replay in tetrio"
        )
        if avatar_revision: 
            embed.set_thumbnail(url=f"https://tetr.io/user-content/avatars/{user_id}.jpg?rv={avatar_revision}")
        else: 
            embed.set_thumbnail(url="https://tetr.io/res/avatar.png") #改用anonymous的頭像
        #40l
        stats = entries[0].get("results").get("stats")
        pps = round(entries[0].get("results").get("aggregatestats").get("pps"), 2)
        finaltime = stats.get("finaltime") / 1000
        kpp = round((stats.get("inputs")) / (stats.get("piecesplaced")), 2)
        holds = stats.get("holds")
        piecesplaced = stats.get("piecesplaced")
        finesse = stats.get("finesse").get("faults")
        #blz
        score = stats.get("score")
        level = stats.get("level")
        spp = round(score / piecesplaced, 2)
        perfectclear = stats.get("clears").get("allclear")
        #qpl
        zenith = stats.get("zenith")
        altitude = round(zenith.get("altitude"), 1)
        apm = round(entries[0].get("results").get("aggregatestats").get("apm"), 2)
        floor = zenith.get("floor")
        spdrun = zenith.get("splits")[8]
        peakrank = int(zenith.get("peakrank"))
        avgrankpts = zenith.get("avgrankpts")
        avgcsp = round(avgrankpts / finaltime / 60, 2)
        topbtb = stats.get("topbtb") - 1
        received = stats.get("garbage").get("received")
        kills = stats.get("kills")
        finaltime_tuple = divmod(finaltime, 60)
        if gamemode == "40l":
            embed.add_field(name=" pps ", value=pps, inline=True)
            embed.add_field(name=" finaltime ", value=f"{finaltime:.3f}s", inline=True)
            embed.add_field(name=" kpp ", value=kpp, inline=True)
            embed.add_field(name=" holds ", value=holds, inline=True)
            embed.add_field(name=" pieces ", value=piecesplaced, inline=True)
            embed.add_field(name=" finesse faults ", value=finesse, inline=True)
            embed.set_image(url="https://img.littlezhaidi.me/40l.png") 
        elif gamemode == "blitz":
            embed.add_field(name=" score ", value=score, inline=True)
            embed.add_field(name=" level ", value=level, inline=True)
            embed.add_field(name=" pps ", value=pps, inline=True)
            embed.add_field(name=" pieces ", value=piecesplaced, inline=True)
            embed.add_field(name=" score per piece ", value=spp, inline=True)
            embed.add_field(name=" perfect clears ", value=perfectclear, inline=True)
            embed.set_image(url="https://img.littlezhaidi.me/blitz.png")
        else: #zenith
            mods = entries[0].get("extras").get("zenith").get("mods")
            if stats.get("speedrun") and gamemode == "zenith":
                embed.add_field(name=" ZENITH SPEEDRUN ", value=spdrun)
            embed.add_field(name=" altitude ", value=f"**{altitude}m, F{floor}**", inline=True)
            embed.add_field(name=" pps ", value=f"**{pps}**", inline=True)
            embed.add_field(name=" apm ", value=f"**{apm}**", inline=True)
            embed.add_field(name=" avg. climb speed ", value=f"**{avgcsp}**" , inline=True)
            embed.add_field(name=" peak climb speed ", value=f"**{peakrank}**" , inline=True)
            embed.add_field(name=" finaltime ", value=f"**{int(finaltime_tuple[0])}m{ceil(finaltime_tuple[1])}s**" , inline=True)
            embed.add_field(name=" maximum b2b chain ", value=f"**{topbtb}**" , inline=True)
            embed.add_field(name=" lines received ", value=f"**{received}**" , inline=True)
            embed.add_field(name=" KOs ", value=f"**{kills}**" , inline=True)
            if mods:
                merge_icons(mods)
                embed.add_field(name="", value="** mods **")
                embed.set_image(url="attachment://combined.png")
            else:
                embed.set_image(url="https://img.littlezhaidi.me/quickplay.png")
    except Exception:
        raise
    return embed
async def save_replay(replayid: str):
    headers = {
        "User-Agent": UserAgent().random,
        "Content-Type": "application/octet-stream",
        "Content-Disposition": "attachment; filename=replay.ttr"
    }
    url = f'https://inoue.szy.lol/api/replay/{replayid}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                content = await response.read()
                file = discord.File(BytesIO(content), filename=f"{replayid}.ttr")
                return file
            else: 
                return response.status

            
