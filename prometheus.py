import discord
from discord.ext import commands
import requests
from datetime import datetime

prometheus = commands.Bot(command_prefix='do ')


@prometheus.event
async def on_ready():
    print('Prometheus bot active')


@prometheus.command(pass_context=True, name='silence')
async def silence(ctx):
    author = ctx.author

    # Simple function to retrieve the author of a message
    def check(m):
        return author == m.author

    # Check the server name and the user's role to ensure that no one who isn't
    # allowed to use the bot is using it
    if ctx.guild == 'Epoch' and ('mother board' or 'cluster team' or 'post-board' in [y.name.lower for y in author.roles]):

        # Implements a check to ensure that if a user does not respond, the bot will exit the command
        while True:
            await ctx.send('Please specify an end time of the form\n[YYYY]-[MM]-[DD]T[hour]:[minute]:[second]Z')

            # The bot will wait until the user inputs a date and time, for a maximum of 30 seconds

            try:
                end_time = await prometheus.wait_for('message', check=check, timeout=30)
            except TimeoutError: # If no message is entered within 30 seconds, a TimeoutError happens
                await ctx.send('No valid time was entered within 30 seconds.')
                break

            await ctx.send('Any comment?')

            try:
                comment = await prometheus.wait_for('message', check=check)
            except TimeoutError:
                await ctx.send('No valid time was entered within 30 seconds.')
                break

            if comment.content.lower == 'no' or 'nope' or 'n':
                comment = 'No comment'
            # Assigns a message signifying the creation of the silence to a variable for later use
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

    # if a user does not meet the specified criteria, they will be unable to execute the command
    else:
        await ctx.send('You do not have permission to do that')


@prometheus.command()
# checks latency
async def ping(ctx):
    await ctx.send('latency: {} ms'.format(round(prometheus.latency * 1000)))

key = ''

prometheus.run(key)
