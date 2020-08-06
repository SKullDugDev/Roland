# for paths
import pathlib

# for configuration file
import toml

# main module & ext
import discord
from discord.ext import commands

# connect to backend
import RolandSQL

# log errors
import logging
from pyodbc import DatabaseError
import cordlog

CONFIGURATION_FILE = pathlib.Path.cwd() / "data" / "configuration" / "token.toml"
TOKEN = toml.loads(CONFIGURATION_FILE.read_text())
TOKEN = TOKEN['TOKEN']

# create Client connection
client = discord.Client()

# set prefix
bot_prefix = "!"

client = commands.Bot(command_prefix=bot_prefix)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def campaignadd(ctx, user_campaign_name: str):
    # connect to database
    db = RolandSQL.SqlRunner()

    # run new campaign name adding process and store in check_failed
    check_failed = db.process_to_add_new_campaign_name(user_campaign_name)
    if check_failed:
        await ctx.send('Campaign already exists!')
    else:
        try:
            db.check_campaign_name_before_committing(user_campaign_name)
            await ctx.send('Campaign added!')
        except DatabaseError:
            cordlog.logger.exception("Commit Error Occurred...")
        finally:
            db.close()


client.run(TOKEN)
