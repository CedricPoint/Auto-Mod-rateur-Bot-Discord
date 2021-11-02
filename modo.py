#!/usr/bin/python3

import discord

class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        word_list = ['cheat', 'cheats', 'hack', 'hacks', 'internal', 'external', 'ddos', 'denial of service']

        # don't respond to ourselves
        if message.author == self.user:
            return

        messageContent = message.content
        if len(messageContent) > 0:
            for word in word_list:
                if word in messageContent:
                    await message.delete()
                    await message.channel.send('Ne dis pas sa ici!')
            
        messageattachments = message.attachments
        if len(messageattachments) > 0:
            for attachment in messageattachments:
                if attachment.filename.endswith(".dll"):
                    await message.delete()
                    await message.channel.send("Les upload de .dll ne sont pas autorisé ici!")
                elif attachment.filename.endswith('.exe'):
                    await message.delete()
                    await message.channel.send("Les upload de .exe ne sont pas autorisé ici!")
                else:
                    break

client = MyClient()
client.run('ODk0OTgzNjY0MDEyNzY3MjYz.YVx8fQ.qnRjagKz7TbkzIW8mKnmzYklexI')
