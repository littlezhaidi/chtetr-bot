import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="輸入/help <command> 來獲取詳細資訊")
    @app_commands.guilds(discord.Object(id=1325105067787026473))
    async def help(self, interaction: discord.Interaction, cmd: str = None):
        if cmd is None:
            await interaction.response.send_message("""# chillythacat's bot
### 查詢並且記錄tetr.io活動的機器人
```ansi
[0;0m指令介紹
[1;38m輸入 /help 指令名稱 來獲得詳細資訊
[0;30m------------------------------------
[0;0m/help 指令資訊
/get-pb 獲取指定使用者的PB
/sendrp 回傳指定的.ttr檔案
/tasks 定時搜尋某人最近完成的遊戲
/cancel_tasks 停止執行中的搜尋
```""")
        elif cmd.lower() == "get-pb":
            await interaction.response.send_message("""# chillythacat's bot
### 查詢並且記錄tetr.io活動的機器人
```ansi
[0;0m指令介紹
[1;38m/get-pb 手動獲取指定使用者的PB
[0;30m-------------------------------------
[0;0m引數:
[0;34musername [0;0m用戶名稱（也接受長id）
[0;34mgamemode [0;0m遊戲模式，目前不支援tetra league

[0;0m註：想尋找expert模式遊戲，請輸入zenithex
點擊標題連結，可進入遊戲內觀看replay
[0;30m-------------------------------------
[1;38m使用例:（可以直接複製來玩玩看）
[0;0m/get-pb username: osk gamemode: 40l
```""")
        elif cmd.lower() == "sendrp":
            await interaction.response.send_message("""# chillythacat's bot
### 查詢並且記錄tetr.io活動的機器人
```ansi
[0;0m指令介紹
[1;38m/sendrp 回傳指定的.ttr檔案
[0;30m-------------------------------------
[0;0m引數:
[0;34mreplayid [0;0m支持短ID和長ID兩種格式
[0;0m                                          
[0;0m註：replayID可以在tetra channel，或是遊戲結算畫面找到
[0;30m-------------------------------------
[1;38m使用例:（可以直接複製來玩玩看）
[0;0m/sendrp replayid: 0266e1db49f5
```""")
        elif cmd.lower() == "tasks":
            await interaction.response.send_message("""# chillythacat's bot
### 查詢並且記錄tetr.io活動的機器人
```ansi
[0;0m指令介紹
[1;38m/tasks 定時搜尋某人最近完成的遊戲
[0;30m-------------------------------------
[0;0m引數:
[0;34musername [0;0m用戶名稱（也接受長ID）
[0;34mgamemode [0;0m遊戲模式，目前不支援tetra league
[0;34mchannel [0;0m目標頻道名稱，只要找到新紀錄就會發送到那裡
[0;34mhours [0;0m機器人應該幾小時搜尋一次（如果找到多筆紀錄，會一次性發送出來）
[0;34mispb [0;0m機器人是否只尋找新的PB，true或是false

[0;0m註：如果要停止搜尋，輸入/cancal_tasks
[0;0m註2：如果機器人被開發者關機了，所有的tasks將會丟失! 
未來會再開發關機後保留任務的功能
[0;30m-------------------------------------
[1;38m使用例:（可以直接複製來玩玩看）
[0;0m/tasks [0;34musername:[0;0m 5han [0;34mgamemode:[0;0m zenith [0;34mchannel: [0;0mtetriodalao [0;34mhours: [0;0m6 [0;34mispb: [0;0mtrue
```""")
        else: await interaction.response.send_message(f'command "{cmd}" is not available now.')
async def setup(bot):
    await bot.add_cog(Help(bot))
