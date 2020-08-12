# discord
import discord
from discord.ext import commands

# for paths
import pathlib

# for configuration file
import toml

# import the commander
import RolandCommander

# config info

CONFIGURATION_FILE = pathlib.Path.cwd() / "data" / "configuration" / "token.toml"
TOKEN = toml.loads(CONFIGURATION_FILE.read_text())
TOKEN = TOKEN['TOKEN']

# set bot prefix
bot_prefix = "!"

# create bot connection
client = commands.Bot(command_prefix=bot_prefix)

# call in the commander
RolandCommander.initiate_command_sequence(client)


# say hi
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


client.run(TOKEN)
