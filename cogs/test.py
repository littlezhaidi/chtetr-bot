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
        #await interaction.response.defer(thinking=True)
        #channels = interaction.guild.text_channels
        #for channel in channels:
        #    print(f"Channel: {channel.name} (ID: {channel.id})")
        #await interaction.followup.send("已列出所有頻道") 
        embed = discord.Embed(title="icon test", description="this is a test embed", color=0x00ff00)
        embed.set_thumbnail(url="https://tetr.io/user-content/avatars/628dee03e01813ce27475745.jpg")
        embed.add_field(name="name1", value="value1", inline=True)
        embed.add_field(name="name2", value="value2",inline=True)
        embed.add_field(name="name3", value="value3", inline=True)
        embed.add_field(name="name4", value="value4", inline=True)
        embed.add_field(name="name5", value="value5", inline=True)
        embed.add_field(name="name6", value="value6", inline=True)
        embed.add_field(name="maximum b2b chain", value="69", inline=True)
        embed.add_field(name="lines received", value="499", inline=True)
        embed.add_field(name="KOs", value="6", inline=True)
        embed.add_field(name="mods", value="")
        embed.set_image(url="https://img.littlezhaidi.me/expert.png")
        await interaction.response.send_message(embed=embed)

        
async def setup(bot):
    await bot.add_cog(Test(bot))