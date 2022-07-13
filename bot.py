import nextcord
from nextcord.ext import commands, tasks
from constants import *
from register import RegisterUser
from update import UpdateUser
from stats import UserStats

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

bot.add_cog(UserStats(bot))
bot.add_cog(UpdateUser(bot))
bot.add_cog(RegisterUser(bot))
bot.run(BOTTOKEN)