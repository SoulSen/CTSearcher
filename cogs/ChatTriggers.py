from utils.menus import ModulePaginator, HelpCommand

from discord.ext import commands, menus, tasks
import discord
import re


class ChatTriggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        bot.help_command = HelpCommand()
        bot.help_command.cog = self
        
        task = self.check_for_new_module.start()
        task.add_done_callback(self.handle_task_exceptions)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound,)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(title=f'Missing `{error.param.name}` argument',
                                                      color=discord.Color.from_rgb(123, 47, 181)))

        else:
            print(error)

    def cog_unload(self):
        self.check_for_new_module.cancel()
        
    @tasks.loop(minutes=10.0)
    async def check_for_new_module(self):
        try:
            async with self.bot.session.get('https://chattriggers.com/api/modules',
                                            params={'sort': 'DATE_CREATED_DESC'}) as response:
                module = await response.json()

            module = module['modules'][0]

            # Check if `_latest_module` exists and if it's the same module
            if self.bot._latest_module and module == self.bot._latest_module:
                return

            # Prevent sending first module because it's probably not latest
            elif not self.bot._latest_module:
                self.bot._latest_module = module
                return

            # A new module was posted
            # Build from `ModulePaginator`
            e = ModulePaginator.build_embed(module, True)
            
            await self.bot.MODULE_CHANNEL.send(embed=e)
        except Exception as e:
            print(e.with_traceback(e.__traceback__))

    def handle_task_exceptions(self, task):
        if task.exception():
            task.print_stack()

    @commands.command(aliases=['rtfm', 'rtfd', 'docs', 'search'],
                      brief='Searches for an object from the JavaDocs',
                      help='Searches through the available objects from ChatTriggers '
                           'and returns links to the JavaDocs')
    async def javadocs(self, ctx, query: str = None):
        e = discord.Embed(colour=discord.Color.blurple())
        e.set_author(name=f'Query made by: {ctx.author}',
                     icon_url=ctx.author.avatar_url)

        if not query:
            e.description = '[JavaDocs](https://www.chattriggers.com/javadocs/)'
            return await ctx.send(embed=e)

        e.title = f'Results for: {query}'
        query = query.lower()
        description = ''
        results = 0

        for _class, _functions in self.bot._cache.items():
            # Check to prevent over 5 results
            if results > 5:
                break

            # Takes out the package class
            _class_name = re.split(r'.*/', _class)[1].replace('.kt', '')

            # Class result found
            if query in _class_name.lower():
                results += 1

                url = 'https://www.chattriggers.com/javadocs/' + _class.replace('.kt', '.html')
                description += f'[`{_class_name}`]({url})\n'

            for _function in _functions:
                # Checks don't occur in the outer for-loop so we have to check in here too
                if results > 5:
                    break

                # Function result found
                if query in _function.lower():
                    results += 1

                    url = 'https://www.chattriggers.com/javadocs/' + _class.replace('.kt', '.html') + \
                          f'#{_function}'
                    _ = f'{_class_name}.{_function}()'

                    description += f'[`{_}`]({url})\n'

        if results == 0:
            e.description = 'No Results!'
            await ctx.send(embed=e)

        else:
            e.description = description
            await ctx.send(embed=e)

    @commands.command(brief='Search for modules',
                      help='Search for modules posted from the ChatTriggers API')
    async def module(self, ctx, query: str):
        async with self.bot.session.get('https://chattriggers.com/api/modules',
                                        params={'q': query}) as response:
            info = await response.json()

        pages = menus.MenuPages(source=ModulePaginator(info['modules']),
                                clear_reactions_after=True,
                                delete_message_after=True)
        await pages.start(ctx)

    @commands.command(brief='Get the source code of ChatTriggers',
                      help='Get the source code of ChatTriggers')
    async def source(self, ctx):
        e = discord.Embed(title='Source Code',
                          description='[ct.js Repository](https://github.com/ChatTriggers/ct.js)\n'
                                      '[Rhino Repository](https://github.com/ChatTriggers/rhino)\n'
                                      '[Backend Repository](https://github.com/ChatTriggers/website-backend)\n'
                                      '[Frontend Repository](https://github.com/ChatTriggers/website-frontend)\n'
                                      '[Bot Repository](https://github.com/SoulSen/CTSearcher)',
                          color=discord.Color.from_rgb(123, 47, 181))

        '''
        if repo == 'main':
            e.title = 'ct.js Repository'
            e.url = 'https://github.com/ChatTriggers/ct.js'
        elif repo.lower() == 'rhino':
            e.title = 'ct.js Rhino Repository'
            e.url = 'https://github.com/ChatTriggers/rhino'
        elif repo.lower() == 'backend':
            e.title = 'Website Backend Repository'
            e.url = 'https://github.com/ChatTriggers/website-backend'
        elif repo.lower() == 'frontend':
            e.title = 'Website Frontend Repository'
            e.url = 'https://github.com/ChatTriggers/website-frontend'
        elif repo.lower() == 'mamba':
            e.title = 'ct.js Mamba Repository'
            e.url = 'https://github.com/ChatTriggers/Mamba'
        elif repo.lower() == 'bot':
            e.title = 'ChatTriggers Bot Repository'
            e.url = 'https://github.com/SoulSen/CTSearcher'
        else:
            e.title = 'ChatTriggers User'
            e.url = 'https://github.com/ChatTriggers'
        '''

        await ctx.send(embed=e)

    @commands.command(brief='Get the patreon link for ChatTriggers',
                      help='Gives the user a patreon link to help benefit ChatTriggers')
    async def patreon(self, ctx):
        e = discord.Embed(title='Patreon', url='https://www.patreon.com/ChatTriggers',
                          description='Thanks for being interested in becoming a Patreon! '
                                      'It really means a lot, it helps us keep the website running.'
                                      ' To learn more about the cool perks click the link above.',
                          color=discord.Color.from_rgb(123, 47, 181))

        await ctx.send(embed=e)

    @commands.command(brief='A migrating guide to the next major version',
                      help='Help migrate to 1.0.0 and learn about its new features')
    async def migrating(self, ctx):
        e = discord.Embed(title='Migrating', url='https://github.com/ChatTriggers/ct.js/blob/master/MIGRATION.md',
                          description='Lots of changes are coming, ' 
                                      'so be sure to be prepared check out the migrating guide to be ready for 1.0.0!',
                          color=discord.Color.from_rgb(123, 47, 181))

        await ctx.send(embed=e)

    @commands.command()
    async def crank(self, ctx):
        e = discord.Embed(title='CustomRank', url='https://www.chattriggers.com/modules/v/CustomRank',
                          description='1. Are you using Labymod or Frames+? If so, they are not supported currently.\n'
                                      '2. Are you using a supported ChatTriggers version? '
                                      'Versions allowed are `0.18.4` & `1.0.0`.\n'
                                      '3. Are you on Minecraft Version `1.8.9`?\n'
                                      '4. Did you use `/ct import CustomRank` **EXACTLY**\n'
                                      '5. Did you use `/crank` after importing CustomRank?\n',
                          color=discord.Color.from_rgb(123, 47, 181))

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(ChatTriggers(bot))
