
from discord.colour import Color
from discord.ext import commands
import discord
from django.db.models.fields import DecimalField
import checkipo
import requests
from PIL import Image, ImageDraw, ImageFont
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ipobot.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from bot.models import Guilds,Boids
import datetime


token = "OTAxMDUyMDczNzA4MjQwOTE2.YXKQIw.-CaK7BpXAark7tU94Uv-inSkjKk"

# class MyClient(discord.Client):
#     def __init__(self, *args, **options):
#         super().__init__(*args,**kwargs)
    
#     async def on_guild_join(self,guild):
#         print(guild)



def getEmbed(title="You forgot to pass title",color=discord.Colour.orange(),description="forgot desc?"):
    return discord.Embed(
        title=title,
        description=description,
        color=color
    )

async def isServerRegistered(ctx):
    if len(Guilds.objects.filter(guild_id=ctx.message.guild.id)) == 0:
        embed = getEmbed(title="Server Not Registered!!",color=discord.Colour.red(),description="Type '.register' to resiter server before doing anything")
        await ctx.send(embed=embed)
        return 0
    return 1


bot  = commands.Bot(command_prefix=".")
bot.remove_command('help')



@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title = "Awesome Bot Commands",
        description = "Welcome to the help section. Here are all the commands",
        color = discord.Colour.orange()
    )
    embed.add_field(
        name=".help",
        value="Show all available command",
        inline=False
    )
    embed.add_field(
        name=".register",
        value="Register this server for proper functionality",
        inline=False
    )
    embed.add_field(
        name=".iporesult",
        value="""Get Iporesult for all users of given company
        Usage: .iporesult company='nyadi' users="ram shyam hari"
        Available arguments:
        company="<portion of company name will do>"
        users="<name of user separated by space >" you can skip this argument,default [all]
        """,
        inline=False
    )
    embed.add_field(
        name=".add",
        value="Add User and boid\nUsage: .add ravan 1234567890123456",
        inline=False
    )
    embed.add_field(
        name=".listuser",
        value="List all the users and boids",
        inline=False
    )
    
    await ctx.send(embed=embed)


@bot.command()
async def iporesult(ctx,*args):
    print("send the file")
    isRegistered = await isServerRegistered(ctx)
    if isRegistered == 0:
        return
    boids = Boids.objects.filter(guild=Guilds.objects.get(guild_id=ctx.message.guild.id))
    
    print(boids)
    filteredNames = [each.username for each in boids]
    if "--company" in args:
        try:
            companyName = args[args.index('--company')+1].lower()
            if companyName.startswith("--"):
                raise Exception()
            print("name of company",companyName)
        except Exception as e:
            await ctx.send(f"missing company name after --company \nUsage: .iporesult --company <companny name>\nfor More help type : .help")
            return
    else:
        await ctx.send(f"missing --company \nUsage: .iporesult --company <companny name>\nfor More help type : .help")
        return
    if "--users" in args:
        try:
            users = args[args.index('--users')+1]
            if users.startswith("--"):
                raise Exception("""Username cannot start with '--'\nUsage .iporesult --company <company name> --users "<user1 user2 user3>" """)
            print(type(users))
            users = users.split(" ")
            print(type(users))
            print("users are ",users)
        except Exception as e:
            await ctx.send(f"missing users after --users\nError Details:{e}")
            return
        valid_names = filteredNames
        invalid_users = set(users).difference(set(valid_names))
        if len(invalid_users)>0:
            await ctx.send(f"invalid user : {', '.join(invalid_users)}")
            return
        filteredNames = set(users).difference(invalid_users)
        print("filtered names: ",filteredNames)
        
    client = requests.session() #using session is bit more faster than not using it
    try:
        allCompanies = client.get("https://iporesult.cdsc.com.np/result/companyShares/fileUploaded")
        if allCompanies.status_code != 200:
            await ctx.send("failed Try again later")
            return
            print(allCompanies.json()['body'])
        allCompanies = allCompanies.json()['body']
        # print("all comp",allCompanies)
        # .json()['body']
        for company in allCompanies:
            # print(company['name'])
            # print(companyName.lower()+" ==> "+company['name'].lower())
            if companyName.lower() in company['name'].lower():
                # print("vitra aayo")
                checkipo.shareNo = str(company['id'])
                scrip = str(company['scrip'])
                # # print(company['name'])
                # await ctx.send(company['name'])
                break
        else:
            allC = "\n".join([company['name'] for company in allCompanies])
            await ctx.send(f"no such company found\nSelect among these or maybe the one you are looking is not listed yet in iporesult.cdsc.com.np\n{allC}")
            return

    except Exception as e:
        print(f"Error occured while finding company id and name : {e}")
        await ctx.send("Error occured while finding company id and name")
        return

    filteredNameLists = [[each.boid,each.username] for each in boids if each.username in filteredNames]
    checkipo.withThreading(client,filteredNameLists)
    table_str = checkipo.table.get_string().replace(checkipo.colors['red'],"").replace(checkipo.colors['green'],"").replace(checkipo.colors['reset'],"")
    print(table_str)

    len_of_str = table_str.count("\n")
    initial_height = 50 
    each_line_spacing = 20
    final_height = initial_height + len_of_str * each_line_spacing

    im = Image.new("RGB", (400, final_height), "#1a8a8a")
    draw = ImageDraw.Draw(im)

    font = ImageFont.truetype("font/mono1.ttf", 15)
    
    draw.text((30, 10), str(company['name']), font=font,fill="#fff")
    draw.text((30, 30), str(table_str), font=font,fill="#fff")
    im.save("table.png")
    await ctx.send(file=discord.File("table.png"))

    checkipo.table = checkipo.PrettyTable()
    checkipo.table.field_names = ['id','name','status']


