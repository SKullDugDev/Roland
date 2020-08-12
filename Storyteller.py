# main module & ext
from discord.ext import commands

# connect to backend
import StorytellerGuide

# typing hint
from typing import NewType

message = NewType('message', str)

STG = StorytellerGuide

# config info


# set prefix
bot_prefix = "!"

# create Client connection
client = commands.Bot(command_prefix=bot_prefix)


class CampaignCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        pass

    # add campaigns
    @commands.command()
    async def campaignadd(self, ctx, *campaigns_adding) -> message:
        return await ctx.send(STG.campaignadd(ctx, campaigns_adding))

    # list campaigns
    @commands.command()
    async def campaignlist(self, ctx) -> message:
        return await ctx.send(STG.campaignlist(ctx))

    # remove campaigns
    @commands.command()
    async def campaignremove(self, ctx, *campaigns_removing) -> message:
        return await ctx.send(STG.campaignremove(ctx, campaigns_removing))

    # clear campaigns
    @commands.command()
    async def campaignclear(self, ctx) -> message:
        return await ctx.send(STG.campaignclear(ctx))


def setup(bot):
    bot.add_cog(CampaignCommands(bot))
