import discord
from discord.ext import commands
from discord import app_commands

#測試用，可以亂改
#因為啟動之後再寫新的cog，似乎沒辦法用^load指令載入

class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="test", description="test command")
    @app_commands.guilds(discord.Object(id=1325105067787026473))
    async def test(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        channels = interaction.guild.text_channels
        for channel in channels:
            print(f"Channel: {channel.name} (ID: {channel.id})")
        await interaction.followup.send("已列出所有頻道") 
        
async def setup(bot):
    await bot.add_cog(Test(bot))