@bot.command()
async def add(ctx,*args):
    print(f"got a add request from guild {ctx.message.guild} and author {ctx.message.author}")
    try:
        if len(args)!=2:
            raise Exception("Invalid Format\nUsage: .add username(without space) boid\nExample: .add ram 1234567891234567")
        else:
            if len(args[1])!=16:
                embed = getEmbed(title=f"Invalid Boid {args[1]}",description="Boid should be 16 digit",color=discord.Colour.red())
                await ctx.send(embed=embed)
                return
            guild = Guilds.objects.filter(guild_id=ctx.message.guild.id)
            isRegistered = await isServerRegistered(ctx)
            if isRegistered == 0:
                return

            if len(Boids.objects.filter(guild=guild[0],username=args[0])) > 0 or len(Boids.objects.filter(guild=guild[0],boid=args[1])) > 0:
                embed = getEmbed(title="Already Exists!!",description=f"username: {args[0]} or boid: {args[1]} already exists.",color=discord.Color.red())
                await ctx.send(embed=embed)
                return
            newUser  = Boids(guild=guild[0],username=args[0],boid=args[1])
            newUser.save()
            embed = getEmbed(title="Successfully Added",color=discord.Colour.green(),description=f"Added {args[0]} with boid {args[1]}")
            await ctx.send(embed=embed)
            
    except Exception as e:
        await ctx.send(e)

@bot.command()
async def register(ctx):
    try:
        newGuild = Guilds(guild_id=ctx.message.guild.id,guild_name=ctx.message.guild,bot_added_date=datetime.datetime.now())
        newGuild.save()
        await ctx.send("Registered Successfully")
    except Exception as e:
        if "duplicate key" in str(e):
            await ctx.send("already registered. no need to register anymore")
        else:
            await ctx.send(e)

@bot.command()
async def listuser(ctx):
    isRegistered = await isServerRegistered(ctx)
    if (isRegistered == 0):
        return
    guild_id = ctx.message.guild.id
    users = Boids.objects.filter(guild=Guilds.objects.get(guild_id=guild_id))
    embed = discord.Embed(title="List of Users",color=discord.Colour.orange())
    
    for each in users:
        # print(each.username)
        embed.add_field(name=each.username,value=each.boid,inline=True)
    
    await ctx.send(embed=embed)

if __name__=='__main__':
    
    
    bot.run(token)
