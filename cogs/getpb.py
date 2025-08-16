import discord, typing
from discord.ext import commands
from discord import app_commands
#自製模組
from utils.fetchdata import fetchdata, create_embed

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
        await interaction.response.defer(thinking=True)
        record_data = await fetchdata(record_url, ignorecache=False)
        user_data = await fetchdata(user_url, ignorecache=False)

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
        entries = record_data.get("data").get("entries")
        embed, file = await create_embed(record_data, user_data, gamemode, username)

        if gamemode == "zenith":                                   #40l和blitz的extras是空的
            if entries[0].get("extras").get("zenith").get("mods"): #所以要套兩層否則會出錯，暫時沒想到更好的解法 
                await interaction.followup.send(embed=embed, file=file)
                return
        else:
            await interaction.followup.send(embed=embed)  
    
async def setup(bot):
    try:
        await bot.add_cog(Getpb(bot))
    except Exception as e:
        print(f"載入 Getpb 時發生錯誤: {e}")

