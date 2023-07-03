import disnake
from disnake.ext import commands
import sqlite3
from datetime import datetime
from disnake.ext.commands import Param
from disnake.utils import get
from disnake.ui import Button
from disnake import TextInputStyle, ButtonStyle
global embedColor
embedColor=4143049       
    
        
class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('logs.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                message_id INTEGER,
                                user_id INTEGER,
                                reason TEXT,
                                moderator TEXT,
                                notes TEXT,
                                punishment TEXT,
                                removed INTEGER,
                                dmmsg_id INTEGER,
                                servermsg_id INTEGER,
                                dm_id INTEGER,
                                channel_id INTEGER
                            )''')
        self.conn.commit()

    def create_log_embed(self, log_id, user, reason, author_name, notes, punishment):
        embed = disnake.Embed(title=f"{user.display_name}: {punishment}", 
            color=embedColor, # I KNOW ITS A MAGIC NUMBER SHUT THE FUCK UP)        
            timestamp=datetime.now(), #Get the datetime... now...
                              )
        
        embed.add_field(name="<:Num:1124124537580179536>  Case Number", value=log_id)
        embed.add_field(name="<:Reason:1124124961712394310>   Reason", value=reason)
        embed.add_field(name="<:Note:1124096605944037438> Notes", value=notes, inline = False)
        return embed
    
##    @commands.slash_command()
##    async def kill(self, inter: disnake.ApplicationCommandInteraction):
##        category = disnake.utils.get(inter.guild.categories, name = "📬 | Support tickets")
##        for channel in category.channels:
##            await channel.delete()
    
    @commands.slash_command(description="Log a moderation action")
    async def log(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.User,
        reason: str,
        notes: str = "N/A",
        punishment: str = Param(
            choices=[
                "Verbal Warning",
                "1 Hour Ban",
                "3 Hour Ban",
                "6 Hour Ban",
                "1 Day Ban",
                "3 Day Ban",
                "5 Day Ban",
                "7 Day Ban",
                "14 Day Ban",
                "Permanent Ban",
                "Permanent Ban Without Appeal"
            ]
        )
    ):
        server = inter.guild.name
        inChannelMsg = f'''
    **Dear {user},**

    We regret to inform you that after investigation, we have determined that you have violated {server} guidelines.

    The results of our investigation are linked below, and a **link to your appeals site** is included.

    Please remember to abide by the server rules in the future.

    **Regards,**
    **{server} Management Team**
    '''
        inDMMessage= f'''
    **Dear {user},**

    We regret to inform you that after close investigation, we have concluded that you have by greater weight of the evidence violated {inter.guild.name} Community Guidelines (The Rules).

    Due to this, our staff team has decided it is in the server's best interest to give you a **{punishment}.**

    You should be aware, however, that you have **rights** in this case. We believe everyone deserves to be heard, so if you so desire, you may appeal this action using this link for our records:
    https://smpwa.ca/appeal

    You also have the right to your evidence. You are able to request the evidence provided by your moderator as well as the pertinent information from your log. Note that this will not include any external notes the moderator may have made during extensive investigation.

    We hope this will be a learning experience for you.

    **Regards,**
    **{inter.guild.name} Management Team**
    '''    
        await inter.response.defer(with_message=True, ephemeral=True)
        log_id = self.get_next_log_id()

        channel = disnake.utils.get(inter.guild.channels, name="📂moderation")

        log_embed = self.create_log_embed(log_id, user, reason, inter.author.name, notes, punishment)

        # Add Edit button
        edit_button = Button(
            style=ButtonStyle.primary,
            label="Edit",
            custom_id=f"edit_log:{log_id}",
        )
        log_embed.set_footer(
            text=f"Logged case by {inter.author.display_name}",
            icon_url=inter.author.display_avatar,
        )
        log_embed.set_author( # Narcissism
            name="SMPWACA Moderation",
            icon_url="https://cdn.discordapp.com/attachments/1003324050950586488/1036996275985453067/Protection_Color.png",
        )
        log_embed.set_thumbnail(user.display_avatar)
        

        # Add Remove button
        remove_button = Button(
            style=ButtonStyle.danger,
            custom_id=f"remove_log:{log_id}",
            emoji = "<:trash2:1124096546032603347> "
        )

        # Add Reinstate button
        reinstate_button = Button(
            style=ButtonStyle.primary,
            label="Reinstate",
            custom_id=f"reinstate_log:{log_id}",
            disabled=True,  # Initially disabled
        )

        action_row = [edit_button, remove_button]

        message = await channel.send(embed=log_embed, components=action_row)
        
        # Get the message ID of the logged message
        message_id = message.id

        # Log the moderation action in the database
        self.cursor.execute(
            '''INSERT INTO logs
            (log_id, message_id, user_id, reason, moderator, notes, punishment, removed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (log_id, message_id, user.id, reason, inter.author.display_name, notes,punishment, 0)
        )
        self.conn.commit()
 ############################################# -- SEND MESSAGE TO USER -- #############################################################################       

        log = self.get_log(log_id)
        member = user

        overwrites = {
            member.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            get(member.guild.roles, name="Staff"): disnake.PermissionOverwrite(read_messages = True),
            member: disnake.PermissionOverwrite(read_messages = True)}
        category = disnake.utils.get(member.guild.categories, name = "📬 | Support tickets")
        channel = await member.guild.create_text_channel(f"notice-{member.display_name}", overwrites=overwrites, category=category)
        print(channel.id)
        await channel.send(f"**ATTN:** {inter.author.mention} {user.mention}")


        logmsg = disnake.Embed(
            title=f"NOTICE FOR: {user.display_name}", # Smart or smoothbrain?????
            color=disnake.Colour.brand_red(), # I KNOW ITS A MAGIC NUMBER SHUT THE FUCK UP
            description=inChannelMsg,
            timestamp=datetime.now(), #Get the datetime... now...
        )

        logmsg.set_author( # Narcissism
            name="SMPWACA Moderation",
            icon_url="https://cdn.discordapp.com/attachments/1003324050950586488/1036996275985453067/Protection_Color.png",
        )
        logmsg.set_footer( # Show the moderator
            text=f"Your moderator: {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
        logmsg.set_thumbnail(user.display_avatar)
        logmsg.add_field(name="<:NumRed:1124124538905575444> Case Number: ", value=log_id, inline=True)
        logmsg.add_field(name="<:Punishment:1124125689772257310> Action Taken: ", value=punishment, inline=True)
        logmsg.add_field(name="<:ReasonRed:1124124959158054912> Reason: ", value=reason, inline=True)
        logmsg.add_field(name="<:NoteRed:1124125152666456134>Moderator Notes: ", value=notes, inline = False)
        logmsg.add_field(name="<:StaffRed:1124124861271392346> Your Moderator: ", value=inter.author.name, inline=True)
        appeal = Button(label='Appeal Ban', url="https://smpwa.ca/appeal", style=disnake.ButtonStyle.link, emoji = "<:Appeal:1124143624783941632> ")
        close = Button(label="Close Ticket", custom_id=f"close: {inter.author.id}",style=disnake.ButtonStyle.danger)
        message = await channel.send(embed=logmsg, components = [appeal, close])
        print(message.id)
        dmmsg = await user.send(embed=logmsg, components = [appeal])
        # Get the message ID of the logged message
        servermsg_id = message.id
        dmmsg_id = dmmsg.id
       
        if log:
            #
            self.cursor.execute(
                'UPDATE logs SET servermsg_id = ? WHERE log_id = ?',
                (servermsg_id, log_id)
            )
            self.cursor.execute(
                'UPDATE logs SET dmmsg_id = ? WHERE log_id = ?',
                (dmmsg_id, log_id)
            )
            self.cursor.execute(
                'UPDATE logs SET channel_id = ? WHERE log_id = ?',
                (channel.id, log_id)
            )
            self.cursor.execute(
                'UPDATE logs SET dm_id = ? WHERE log_id = ?',
                (user.dm_channel.id, log_id)
            )
            
            self.conn.commit()






        query = "SELECT COUNT(*) FROM logs WHERE user_id = ? AND removed = 0"
        self.cursor.execute(query, (user.id,))
        count = self.cursor.fetchone()[0]

        await inter.edit_original_response(
            f"{user.display_name} has been logged. They currently have {count} offence(s)"
        )

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        custom_id = inter.component.custom_id
        try:
            log_id = int(custom_id.split(":")[1])
        except:
            print("No LogID Found for Logging System!")

        if custom_id.startswith("edit_log"):
            await self.handle_edit_button(inter, log_id)
        elif custom_id.startswith("remove_log"):
            await self.handle_remove_button(inter, log_id)
        elif custom_id.startswith("reinstate_log"):
            await self.handle_reinstate_button(inter, log_id)

        elif custom_id.startswith("user_logs_detail"):
            cursor = self.cursor
            user_id = int(inter.component.custom_id.split("_")[-1])
            user = await self.bot.fetch_user(user_id)
            query = "SELECT * FROM logs WHERE user_id = ? AND removed = 0"
            cursor.execute(query, (user_id,))
            logs = cursor.fetchall()
            
            if logs:
                embed = disnake.Embed(
                    title=f"Moderation History of: {user.display_name}",
                    color=4143049
                )
                
                for log in logs:
                    log_id, message_id, user_id, reason, moderator, notes, punishment, removed, dmmsg_id, servermsg_id, dm_id, channel_id = log
                    embed.add_field(name=f"<:Num:1124124537580179536> Case Number: {log_id}", value=f"Punishment: {punishment}\nReason: {reason}\nModerator: {moderator}\n---", inline=False)
                embed.set_thumbnail(user.display_avatar)
                await inter.response.edit_message(embed=embed, components = [])
            else:
                await inter.response.edit_message(content="No logs found for the user.")
            

    async def handle_edit_button(self, inter: disnake.MessageInteraction, log_id: int):
        custom_id = inter.component.custom_id
        log_id = int(custom_id.split(":")[1])
        log = self.get_log(log_id)
        if log:
            # Check if the log is already removed
            if log[7] == 1:
                await inter.send(
                    f"Log {log_id} has been removed and cannot be edited.",
                    ephemeral=True
                )
                return

            # Retrieve the log embed message
            channel = disnake.utils.get(inter.guild.channels, name="📂moderation")
            message = inter.message.id

            
            
            # Reason input field
            reason_input = disnake.ui.TextInput(
                label="New Reason:",
                placeholder="Enter the new reason...",
                min_length=1,
                max_length=256,
                custom_id=f"edit_reason:{log_id}",
                value=log[3]  # Set the current reason as the initial value
            )
            

            # Punishment input field
            punishment_input = disnake.ui.TextInput(
                label="New Punishment:",
                placeholder="Enter the new punishment...",
                min_length=1,
                max_length=256,
                custom_id=f"punishment_reason:{log_id}",
                value=log[6]  # Set the current reason as the initial value
            )

            # Notes input field
            notes_input = disnake.ui.TextInput(
                label="New Notes:",
                placeholder="Enter the new notes...",
                min_length=1,
                max_length=256,
                custom_id=f"edit_notes:{log_id}",
                value=log[5]  # Set the current notes as the initial value
            )
            user = await self.bot.fetch_user(int(log[2]))
            # Username input field
            username_input = disnake.ui.TextInput(
                label="New Username:",
                placeholder="Enter the new username...",
                min_length=1,
                max_length=256,
                custom_id=f"edit_username:{log_id}",
                value=user.display_name  # Set the current username as the initial value
            )

            # Submit button
            submit_button = disnake.ui.Button(
                style=disnake.ButtonStyle.primary,
                label="Submit",
                custom_id=f"submit_edit:{log_id}"
            )
            # Create a modal for editing the log entry
            modal = disnake.ui.Modal(title="Edit Log",custom_id=f"editLogModal:{log_id}", components=[username_input,reason_input,punishment_input,notes_input])
            # Add items to the modal



            await inter.response.send_modal(modal)

        else:
            await inter.send(
                f"No log found with ID {log_id}.",
                ephemeral=True
            )



    async def handle_remove_button(self, inter: disnake.MessageInteraction, log_id: int):
        # Retrieve the log entry from the database
        log = self.get_log(log_id)

        if log:
            # Update the 'removed' field in the database
            self.cursor.execute(
                'UPDATE logs SET removed = ? WHERE log_id = ?',
                (1, log_id)
            )
            self.conn.commit()

            await inter.send(
                f"Log {log_id} has been removed.",
                ephemeral=True
            )

            # Add Edit button
            edit_button = Button(
                style=ButtonStyle.primary,
                label="Edit",
                custom_id=f"edit_log:{log_id}",
                disabled=True,  # Initially disabled
            )

            # Add Reinstate button
            reinstate_button = Button(
                style=ButtonStyle.success,
                custom_id=f"reinstate_log:{log_id}",
                emoji="<:restore:1124096542228365343>",
                disabled=False,  # Initially disabled
        )
            # Retrieve the log embed message
            channel = disnake.utils.get(inter.guild.channels, name="📂moderation")
            message_id = log[1]

            try:
                message = await channel.fetch_message(message_id)
            except disnake.NotFound:
                await inter.send(
                    f"Unable to find the log message with ID {message_id}.",
                    ephemeral=True
                )
                return
            user = await self.bot.fetch_user(int(log[2]))
            # Update the embed fields with the new values
            embed = message.embeds[0]
            embed.color=disnake.Colour.red()
            embed.title = f"{user.display_name}: LOG REMOVED"
            embed.set_field_at(0, name="<:NumRed:1124124538905575444> Case Number",value=log[0], inline=True)
            embed.set_field_at(1, name="<:ReasonRed:1124124959158054912> Reason",value=log[3], inline=True)
            embed.set_field_at(2, name="<:NoteRed:1124125152666456134> Notes",value=log[5], inline=False)
            try:
                embed.set_field_at(3, name="<:StaffRed:1124124861271392346> Initial Moderator",value=log[4], inline=True)
            except IndexError:
                embed.add_field(name="<:StaffRed:1124124861271392346> Initial Moderator",value=log[4])
            try:
                embed.set_field_at(4, name="<:Punishment:1124125689772257310> Action",value=log[6], inline=True)
            except IndexError:
                embed.add_field(name="<:Punishment:1124125689772257310> Action",value=log[6])
            
            embed.set_footer(
            text=f"❗Log removed by {inter.author.name}❗",
            icon_url=inter.author.display_avatar,
        )

            await inter.message.edit(embed=embed,components=[edit_button,reinstate_button])

            embed = disnake.Embed(title=f"LOG REMOVED", 
            color=disnake.Color.green(), # I KNOW ITS A MAGIC NUMBER SHUT THE FUCK UP)        
            timestamp=datetime.now(), #Get the datetime... now...
                                description = f"Please be aware that your **{log[6]}** has been removed and no longer counts towards your moderation history."
                              )
        
            embed.add_field(name="<:NumGreen:1124124535701127218> Case Number",value=log[0], inline=True)
            embed.add_field(name="<:ReasonGreen:1124124962794516592> Reason",value=log[3], inline=True)
            embed.add_field(name="<:NoteGreen:1124125150556729364> Notes",value=log[5], inline=False)
            embed.set_footer(
            text=f"Log removed by {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
            try:
                # Fetch Messagte and Send to Ticket
                message_id = log[9]
                channel = disnake.utils.get(inter.guild.channels, id=log[11])
                message = await channel.fetch_message(int(message_id))
                await channel.send(embed=embed)
            except disnake.NotFound:
                pass

            # Fetch DM Channel and send to User
            message_id = log[8]
            dm = log[10]
            channel = await self.bot.fetch_user(log[2])
            message = await channel.fetch_message(message_id)
            await channel.send(embed=embed)
            
        else:
            await inter.send(
                f"<:wacanotice:1109510616206557254> **NOTICE:** No log found with ID {log_id}.",
                ephemeral=True
            )

    async def handle_reinstate_button(self, inter: disnake.MessageInteraction, log_id: int):
        # Retrieve the log entry from the database
        log = self.get_log(log_id)

        if log:
            # Update the 'removed' field in the database
            self.cursor.execute(
                'UPDATE logs SET removed = ? WHERE log_id = ?',
                (0, log_id)
            )
            self.conn.commit()

            await inter.send(
                f"Log {log_id} has been reinstated.",
                ephemeral=True
            )
            # Add Edit button
            edit_button = Button(
                style=ButtonStyle.primary,
                label="Edit",
                custom_id=f"edit_log:{log_id}",
                disabled=False,  # Initially disabled
            )
            # Add Remove button
            remove_button = Button(
                style=ButtonStyle.danger,
                custom_id=f"remove_log:{log_id}",
                emoji = "<:trash2:1124096546032603347> "
            )
            channel = disnake.utils.get(inter.guild.channels, name="📂moderation")
            message_id = log[1]

            try:
                message = await channel.fetch_message(message_id)
            except disnake.NotFound:
                await inter.send(
                    f"Unable to find the log message with ID {message_id}.",
                    ephemeral=True
                )
                return
            user = await self.bot.fetch_user(int(log[2]))
             # Update the embed fields with the new values
            embed = message.embeds[0]
            embed.title = f"{user.display_name}: {log[6]}"
            embed.color=disnake.Colour.green()
            embed.set_field_at(0, name="<:NumGreen:1124124535701127218> Case Number",value=log[0], inline=True)
            embed.set_field_at(1, name="<:ReasonGreen:1124124962794516592> Reason",value=log[3], inline=True)
            embed.set_field_at(2, name="<:NoteGreen:1124125150556729364> Notes",value=log[5], inline=False)
            try:
                embed.set_field_at(3, name="<:StaffGreen:1124124859237138543> Initial Moderator",value=log[4], inline=True)
            except IndexError:
                embed.add_field(name="<:StaffGreen:1124124859237138543> Initial Moderator",value=log[4])
            embed.remove_field(4)
            embed.set_footer(
            text=f"❗Log reinstated by {inter.author.name}❗",
            icon_url=inter.author.display_avatar,
        )

            await inter.message.edit(embed=embed,components=[edit_button,remove_button])
            






            embed = disnake.Embed(title=f"LOG REINSTATED", 
            color=disnake.Color.red(), # I KNOW ITS A MAGIC NUMBER SHUT THE FUCK UP)        
            timestamp=datetime.now(), #Get the datetime... now...
                                description = f"Please be aware that your **{log[6]}** has been restored and now counts towards your moderation history"
                              )
        
            embed.add_field(name="<:NumRed:1124124538905575444> Case Number",value=log[0], inline=True)
            embed.add_field(name="<:ReasonRed:1124124959158054912> Reason",value=log[3], inline=True)
            embed.add_field(name="<:NoteRed:1124125152666456134> Notes",value=log[5], inline=False)
            embed.set_footer(
            text=f"Log reinstated by {inter.author.name}",
            icon_url=inter.author.display_avatar,
        )
            try:
                # Fetch Messagte and Send to Ticket
                message_id = log[9]
                channel = disnake.utils.get(inter.guild.channels, id=log[11])
                await channel.send(embed=embed)
            except disnake.NotFound:
                pass

            # Fetch DM Channel and send to User
            message_id = log[8]
            dm = log[10]
            channel = await self.bot.fetch_user(log[2])
            await channel.send(embed=embed)







        else:
            await inter.send(
                f"No log found with ID {log_id}.",
                ephemeral=True
            )

            
    def get_next_log_id(self):
        self.cursor.execute('SELECT MAX(log_id) FROM logs')
        result = self.cursor.fetchone()[0]
        if result:
            return result + 1
        return 1

    def get_log(self, log_id):
        self.cursor.execute('SELECT * FROM logs WHERE log_id = ?', (log_id,))
        return self.cursor.fetchone()
    
    @commands.Cog.listener()
    async def on_modal_submit(self, inter: disnake.ModalInteraction):

        if inter.custom_id.startswith("editLogModal"):
            log_id = int(inter.custom_id.split(":")[1])
            log = self.get_log(log_id)
            dic=inter.text_values
            name=dic[f"edit_username:{log_id}"]
            punish=dic[f"punishment_reason:{log_id}"]
            reason=dic[f"edit_reason:{log_id}"]
            notes=dic[f"edit_notes:{log_id}"]
            if log:
                # Check if the log is already removed
                if log[6] == 1:
                    await inter.send(
                        f"Log {log_id} has been removed and cannot be edited.",
                        ephemeral=True
                    )
                    return

                # Retrieve the log embed message
                channel = disnake.utils.get(inter.guild.channels, name="📂moderation")
                message_id = log[1]

                try:
                    message = await channel.fetch_message(message_id)
                except disnake.NotFound:
                    await inter.send(
                        f"Unable to find the log message with ID {message_id}.",
                        ephemeral=True
                    )
                    return

                # Update the embed fields with the new values
                embed = message.embeds[0]
                embed.color=embedColor
                try:
                    embed.set_field_at(3, name="<:Staff:1124124862487732255> Initial Moderator",value=log[4], inline=True)
                except IndexError:
                    embed.add_field(name="<:Staff:1124124862487732255> Initial Moderator",value=log[4])
                try:
                    embed.set_field_at(4, name="<:Punishment:1124125689772257310> Action",value=log[6], inline=True)
                except IndexError:
                    pass
                
                embed.set_footer(
                text=f"❗Log edited by {inter.author.name}❗",
                icon_url=inter.author.display_avatar,
            )
                embed.title = f"{name}: {punish}"
                embed.set_field_at(0, name="<:Num:1124124537580179536> Case Number",value=log[0], inline=True)
                embed.set_field_at(1, name="<:Reason:1124124961712394310> Reason", value=reason, inline=True)
                embed.set_field_at(2, name="<:Note:1124096605944037438> Notes", value=notes, inline=False)
                
                # Update the log entry in the database
                self.cursor.execute(
                    'UPDATE logs SET punishment = ?, reason = ?, moderator = ?, notes = ? WHERE log_id = ?',
                    (punish, reason, name, notes, log_id)
                )
                self.conn.commit()
                
                #Update the log
                await message.edit(embed=embed)


                #Set Embed
                embed = message.embeds[0]
                embed.title = f"UPDATE FOR: {name}"
                embed.description = f"""
**Dear {name},**

Your case has been updated by a staff member! Please review the changes to your case, and, if required, submit a new appeal. Thank you for your understanding.

"""
                embed.set_field_at(0, name="<:NumRed:1124124538905575444> Case Number",value=log_id, inline=True)
                embed.set_field_at(1, name="<:Punishment:1124125689772257310> Action Taken",value=punish, inline=True)
                embed.set_field_at(2, name="<:ReasonRed:1124124959158054912> Reason",value=reason, inline=True)
                embed.set_field_at(3, name="<:NoteRed:1124125152666456134> Notes",value=log[5], inline=False)
                appeal = Button(label='Appeal Ban', url="https://smpwa.ca/appeal", style=disnake.ButtonStyle.link, emoji = "<:Appeal:1124143624783941632> ")

                try:
                    # Fetch Messagte and Send to Ticket
                    message_id = log[9]
                    channel = disnake.utils.get(inter.guild.channels, id=log[11])
                    message = await channel.fetch_message(int(message_id))
                    await message.edit(embed=embed, components=[appeal])
                except disnake.NotFound:
                    pass

                # Fetch DM Channel and send to User
                message_id = log[8]
                dm = log[10]
                channel = await self.bot.fetch_user(log[2])
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed, components=[appeal])
                await inter.response.send_message("Done!")












                
    @commands.slash_command(description="Find a user's mod history")
    async def history(self, inter, user: disnake.User):
        cursor = self.cursor
        user_id = user.id
        query = "SELECT COUNT(*) FROM logs WHERE user_id = ? AND removed = 0"
        cursor.execute(query, (user_id,))
        count = cursor.fetchone()[0]
        
        embed = disnake.Embed(
            title="User Logs",
            description=f"Total logs for {user.mention}: {count}",
            color=4143049
        )
        embed.set_thumbnail(url=user.avatar.url)
        
        if count > 0:
            # Add "More Detail" button
            components = [
                disnake.ui.Button(
                    style=disnake.ButtonStyle.primary,
                    label="More Detail",
                    custom_id=f"user_logs_detail_{user_id}"
                )
            ]
            action_row = disnake.ui.ActionRow(*components)
            await inter.response.send_message(embed=embed, components=[action_row])
        else:
            await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Find any mod log!")
    async def findlog(self, inter, log_id: int):
        cursor = self.cursor
        query = "SELECT * FROM logs WHERE log_id = ?"
        cursor.execute(query, (log_id,))
        log = cursor.fetchone()
        
        if log:
            log_id, message_id, user_id, reason, moderator, notes, punishment, removed, dmmsg_id, servermsg_id, dm_id, channel_id = log
            
            embed = disnake.Embed(
                title=f"{inter.author.display_name}: {punishment}",
                color=4143049,
                timestamp=inter.created_at
            )
            embed.add_field(name="<:Num:1124124537580179536> Case Number", value=log_id, inline=False)
            embed.add_field(name="<:Reason:1124124961712394310> Reason", value=reason, inline=False)
            embed.add_field(name="<:Note:1124096605944037438> Notes", value=notes, inline=False)
            embed.set_footer(
                text=f"Logged case by {inter.author.display_name}",
                icon_url=inter.author.avatar.url
            )
            embed.set_author(
                name="SMPWACA Moderation",
                icon_url="https://cdn.discordapp.com/attachments/1003324050950586488/1036996275985453067/Protection_Color.png"
            )
            embed.set_thumbnail(url=inter.author.avatar.url)
            
            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message("Log not found.")


def setup(bot):
    bot.add_cog(Log(bot))
