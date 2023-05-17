import disnake
print("Importing disnake")
from disnake.ext.commands import Bot
from commands.ping import Ping
print("Importing RVDS")
from RVDS.MDS import MDS
print("Completed!")
print("Importing AI Support")

from AHS import AISupport#, Reminder

print("Completed!")
from commands import owo,notify
from training import accept
from moderation.Log import Log
from moderation import DMListener
from onboarding.verified import on_verification
from eastereggs import insanity
from eastereggs import Mitochondria
from eastereggs import bless
from moderation import Close
from commands import hostinfo
import os
global testingMode
global pingOn
global veriOn
global owoOn
global logOn
global supportOn
global reminderOn
global notifyOn
global acceptOn
global insanityOn
global mitoOn
global MDSOn
global hostOn
global botVer
global DMListen
global blessOn

print("Setting variables")
testingMode = False
pingOn = "Online :green_circle:"
veriOn = "Online :green_circle:"
owoOn = "Online :green_circle:"
logOn = "Online :green_circle:"
supportOn = "Online :green_circle:"
reminderOn="Online :green_circle:"
notifyOn="Online :green_circle:"
acceptOn="Online :green_circle:"
insanityOn="Online :green_circle:"
mitoOn="Online :green_circle:"
MDSOn = "Online :green_circle:"
botVer = "2.0.2"
DMListen = "Online :green_circle:"
blessOn = "Online :green_circle:"
hostOn = "Online :green_circle:"

bot = Bot("!",sync_commands_debug=True,
          intents=disnake.Intents.all(),
          test_guilds=[912725322166829116])



## ADD COGS
bot.add_cog(Close.Close(bot))
try:
    bot.add_cog(DMListener.DMListener(bot))
except:
    DMListen = "Offline :red_circle:"
try:
    bot.add_cog(Ping(bot))
except:
    pingOn="Offline :red_circle:"
try:
    bot.add_cog(on_verification(bot))
except:
    veriOn = "Offline :red_circle:"
try:
    bot.add_cog(MDS(bot))
except:
    MDSOn = "Offline :red_circle:"
try:    
    bot.add_cog(owo.OWO(bot))
except:
    owoOn = "Offline :red_circle:"
try:
    bot.add_cog(Log(bot))
except:
    logOn = "Offline :red_circle:"
try:
    bot.add_cog(AISupport.Support(bot))
except:
    supportOn = "Offline :red_circle:"
try:
    bot.add_cog(Reminder.Reminder(bot))
except:
    reminderOn="Offline :red_circle:"
try:
    bot.add_cog(notify.notify(bot))
except:
    notifyOn = "Offline :red_circle:"
try:
    bot.add_cog(accept.accept(bot))
except:
    acceptOn = "Offline :red_circle:"
try:
    bot.add_cog(insanity.EasterEggs(bot))
except:
    insanityOn = "Offline :red_circle:"
try:
    bot.add_cog(bless.Bless(bot))
except:
    blessOn = "Offline :red_circle:"
try:  
    bot.add_cog(Mitochondria.Mitochondria(bot))
except:
    mitoOn = "Offline :red_circle:"
try:  
    bot.add_cog(hostinfo.hoster(bot))
except:
    hostOn = "Offline :red_circle:"
@bot.slash_command(description="WACA-Guard Information")
async def about(inter):
    botVer = "2.2.3"
    depDate = "April 11th, 2023"
    embed = disnake.Embed(title=f"About WACA-Guard v. {botVer}", description=f"""

Deployed on: **{depDate}**

Bot latency is {bot.latency * 1000:.2f}ms.

--------------------------------------------

**TEST MODE?** {testingMode}

--------------------------------------------

**COG FUNCTIONALITY ANALYSIS:**

Ping: **{pingOn}**
Verification: **{veriOn}**
OWO Commands: **{owoOn}**
Moderation Logs: **{logOn}**
Support Detection: **{supportOn}**
Friendly Reminders: **{reminderOn}**
Notifications: **{notifyOn}**
Training Commands: **{acceptOn}**
Insanity Easter Egg:**{insanityOn}**
Mitochondria Easter Egg: **{mitoOn}**

**Machine Learning Algorithms:**

Mean Detection System: **{MDSOn}**
NSFW Detection System : **NOT IMPLEMENTED  :red_circle:**

**Listeners:**

DM Listener: **{DMListen}**
OWO Listener: **{owoOn}**
Easter Egg Listeners: **{insanityOn}**

--------------------------------------------

**Notable Changes:**

- Increased MDS training data
- Increased AI Support Data
- Fixed an error with the owoify command
- Fixed an error with the ticketing system

""", color = disnake.Colour.brand_green())
    await inter.response.send_message(embed=embed)




    
token = "OTIxMTAwMzUyMzAzMDMwMzU3.Gse5_e.qJz0DDAcw-2wEN-v7wWdvz-1NeiTPt9ggIN-Iw"
testToken = "MTAzOTE2NjMyODAzODIyODEyMA.GdnGsq.9pcFZAul1zW7Gf0_a6cvBM5aCrUgqTj__DENDM"

if testingMode:
    bot.run(testToken)
else:
    bot.run(token)
