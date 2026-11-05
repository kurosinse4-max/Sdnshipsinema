import os
import aiohttp
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

@bot.command(name="kuro", help="البحث عن الأفلام وعرض تفاصيلها وروابط المشاهدة")
async def search_movie(ctx, *, query: str):
    if not TMDB_API_KEY:
        await ctx.send("⚠️ تنبيه: مفتاح TMDB API غير معرّف في متغيرات البيئة!")
        return

    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await ctx.send("❌ حدث خطأ أثناء الاتصال بقاعدة بيانات الأفلام.")
                return
            
            data = await response.json()
            results = data.get("results", [])
            
            if not results:
                await ctx.send(f"❌ لم يتم العثور على أي فيلم مطابق لـ: **{query}**")
                return
            
            movie = results[0]
            title = movie.get("title", "بدون عنوان")
            overview = movie.get("overview", "لا توجد نبذة متوفرة.")
            vote_average = movie.get("vote_average", "N/A")
            release_date = movie.get("release_date", "غير معروف")
            movie_id = movie.get("id")
            poster_path = movie.get("poster_path")
            
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            watch_link = f"https://vidsrc.to/embed/movie/{movie_id}"

            embed = discord.Embed(
                title=title,
                description=overview[:300] + ("..." if len(overview) > 300 else ""),
                color=discord.Color.dark_embed()
            )
            embed.add_field(name="⭐ التقييم", value=str(vote_average), inline=True)
            embed.add_field(name="📅 تاريخ الإصدار", value=release_date, inline=True)
            embed.add_field(name="🔗 رابط المشاهدة المباشرة", value=f"[اضغط هنا للمشاهدة على vidsrc]({watch_link})", inline=False)
            
            if poster_url:
                embed.set_image(url=poster_url)
                
            embed.set_footer(text="!KURO Cinema Bot | Powered by TMDB & Vidsrc")
            
            await ctx.send(embed=embed)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ يرجى تعيين رمز البوت (DISCORD_TOKEN) في البيئة.")
