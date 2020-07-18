import discord
from discord.ext import commands
import requests
from datetime import datetime
from datetime import timedelta
import os

prometheus = commands.Bot(command_prefix='do ')


@prometheus.event
async def on_ready():
    print('Prometheus bot active')



@prometheus.command(pass_context=True, name='silence')
async def silence(ctx, time=720):
    author = ctx.author

    # Simple function to ensure the author of a message is the same as the one
    # who inputted the command
    def check(m):
        return author == m.author

    # Converts the minutes argument into a datetime object
    def datetime_from_minutes(minutes):
        end_time = datetime.now() + timedelta(minutes=minutes)
        return end_time

    # Check the server name and the user's role to ensure that no one who isn't
    # allowed to use the bot is using it
    if ctx.guild == 'Epoch' and ('mother board' or 'cluster team' or 'post-board' in [y.name.lower for y in author.roles]):

        while True:
            try:
                time = int(time)
            except TypeError:
                ctx.send('Please enter a valid time')
                # line to enter a new time value if the time entered is not an integer
                try:
                    time = await prometheus.wait_for('message', check=check, timeout=15)
                except TimeoutError:
                    continue
            break

        # Implements a check to ensure that if a user does not respond, the bot
        # will exit the command
        while True:
            end_time = str(datetime_from_minutes(time)).replace(' ', 'T') + 'Z'
            await ctx.send('Any comment?')

            try:
                comment = await prometheus.wait_for('message', check=check, timeout=45)
                if comment.content.lower == 'no' or 'nope' or 'n':
                    comment = 'No comment'

            except TimeoutError:
                # defaults to no comment without a comment being entered
                await ctx.send('No comment was entered within 45 seconds. Setting to default.')
                comment = 'No comment'

            # Assigns a message signifying the creation of the silence to a
            # variable for later use
            creating = await ctx.send('Creating silence for {}...'.format(author.name))

            now = str(datetime.now()).replace(' ', 'T') + 'Z'
            url = 'http://alerts.epoch.imsa.edu/api/v1/silences'
            post_data = {"id": "",
                         "createdBy": author.name,
                         "comment": comment,
                         "startsAt": now,
                         "endsAt": end_time,
                         "matchers": [{"name": "job",
                                       "value": "evc_slurm_exporter",
                                       "isRegex": False}]}
            x = requests.post(url, data=post_data)

            # edits the previous message to show that the request has gone through
            await creating.edit(content='Creating silence for{}...done'.format(author.name))
            # sends the response to the Discord channel
            await ctx.send(x)
            # ends the command
            break

    # if a user does not meet the specified criteria, they will be unable to
    # execute the command
    else:
        await ctx.send('You do not have permission to do that')


@prometheus.command()
# checks latency
async def ping(ctx):
    await ctx.send('latency: {} ms'.format(round(prometheus.latency * 1000)))

key = os.environ['DISCORD_KEY']

prometheus.run(key)
