from cachetools import TTLCache
from fake_useragent import UserAgent
import discord, aiohttp
from math import ceil
from io import BytesIO
from PIL import Image
from sklearn.cluster import KMeans
import numpy as np
from utils.fetchimage import merge_icons #自製模組

cache = TTLCache(maxsize=100, ttl=60)
headers = {
    "User-Agent": UserAgent().random,
    "Content-Type": "application/octet-stream",
    "Content-Disposition": "attachment; filename=replay.ttr"
}

async def fetchdata(url: str, ignorecache: bool):  
    headers = {"User-Agent": UserAgent().random}
    if url in cache and not ignorecache:
        print(f"從快取中讀取資料: {url}")
        return cache[url]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=5) as response:
                data = await response.json()
                cache[url] = data
                return data
    except Exception as e:
        print(f"fetchdata炸了: {e}")
        raise

async def _get_embed_color(user_id, avatar_revision):
    embed_color = discord.Color.from_rgb(55, 54, 59) #這好像才是預設，你如果用.default()會變成黑色
    if avatar_revision:
        avatar_url = f"https://tetr.io/user-content/avatars/{user_id}.jpg?rv={avatar_revision}"
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url, headers=headers) as response:
                image_data = await response.read()

        img = Image.open(BytesIO(image_data)).convert("RGB")
        img = img.resize((100, 100))  # 加速
        pixels = np.array(img).reshape(-1, 3)

        kmeans = KMeans(n_clusters=5, random_state=0, n_init="auto").fit(pixels)
        labels, counts = np.unique(kmeans.labels_, return_counts=True)
        #佔比
        total_pixels = len(pixels)
        proportions = counts / total_pixels
        clusters = [
            {"color": tuple(map(int, kmeans.cluster_centers_[label])), "proportion": prop}
            for label, prop in zip(labels, proportions)
        ]
        clusters.sort(key=lambda x: x["proportion"], reverse=True)

        main_color = None
        if clusters[0]["proportion"] > 0.5 and len(clusters) > 1:
            main_color = clusters[1]["color"]
        else:
            main_color = clusters[0]["color"]
        
        embed_color = discord.Color.from_rgb(*main_color)
    return embed_color

def _add_40l_fields(embed, stats, entries):
    pps = round(entries[0].get("results").get("aggregatestats").get("pps"), 2)
    finaltime = stats.get("finaltime") / 1000
    piecesplaced = stats.get("piecesplaced")
    kpp = round((stats.get("inputs")) / piecesplaced, 2)
    holds = stats.get("holds")
    finesse = stats.get("finesse").get("faults")
    embed.add_field(name=" pps ", value=pps, inline=True)
    embed.add_field(name=" finaltime ", value=f"{finaltime:.3f}s", inline=True)
    embed.add_field(name=" kpp ", value=kpp, inline=True)
    embed.add_field(name=" holds ", value=holds, inline=True)
    embed.add_field(name=" pieces ", value=piecesplaced, inline=True)
    embed.add_field(name=" finesse faults ", value=finesse, inline=True)

def _add_blitz_fields(embed, stats, entries):
    pps = round(entries[0].get("results").get("aggregatestats").get("pps"), 2)
    score = stats.get("score")
    level = stats.get("level")
    piecesplaced = stats.get("piecesplaced")
    spp = round(score / piecesplaced, 2)
    perfectclear = stats.get("clears").get("allclear")
    embed.add_field(name=" score ", value=score, inline=True)
    embed.add_field(name=" level ", value=level, inline=True)
    embed.add_field(name=" pps ", value=pps, inline=True)
    embed.add_field(name=" pieces ", value=piecesplaced, inline=True)
    embed.add_field(name=" score per piece ", value=spp, inline=True)
    embed.add_field(name=" perfect clears ", value=perfectclear, inline=True)
    #embed.set_image(url="https://img.littlezhaidi.me/blitz.png")

def _add_zenith_fields(embed, stats, entries):
    pps = round(entries[0].get("results").get("aggregatestats").get("pps"), 2)
    finaltime = stats.get("finaltime") / 1000

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
    mods = entries[0].get("extras").get("zenith").get("mods")
    if stats.get("speedrun") and not mods: #無mod才能進入hyperspeed(expert是其中一種mod)，hyperspeed撐到f10才會有speedrun
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
    #if mods:
    #    merge_icons(mods)
    #    embed.add_field(name="", value="** mods **")
    #    embed.set_image(url="attachment://combined.png")
    #else:
    #    embed.set_image(url="https://img.littlezhaidi.me/quickplay.png")

async def _add_image(gamemode, mods: dict = None):
    if gamemode == "40l":
        return "https://img.littlezhaidi.me/40l.png"
    elif gamemode == "blitz":
        return "https://img.littlezhaidi.me/blitz.png"
    else:
        if mods:
            return await merge_icons(mods)
        else:
            return "https://img.littlezhaidi.me/quickplay.png"

async def create_embed(record_data: dict, user_data: dict, gamemode: str, username: str):

    try: #avatar
        entries = record_data.get("data").get("entries")
        replayid = entries[0].get("replayid")
        user_id = user_data.get("data").get("_id")
        avatar_revision = user_data.get("data").get("avatar_revision")

        if avatar_revision:
            avatar_url = f"https://tetr.io/user-content/avatars/{user_id}.jpg?rv={avatar_revision}"
        else:
            avatar_url = "https://tetr.io/res/avatar.png" #改用anonymous的頭像
        embed_color = await _get_embed_color(user_id, avatar_revision)
    except Exception as e:
        print(e)
    try:
        embed = discord.Embed(
            title=f"{username}'s {gamemode} record", 
            url=f"https://tetr.io/#R:{replayid}", 
            description="click title to watch replay in tetrio",
            color=embed_color
        )
        embed.set_thumbnail(url=avatar_url)
        
        stats = entries[0].get("results").get("stats")
        file = None
        if stats.get("seed"):
            print("舊版結構")
        if gamemode == "40l":
            _add_40l_fields(embed, stats, entries)
            embed.set_image(url="https://img.littlezhaidi.me/40l.png") #直接用url比較快
        elif gamemode == "blitz":
            _add_blitz_fields(embed, stats, entries)
            embed.set_image(url="https://img.littlezhaidi.me/blitz.png")
        else:
            mods = entries[0].get("extras").get("zenith").get("mods")
            _add_zenith_fields(embed, stats, entries)
            file = await _add_image(gamemode, mods)
        return embed, file
    
    except Exception as e:
        print("fetchdata", e)

async def save_replay(replayid: str):
    url = f'https://inoue.szy.lol/api/replay/{replayid}'
    #url = "https://httpbin.io/status/503"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                content = await response.read()
                file = discord.File(BytesIO(content), filename=f"{replayid}.ttr")
                return file
            else: 
                raise Exception(response.status)