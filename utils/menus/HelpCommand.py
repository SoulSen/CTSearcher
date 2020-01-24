from discord.ext import commands, menus
from .HelpPaginator import HelpPaginator
import discord


class HelpCommand(commands.HelpCommand):
    # How commands should be viewed
    def get_command_signature(self, command):
        return f"{command.name} {command.signature} {' ' * int(17 - len(command.name + command.signature))}:: " \
               f"{command.brief}\n"

    async def send_bot_help(self, mapping):
        e = discord.Embed(title='Command Help', 
                          color=discord.Color.from_rgb(123, 47, 181))
        e.set_author(name=self.context.author, 
                     icon_url=self.context.author.avatar_url)
        e.set_footer(text=f'Current Prefix: {self.context.prefix}')

        # Separate Page
        e_command = e.copy()

        e.set_thumbnail(url='https://avatars2.githubusercontent.com/u/31901301?s=280&v=4')

        e.add_field(name='Download 1.8.9',
                    value='[1.0.0 RC4 Beta](https://github.com/ChatTriggers/ct.js/releases/download/1.0.0RC4/ctjs-1.0'
                          '.0-RC4-1.8.9.jar)\n '
                          '[0.18.4 Stable](https://github.com/ChatTriggers/ct.js/releases/download/0.18.4/ctjs-0.18.4'
                          '-SNAPSHOT-1.8.9.jar)\n '
                          '[0.16.4 Legacy](https://github.com/ChatTriggers/ct.js/releases/download/0.16.6/ctjs-0.16.6'
                          '-SNAPSHOT-1.8.9.jar)')

        e.add_field(name='Download 1.12.2',
                    value='[0.18.4 Stable](https://github.com/ChatTriggers/ct.js/releases/download/0.18.4/ctjs-0.18.4'
                          '-SNAPSHOT-1.12.2.jar)\n '
                          '[0.16.4 Legacy](https://github.com/ChatTriggers/ct.js/releases/download/0.16.6/ctjs-0.16.6'
                          '-SNAPSHOT-1.12.2.jar)')

        e.add_field(name='Developers',
                    value='[kerbybit](https://github.com/kerbybit)\n'
                          '[FalseHonesty](https://github.com/FalseHonesty)\n'
                          '[Matt](https://github.com/mattco98)',
                    inline=True)

        e.add_field(name='What is ChatTriggers?',
                    value='ChatTriggers is a framework for Minecraft that allows for live scripting and client '
                          'modification using JavaScript. We provide libraries, wrappers, objects and more to make '
                          'your life as a modder as easy as possible. Even without the proper wrapper, you can still '
                          'use exposed Minecraft methods and variables but you will need knowledge of FML mappings',
                    inline=False)
        
        # Iterate over Cogs & Command to add to the 2nd embed
        # Built for only one Cog
        for cog, _commands in self.get_bot_mapping().items():
            _commands = await self.filter_commands(_commands)

            command_string = '```asciidoc\n'

            for _command in _commands:
                command_string += self.get_command_signature(_command) + '\n'
            
            # Remove last `\n`
            command_string = command_string[:-2]
            command_string += '```'

            if cog:
                e_command.description = command_string

        pages = menus.MenuPages(source=HelpPaginator([e, e_command]),
                                clear_reactions_after=True)
        await pages.start(self.context)
