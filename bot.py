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
        # جلب الأفلام الرائجة
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
        # البحث عن الأنمي عبر TMDB
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

@bot.command(name="panel", help="إرسال لوحة التحكم الخاصة بالسينما")
async def panel(ctx):
    embed = discord.Embed(
        title="SUDANSHIP-CINEMA 🎬",
        description="مرحباً بك في | SUDANSHIP-CINEMA ، لوحة التحكم الموحدة لاكتشاف ومشاهدة الأفلام، المسلسلات، والأنمي 🎞️",
        color=discord.Color.gold()
    )
    embed.set_image(url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800")
    embed.set_footer(text="Powered by TMDB & SUDANSHIP")
    
    await ctx.send(embed=embed, view=CinemaView())

@bot.command(name="kuro", help="البحث عن الأفلام")
async def search_movie(ctx, *, query: str):
    if not TMDB_API_KEY:
        await ctx.send("⚠️ مفتاح TMDB غير معرّف!")
        return

    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await ctx.send("❌ حدث خطأ في الاتصال.")
                return
            data = await response.json()
            results = data.get("results", [])
            if not results:
                await ctx.send(f"❌ لم يتم العثور على نتائج لـ: **{query}**")
                return
            
            movie = results[0]
            title = movie.get("title")
            overview = movie.get("overview", "لا توجد نبذة.")
            movie_id = movie.get("id")
            watch_link = f"https://vidsrc.to/embed/movie/{movie_id}"

            embed = discord.Embed(title=title, description=overview[:300], color=discord.Color.dark_embed())
            embed.add_field(name="🔗 رابط المشاهدة المباشرة", value=f"[اضغط هنا للمشاهدة]({watch_link})", inline=False)
            
            poster_path = movie.get("poster_path")
            if poster_path:
                embed.set_image(url=f"https://image.tmdb.org/t/p/w500{poster_path}")
                
            await ctx.send(embed=embed)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
