import discord
import discord.ext
from discord.ext import commands
from discord import ui
import json
import os
import logging

import discord.ext.commands


logging.basicConfig(level=logging.ERROR)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='+', intents=intents)

dmall_active = False
sent_members = []

class Config:
    file = 'save.json'

    def load_message() -> str:
        if os.path.exists(Config.file):
            with open(Config.file, 'r') as f:
                content = f.read().strip()
                if content:
                    data:dict = json.loads(content)
                    return data.get('message', None)
                else:
                    return None
        else:
            with open(Config.file, 'w') as f:
                json.dump({'message': ''}, f)
            return None

    def save_message(message):
        with open(Config.file, 'w') as f:
            json.dump({'message': message}, f)

message_to_send = Config.load_message()

class Buttons(ui.View):
    def __init__(self, ctx: discord.ext.commands.Context, message: discord.Message):
        super().__init__(timeout=None)
        self.ctx: discord.ext.commands.Context = ctx
        self.message: discord.Message = message
    
    def check(self, message: discord.Message):
        return message.author == self.ctx.author and message.channel == self.ctx.channel

    @ui.button(label="Modifier", style=discord.ButtonStyle.primary)
    async def modify_message(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user == self.ctx.author:
            await interaction.response.send_message("Veuillez entrer le nouveau message :")

            try:
                message = await bot.wait_for('message', check=self.check, timeout=60.0)
                message_to_send = message.content
                
                Config.save_message(message_to_send)
                
                embed = self.message.embeds[0]
                embed.set_field_at(0, name="Message:", value=message_to_send, inline=False)
                
                await self.message.edit(embed=embed)
                await self.ctx.send(f"Nouveau message enregistré : `{message_to_send}`")
            except:
                await self.ctx.send("Le temps d'attente pour modifier le message a expiré.")
    
    @ui.button(label="Envoyer", style=discord.ButtonStyle.success)
    async def send_message(self, interaction: discord.Interaction, button: ui.Button):
        message_to_send = Config.load_message()
        
        if interaction.user == self.ctx.author:
            if not message_to_send:
                await interaction.response.send_message("Aucun message n'a été enregistré. Veuillez utiliser le bouton Modifier pour entrer un message.", ephemeral=True)
                return

            dmall_active = True
            sent_members.clear()
            guild = self.ctx.guild

            if not guild:
                await self.ctx.send("Cette commande doit être utilisée dans un serveur.")
                return

            await interaction.response.defer(ephemeral=True)

            confirmation_message: discord.Message = await interaction.followup.send("0 membres ont reçu le message.", ephemeral=True)

            members_contacted = 0

            for member in guild.members:
                if member.bot:
                    continue

                try:
                    if dmall_active:
                        await member.send(message_to_send)
                        members_contacted += 1
                        sent_members.append(member.name)

                        await confirmation_message.edit(content=f"{members_contacted} membres ont reçu le message.")
                    else:
                        print("L'envoi de DM a été interrompu.")
                        break
                except discord.Forbidden:
                    print(f"Impossible d'envoyer un message à {member.name} ({member.id}).")
                except Exception as e:
                    print(f"Erreur lors de l'envoi à {member.name}: {e}")

@bot.command()
async def dmall(ctx: discord.ext.commands.Context):
    embed = discord.Embed(title="DM à tous les membres", description="Voici le message qui va être envoyé :")
    _message = message_to_send if message_to_send else "*Aucun message enregistré*"
    embed.add_field(name="Message:", value=_message, inline=False)
    
    view = Buttons(ctx, message=None)
    message = await ctx.send(embed=embed, view=view)
    
    view.message = message

@bot.event
async def on_message(message: discord.Message):
    if bot.user in message.mentions:
        await message.channel.send("Fait **+dmall** pour envoyer un message à tous les membres du serveur.")
    
    await bot.process_commands(message)

token = input(f"[+] Enter token: ")
bot.run(token)
