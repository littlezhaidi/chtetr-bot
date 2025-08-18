import discord
from discord.ext import commands
from discord import app_commands
from utils.fetchdata import save_replay

class SaveReplay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(name="saverp", description="回傳指定的.ttr檔案")
    @app_commands.guilds(discord.Object(id=1325105067787026473))
    async def save_replay(self, 
        interaction: discord.Interaction, 
        replayid: str
    ):
        file = await save_replay(replayid)
        if type(file) == int:
            status = file
            # 如果 file 是 int，表示發生了錯誤，status 會是 HTTP 狀態碼
            if status == 404:
                await interaction.response.send_message("我猜你複製了錯誤的replayid，或者這個replay早就被刪了")
                return
            else:
                await interaction.response.send_message("發生錯誤，請稍後再試。")
                error_message = (
                    f"API 發生異常狀況。\n"
                    f"Replay ID: {replayid}\n"
                    f"HTTP 狀態碼: {status}\n"
                )
                chillythecat = await self.bot.fetch_user(803794851920478208)
                await chillythecat.send(error_message)
                return
        else:
            await interaction.response.send_message(content="replay saved", file=file)
        

async def setup(bot):
    await bot.add_cog(SaveReplay(bot))
