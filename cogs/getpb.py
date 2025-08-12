import discord, typing, aiohttp
from discord.ext import commands
from discord import app_commands
from fake_useragent import UserAgent
from math import ceil
#自製模組
from utils.fetchimage import merge_icons 
from utils.fetchdata import fetchdata

class Getpb(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(name="get-pb", description="ew")
    @app_commands.guilds(discord.Object(id=1325105067787026473))
    async def getpb(self, 
        interaction: discord.Interaction, 
        username: str, 
        gamemode: typing.Literal["40l", "blitz", "zenith", "zenithex"]
    ):
        record_url = f"https://ch.tetr.io/api/users/{username}/records/{gamemode}/top?limit=1"
        user_url = f"https://ch.tetr.io/api/users/{username}"
        record_data = await fetchdata(record_url)
        user_data = await fetchdata(user_url)
        await interaction.response.defer(thinking=True)

        if not record_data.get("success", True):
            error_msg = record_data.get("error").get("msg")
            await interaction.followup.send(f"我猜你把 {username} 打錯了")
            print(f"API 回應錯誤: {error_msg}")
            return
        entries = record_data.get("data").get("entries")
        if len(entries) == 0:
            await interaction.followup.send(f'欸你知道嗎，{username} 居然沒有玩過 {gamemode} 耶')
            return
        #print("讀取資料中")
        try:
            user_id = user_data.get("data").get("_id")
            avatar_revision = user_data.get("data").get("avatar_revision")
            stats = entries[0].get("results").get("stats")
            replayid = entries[0].get("replayid")
            #40l
            pps = round(entries[0].get("results").get("aggregatestats").get("pps"), 2)
            finaltime = stats.get("finaltime") / 1000
            kpp = round((stats.get("inputs")) / (stats.get("piecesplaced")), 2)
            #blitz
            score = stats.get("score")
            level = stats.get("level")
            #zenith
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
            embed = discord.Embed(
                title=f"{username}'s {gamemode} PB", 
                url=f"https://tetr.io/#R:{replayid}", 
                description="click title to watch replay in tetrio"
            )
            embed.set_thumbnail(
                url=f"https://tetr.io/user-content/avatars/{user_id}.jpg?rv={avatar_revision}"
            )
            #print(f"讀取 {username} 的 {gamemode} PB 成功")
        except Exception as e:
            await interaction.followup.send("發生錯誤")
            print(f"讀取發生錯誤: {e}")
        try:
            if gamemode == "40l":
                embed.add_field(name=" pps ", value=pps, inline=True)
                embed.add_field(name=" finaltime ", value=f"{finaltime:.3f}s", inline=True)
                embed.add_field(name=" kpp ", value=kpp, inline=True)
                embed.set_image(url="https://img.littlezhaidi.me/40l.png")
                await interaction.followup.send(embed=embed)
                return     
            elif gamemode == "blitz":
                embed.add_field(name=" score ", value=score, inline=True)
                embed.add_field(name=" level ", value=level, inline=True)
                embed.add_field(name=" pps ", value=pps, inline=True)
                embed.set_image(url="https://img.littlezhaidi.me/blitz.png")
                await interaction.followup.send(embed=embed)
                return     
            else:
                mods = entries[0].get("extras").get("zenith").get("mods")
                if stats.get("speedrun"):
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
                    file = discord.File("/Volumes/TRANSCEND/sdhc/somecoolstuff/chtetr-bot/combined.png", filename="combined.png")
                    embed.set_image(url="attachment://combined.png")
                    await interaction.followup.send(embed=embed, file=file)
                    return
                else:
                    embed.set_image(url="https://img.littlezhaidi.me/quickplay.png")
                    await interaction.followup.send(embed=embed)
                    return     
        except Exception as e:
            print(f"處理嵌入內容時發生錯誤: {e}")
            await interaction.followup.send("發生錯誤:)")
            return   
        await interaction.followup.send("發生錯誤")

    
async def setup(bot):
    try:
        await bot.add_cog(Getpb(bot))
    except Exception as e:
        print(f"載入 Getpb 時發生錯誤: {e}")

