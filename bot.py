import asyncio
import os
import discord
from discord.ext import commands
import aiohttp
import urllib.parse

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# إعداد البوت مع الصلاحيات المطلوبة
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# معرف الروم المحدد لتثبيت اللوحة وتنظيف الشات
TARGET_CHANNEL_ID = 1567444961442398298
dashboard_message_id = None


class CinemaView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="🔥 Trending Movies",
      style=discord.ButtonStyle.danger,
      custom_id="trending_movies",
  )
  async def trending_movies(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.defer(ephemeral=True)
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        if resp.status == 200:
          data = await resp.json()
          results = data.get("results", [])[:5]
          embed = discord.Embed(
              title="🔥 أبرز الأفلام الرائجة اليوم", color=0xE50914
          )
          for movie in results:
            title = movie.get("title") or movie.get("name")
            vote = movie.get("vote_average", 0)
            embed.add_field(
                name=title, value=f"⭐ التقييم: {vote:.1f}", inline=False
            )
          await interaction.followup.send(embed=embed, ephemeral=True)
        else:
          await interaction.followup.send(
              "❌ حدث خطأ أثناء جلب الأفلام الرائجة.", ephemeral=True
          )

  @discord.ui.button(
      label="📺 Trending TV",
      style=discord.ButtonStyle.primary,
      custom_id="trending_tv",
  )
  async def trending_tv(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.defer(ephemeral=True)
    url = f"https://api.themoviedb.org/3/trending/tv/day?api_key={TMDB_API_KEY}"
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        if resp.status == 200:
          data = await resp.json()
          results = data.get("results", [])[:5]
          embed = discord.Embed(
              title="📺 أبرز المسلسلات الرائجة اليوم", color=0x1F8B4C
          )
          for tv in results:
            title = tv.get("name")
            vote = tv.get("vote_average", 0)
            embed.add_field(
                name=title, value=f"⭐ التقييم: {vote:.1f}", inline=False
            )
          await interaction.followup.send(embed=embed, ephemeral=True)
        else:
          await interaction.followup.send(
              "❌ حدث خطأ أثناء جلب المسلسلات الرائجة.", ephemeral=True
          )

  @discord.ui.button(
      label="🌸 Anime", style=discord.ButtonStyle.success, custom_id="trending_anime"
  )
  async def trending_anime(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.defer(ephemeral=True)
    url = f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&with_genres=16&sort_by=popularity.desc"
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        if resp.status == 200:
          data = await resp.json()
          results = data.get("results", [])[:5]
          embed = discord.Embed(
              title="🌸 أبرز أعمال الأنمي الرائجة", color=0x2ECC71
          )
          for anime in results:
            title = anime.get("name")
            vote = anime.get("vote_average", 0)
            embed.add_field(
                name=title, value=f"⭐ التقييم: {vote:.1f}", inline=False
            )
          await interaction.followup.send(embed=embed, ephemeral=True)
        else:
          await interaction.followup.send(
              "❌ حدث خطأ أثناء جلب الأنمي.", ephemeral=True
          )


class MediaButtons(discord.ui.View):

  def __init__(self, media_id, media_type, title):
    super().__init__(timeout=180)

    # رابط المشغل المباشر (Vidsrc) لكي يحضر الزول الفيلم أو المسلسل فوراً
    if media_type == "tv" or media_type == "anime":
      watch_url = f"https://vidsrc.xyz/embed/tv?tmdb={media_id}"
    else:
      watch_url = f"https://vidsrc.xyz/embed/movie?tmdb={media_id}"

    # رابط يوتيوب دقيق للـ Trailer مع اسم العمل
    query_encoded = urllib.parse.quote(f"{title} official trailer")
    trailer_url = f"https://www.youtube.com/results?search_query={query_encoded}"

    # رابط Simkl للبحث عن العمل
    simkl_encoded = urllib.parse.quote(title)
    simkl_url = f"https://simkl.com/search/?q={simkl_encoded}"

    # زر المشاهدة مع الإيموجي المطلوب ⏹️
    self.add_item(
        discord.ui.Button(
            label="Watch",
            style=discord.ButtonStyle.link,
            url=watch_url,
            emoji="⏹️",
        )
    )
    # زر إعلان اليوتيوب مع الإيموجي المخصص
    self.add_item(
        discord.ui.Button(
            label="Trailer",
            style=discord.ButtonStyle.link,
            url=trailer_url,
            emoji="▶️",
        )
    )
    # زر Simkl
    self.add_item(
        discord.ui.Button(
            label="Simkl",
            style=discord.ButtonStyle.link,
            url=simkl_url,
            emoji="🔗",
        )
    )


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name}")
  bot.add_view(CinemaView())
  channel = bot.get_channel(TARGET_CHANNEL_ID)
  if channel:
    global dashboard_message_id
    try:
      await channel.purge(
          limit=50, check=lambda m: m.id != dashboard_message_id and not m.pinned
      )
    except Exception:
      pass

    embed = discord.Embed(
        title="🎬 SUDANSHIP-CINEMA",
        description=(
            "اختر أحد التصنيفات أدناه لتصفح أحدث الأفلام والمسلسلات والأنمي:"
        ),
        color=0xE50914,
    )
    embed.set_image(
        url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba"
    )
    embed.set_footer(text="Powered by TMDB & SUDANSHIP")

    msg = await channel.send(embed=embed, view=CinemaView())
    dashboard_message_id = msg.id


@bot.event
async def on_message(message):
  if message.author.bot:
    return

  if message.channel.id == TARGET_CHANNEL_ID:
    await bot.process_commands(message)

    # التنظيف التلقائي بعد دقيقتين
    await asyncio.sleep(120)
    try:
      if message.id != dashboard_message_id:
        await message.delete()
    except Exception:
      pass
    return

  await bot.process_commands(message)


@bot.command(name="movie")
async def movie_search(ctx, *, query: str = None):
  try:
    await ctx.message.delete()
  except Exception:
    pass

  if not query:
    embed = discord.Embed(
        title="🎬 SUDANSHIP-CINEMA",
        description="استخدم الأمر هكذا: `!movie اسم الفيلم أو المسلسل`",
        color=0xE50914,
    )
    msg_err = await ctx.send(embed=embed)
    await asyncio.sleep(10)
    try:
      await msg_err.delete()
    except Exception:
      pass
    return

  url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      if resp.status == 200:
        data = await resp.json()
        results = data.get("results", [])
        if not results:
          msg_err = await ctx.send("❌ عذراً، لم يتم العثور على نتائج مطابقة.")
          await asyncio.sleep(10)
          try:
            await msg_err.delete()
          except Exception:
            pass
          return

        item = results[0]
        title = item.get("title") or item.get("name", "بدون عنوان")
        overview = item.get("overview", "لا توجد نبذة متوفرة.")
        vote = item.get("vote_average", 0)
        poster_path = item.get("poster_path")
        media_type = item.get("media_type", "movie")
        media_id = item.get("id")

        poster_url = (
            f"https://image.tmdb.org/t/p/w500{poster_path}"
            if poster_path
            else "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba"
        )

        embed = discord.Embed(
            title=title, description=overview[:300] + "...", color=0xE50914
        )
        embed.set_image(url=poster_url)
        embed.add_field(name="⭐ التقييم", value=f"{vote:.1f}", inline=True)
        embed.add_field(name="📁 التصنيف", value=media_type.upper(), inline=True)

        view = MediaButtons(media_id, media_type, title)
        result_msg = await ctx.send(embed=embed, view=view)

        # حذف نتيجة البحث بعد دقيقتين تلقائياً لتنظيف الشات
        await asyncio.sleep(120)
        try:
          await result_msg.delete()
        except Exception:
          pass
      else:
        msg_err = await ctx.send("❌ حدث خطأ في الاتصال بقاعدة بيانات الأفلام.")
        await asyncio.sleep(10)
        try:
          await msg_err.delete()
        except Exception:
          pass


bot.run(DISCORD_TOKEN)
