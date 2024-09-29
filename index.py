import discord
from discord.ext import commands
from discord import ui
import json
import os
import logging

logging.basicConfig(level=logging.ERROR)

GREEN = '\033[92m'
WHITE = '\033[97m'
RESET = '\033[0m'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='+', intents=intents)

dmall_active = False
sent_members = []
message_to_send = None
save_file = 'save.json'

def load_message():
    global message_to_send
    if os.path.exists(save_file):
        with open(save_file, 'r') as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)
                message_to_send = data.get('message', None)
            else:
                message_to_send = None
    else:
        with open(save_file, 'w') as f:
            json.dump({'message': ''}, f)
        message_to_send = None

def save_message(message):
    with open(save_file, 'w') as f:
        json.dump({'message': message}, f)

load_message()

class Tsaispasdevtgckaysauxcommandefdp(ui.View):
    def __init__(self, ctx, embed_message):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embed_message = embed_message
    
    @ui.button(label="Modifier", style=discord.ButtonStyle.primary)
    async def modify_message(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user == self.ctx.author:
            await interaction.response.send_message("Veuillez entrer le nouveau message :")

            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel

            try:
                message = await bot.wait_for('message', check=check, timeout=60.0)
                global message_to_send
                message_to_send = message.content
                
                save_message(message_to_send)
                
                embed = self.embed_message.embeds[0]
                embed.set_field_at(0, name="Message:", value=message_to_send, inline=False)
                
                await self.embed_message.edit(embed=embed)
                await self.ctx.send(f"Nouveau message enregistré : `{message_to_send}`")
            except:
                await self.ctx.send("Le temps d'attente pour modifier le message a expiré.")
    
    @ui.button(label="Envoyer", style=discord.ButtonStyle.success)
    async def send_message(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user == self.ctx.author:
            global dmall_active
            global message_to_send

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

            confirmation_message = await interaction.followup.send("0 membres ont reçu le message.", ephemeral=True)

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
                    print(f"Impossible d'envoyer un message à {member.name} ({member.id}), ils ont bloqué les messages privés.")
                except Exception as e:
                    print(f"Erreur lors de l'envoi à {member.name}: {e}")

@bot.command()
async def dmall(ctx):
    global message_to_send
    
    embed = discord.Embed(title="DM à tous les membres", description="Voici le message qui va être envoyé :")
    
    if message_to_send:
        embed.add_field(name="Message:", value=message_to_send, inline=False)
    else:
        embed.add_field(name="Message:", value="*Aucun message enregistré*", inline=False)
    
    view = Tsaispasdevtgckaysauxcommandefdp(ctx, embed_message=None)
    embed_message = await ctx.send(embed=embed, view=view)
    
    view.embed_message = embed_message

@bot.event
async def on_message(message):
    if bot.user in message.mentions:
        await message.channel.send("Fait **+dmall** sale zig")
    
    await bot.process_commands(message)

token = input(f"{WHITE}[{RESET}{GREEN}+{RESET}{WHITE}] Enter token: ")

bot.run(token)