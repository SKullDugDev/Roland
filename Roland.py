# for paths
import pathlib

# for configuration file
import toml

# main module & ext
from discord.ext import commands

# connect to backend
import RolandCampaignCommands

rc_commands = RolandCampaignCommands

# typing hint
from typing import NewType

message = NewType('message', str)

# config info

CONFIGURATION_FILE = pathlib.Path.cwd() / "data" / "configuration" / "token.toml"
TOKEN = toml.loads(CONFIGURATION_FILE.read_text())
TOKEN = TOKEN['TOKEN']

# set prefix
bot_prefix = "!"

# create Client connection
client = commands.Bot(command_prefix=bot_prefix)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# add campaigns
@client.command()
async def campaignadd(ctx, *new_campaigns_from_user) -> message:
    campaign_added_message = rc_commands.campaignadd(ctx, new_campaigns_from_user)
    return await ctx.send(campaign_added_message)


# list campaigns
@client.command()
async def campaignlist(ctx) -> message:
    campaign_list_string = rc_commands.campaignlist(ctx)
    return await ctx.send(campaign_list_string)


# remove campaigns
@client.command()
async def campaignremove(ctx, *campaigns_set_for_removal) -> message:
    campaign_deletion_message = rc_commands.campaignremove(ctx, *campaigns_set_for_removal)
    return await ctx.send(campaign_deletion_message)


# clear campaigns
@client.command()
async def campaignclear(ctx) -> message:
    campaign_clear_message = rc_commands.campaignclear(ctx)
    return await ctx.send(campaign_clear_message)


client.run(TOKEN)
