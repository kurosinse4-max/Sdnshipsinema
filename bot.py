import os
import aiohttp
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

class CinemaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Trending Movies", style=discord.ButtonStyle.danger, emoji="🔥")
    async def trending_movies(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send("❌ عذراً، حدث خطأ في جلب الأفلام الرائجة.", ephemeral=True)
                    return
                data = await resp.json()
                results = data.get("results", [])[:5]
                
                desc = ""
                for m in results:
                    desc += f"🎬 **{m.get('title')}** (⭐ {m.get('vote_average')})\n"
                
                embed = discord.Embed(title="🔥 أبرز الأفلام الرائجة اليوم", description=desc, color=discord.Color.red())
                await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Trending TV", style=discord.ButtonStyle.primary, emoji="📺")
    async def trending_tv(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        url = f"https://api.themoviedb.org/3/trending/tv/day?api_key={TMDB_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send("❌ عذراً، حدث خطأ في جلب المسلسلات الرائجة.", ephemeral=True)
                    return
                data = await resp.json()
                results = data.get("results", [])[:5]
                
                desc = ""
                for m in results:
                    desc += f"📺 **{m.get('name')}** (⭐ {m.get('vote_average')})\n"
                
                embed = discord.Embed(title="📺 أبرز المسلسلات الرائجة اليوم", description=desc, color=discord.Color.blue())
                await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Anime", style=discord.ButtonStyle.success, emoji="🍥")
    async def anime_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        url = f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&with_genres=16"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send("❌ عذراً، حدث خطأ في جلب قائمة الأنمي.", ephemeral=True)
                    return
                data = await resp.json()
                results = data.get("results", [])[:5]
                
                desc = ""
                for m in results:
                    desc += f"🍥 **{m.get('name')}** (⭐ {m.get('vote_average')})\n"
                
                embed = discord.Embed(title="🍥 أحدث مسلسلات الأنمي", description=desc, color=discord.Color.green())
                await interaction.followup.send(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command(name="movie", help="إرسال لوحة التحكم الخاصة بالسينما")
async def movie_panel(ctx):
    embed = discord.Embed(
        title="SUDANSHIP-CINEMA 🎬",
        description="مرحباً بك في | SUDANSHIP-CINEMA ، لوحة التحكم الموحدة لاكتشاف ومشاهدة الأفلام، المسلسلات، والأنمي 🎞️",
        color=discord.Color.gold()
    )
    embed.set_image(url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800")
    embed.set_footer(text="Powered by TMDB & SUDANSHIP")
    
    await ctx.send(embed=embed, view=CinemaView())

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
