import os
import discord
from dotenv import load_dotenv
import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands

# GLOBALS ----------------------------------------------------

# discord
message_cooldown = commands.CooldownMapping.from_cooldown(1.0, 5.0, commands.BucketType.user)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

# google sheets
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
cli = gspread.authorize(creds)

# logic
IS_DEBUG = True

hacker_dict = {}
member_dict = {}

guild = discord.utils.get(client.guilds, name=GUILD)
verify_role = discord.utils.get(guild.roles, name="Verified")
unverified_role = discord.utils.get(guild.roles, name="Verification Needed")

# METHODS ---------------------------------------------------

# sheets operations
def parse_data():
    hacker_data_document = cli.open("hacker data")

    cxc_doc = hacker_data_document.get_worksheet(0)  # TODO: update with actual sheet name and data as needed
    membership_doc = hacker_data_document.get_worksheet(1) # TODO: replace fake with real membership data

    cxc_data = cxc_doc.get_all_records()
    membership_data = membership_doc.get_all_records()

    hacker_dict = {record['username']: record['watiam'] for record in cxc_data}
    member_dict = {record['watiam']: record['isMember'] for record in membership_data}
    
    if IS_DEBUG:
        print(hacker_dict)
        print(member_dict)

# discord events
@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(guild)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )

@client.event
async def on_member_join(member: discord.Member):
    guild = discord.utils.get(client.guilds, name=GUILD)
    verify_role = discord.utils.get(guild.roles,name="Verification Needed")
    if verify_role:
        await member.add_roles(verify_role)

@client.event
async def on_message(message: discord.Message):
    message_str = message.content
    if message_str[0] == "!": # command used
        if message_str == "!verify": # verify single user
            await run_verify(message)
        elif message_str == "!verifyall" and discord.utils.get(message.author.roles, name = "Admin"): # verify all users
            await mass_accept_all(message)

# text commands
async def run_verify(message: discord.Message):
    # when user does !verify, update globals with most recent sheets' state
    parse_data()

    # cooldown
    bucket = message_cooldown.get_bucket(message)
    retry_after = bucket.update_rate_limit()

    if retry_after:
        await message.channel.send(f"Slow down! Try again in {retry_after} seconds.")
    else:
        has_verify_role = discord.utils.get(message.author.roles, name="Verified")
        if has_verify_role:
            await message.channel.send(f"{message.author.mention}, you already have the 'Verified' role.")
        else:
            # check author against dicts
            verify_user(message.author)
            
def mass_accept_all(message: discord.Message):
    # update global dicts
    parse_data()
    for hacker in hacker_dict:
        # find hacker
        hacker_member = discord.utils.get(message.guild.members, name=hacker)
        if hacker_member:
            verify_user(hacker_member)

# verify single user
async def verify_user(user: discord.Member):
    username = user.name
    if username in hacker_dict: # is in approved hackers list
        watiam = hacker_dict[username]
        if member_dict[watiam]: # is a member
            await user.add_roles(verify_role)
            await user.remove_roles(unverified_role)
            await user.send(f"{user.mention}, your 'Verify' role has successfully been added.")
        else:
            await user.send(f"{user.mention}, you are not a DSC member.")
    else:
        await user.send(f"{user.mention}, your username is not in the CxC accepted usernames list.")

# main
def __main__():
    parse_data()
    client.run(TOKEN)

__main__()