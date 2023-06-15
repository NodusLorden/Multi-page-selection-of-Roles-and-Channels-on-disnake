import configparser
import disnake
from disnake.ext import commands, tasks
import re
import math


config = configparser.ConfigParser()
config.read("config.ini")

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)


@bot.event
async def on_ready():
    print("Ready")


def create_selection_component(custom_id: str, items: list, page: int):
    if items:
        if type(items[0]) == disnake.Role:
            get_option = lambda x, y: disnake.SelectOption(label=x[y].name, value="role_%d" % x[y].id)
        elif type(items[0]) == disnake.TextChannel:
            get_option = lambda x, y: disnake.SelectOption(label=x[y].name, value="channel_%d" % x[y].id)
        else:
            raise ValueError
    else:
        raise ValueError

    items_count = len(items)
    page_count = math.ceil(items_count / 25)

    return [disnake.ui.StringSelect(
        custom_id=custom_id,
        options=[
            get_option(items, i)
            for i in range(25 * page, 25 * page + min(items_count - 25 * page, 25))
        ]),
        disnake.ui.Button(label="<", custom_id="last_selection", disabled=page <= 0),
        disnake.ui.Button(label=">", custom_id="next_selection", disabled=page >= page_count - 1),
    ]


@bot.slash_command(name="choose_role")
async def choose_role(inter: disnake.ApplicationCommandInteraction):
    roles = inter.guild.roles

    await inter.response.send_message(
        content="Страница: 1",
        ephemeral=True,
        delete_after=60,
        components=create_selection_component("select", roles, 0)
    )


@bot.slash_command(name="choose_text_channel")
async def choose_text_channel(inter: disnake.ApplicationCommandInteraction):
    channels = inter.guild.text_channels

    await inter.response.send_message(
        content="Страница: 1",
        ephemeral=True,
        delete_after=60,
        components=create_selection_component("select", channels, 0)
    )


@bot.listen("on_button_click")
async def button_click(inter: disnake.MessageInteraction):

    roles = inter.guild.roles
    roles.reverse()
    roles_count = len(roles)
    page_count = math.ceil(roles_count / 25)

    if inter.component.custom_id == "last_selection":
        page = int(re.fullmatch("\\D+(\\d+)", inter.message.content).group(1)) - 1

        if page > 0:
            page -= 1
            await inter.response.edit_message(
                content=f"Страница: {page + 1}",
                components=create_selection_component("select", roles, page)
            )
        else:
            await inter.response.pong()

    elif inter.component.custom_id == "next_selection":
        page = int(re.fullmatch("\\D+(\\d+)", inter.message.content).group(1)) - 1

        if page < page_count - 1:
            page += 1
            await inter.response.edit_message(
                content=f"Page: {page + 1}",
                components=create_selection_component("select", roles, page)
            )
        else:
            await inter.response.pong()


@bot.listen("on_dropdown")
async def menu_select(inter: disnake.MessageInteraction):

    await inter.response.edit_message()

    if inter.component.custom_id == "select":

        value = inter.resolved_values[0]
        selection_type, item = value.split("_")

        if selection_type == "role":
            role = inter.guild.get_role(int(item))
            print("select role '%s' id=%d" % (role.name, role.id))

        elif selection_type == "channel":
            channel = inter.guild.get_channel(int(item))
            print("select role '%s' id=%id" % (channel.name, channel.id))
        else:
            raise TypeError


bot.run(config["bot"]["TOKEN"])
