import discord
from discord.ext import commands
import requests
from datetime import datetime
from datetime import timedelta
import sys
import sqlite3

prometheus = commands.Bot(command_prefix='do ')


@prometheus.event
async def on_ready():
    print('Prometheus bot active')



@prometheus.command(pass_context=True, name='silence')
@commands.has_role("Cluster Team")
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
            await ctx.send('No comment was entered within 45 seconds. Cancelling...')
            break
        conn = sqlite3.connect('userassoc.db')
        cursor = conn.execute('''
            SELECT * FROM USERDATA
            WHERE discorduser="{}"
        '''.format(author))
        records = cursor.fetchone()
        conn.close()
        name, email = records[1] if records != [] else "", records[2] if records != [] else ""
        if records == []:
            await ctx.send('We don\'t seem to have your real name on file. What is your real name?')
            try:
                name = await prometheus.wait_for('message', check=check, timeout=45).content
            except TimeoutError:
                # defaults to no comment without a comment being entered
                await ctx.send('No name was entered within 45 seconds. Cancelling...')
                break
            await ctx.send('What is your IMSA email?')
            try:
                email = await prometheus.wait_for('message', check=check, timeout=45).content
            except TimeoutError:
                # defaults to no comment without a comment being entered
                await ctx.send('No name was entered within 45 seconds. Cancelling...')
                break
            query = "REPLACE INTO USERDATA (discorduser,name,email) VALUES ('{}', '{}', '{}')".format(author, name, email)
            conn.execute(query)
            conn.commit()
            conn.close()
        else:
            pass
        # Assigns a message signifying the creation of the silence to a
        # variable for later use
        creating = await ctx.send('Creating silence for {} <{}>...'.format(name, email))

        now = str(datetime.now()).replace(' ', 'T') + 'Z'
        url = 'http://alerts.epoch.imsa.edu/api/v1/silences'
        post_data = {"id": "",
                        "createdBy": "{} {}".format(name, email),
                        "comment": comment,
                        "startsAt": now,
                        "endsAt": end_time,
                        "matchers": [{"name": "job",
                                    "value": "evc_slurm_exporter",
                                    "isRegex": False}]}
        try:
            x = requests.post(url, data=post_data)
        except: 
            await ctx.send("Error silencing the alert. Please try again.")
            break

        # edits the previous message to show that the request has gone through
        await creating.edit(content='Creating silence for {} <{}> ... done!'.format(name, email))
        # sends the response to the Discord channel
        await ctx.send(x)
        # ends the command
        break


@prometheus.command()
# checks latency
async def ping(ctx):
    await ctx.send('latency: {} ms'.format(round(prometheus.latency * 1000)))

key = sys.argv[1]

prometheus.run(key)