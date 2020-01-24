from utils.menus import ModulePaginator, HelpCommand

from discord.ext import commands, menus, tasks
import discord
import re


class ChatTriggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        bot.help_command = HelpCommand()
        bot.help_command.cog = self
        
        # self.check_for_new_module.start()
        
    def cog_unload(self):
        self.check_for_new_module.cancel()
        
    @tasks.loop(minutes=15.0)
    async def check_for_new_module(self):
        async with self.bot.session.get('https://chattriggers.com/api/modules',
                                        params={'sort': 'DATE_CREATED_DESC'}) as response:
            module = await response.json()

        module = module['modules'][0]

        # Check if `_latest_module` exists if not set it, but don't send it
        if not self.bot._latest_module:
            self.bot._latest_module = module
            return 

        # If latest module is the same return
        if module == self.bot._latest_module:
            return 

        # A new module was posted
        # This embed was taken from `ModulePaginator`

        e = discord.Embed(title=f'New Module Posted: {module["name"]}',
                          description=f'Owner: {module["owner"]["name"]}',
                          url=f'https://www.chattriggers.com/modules/v/{module["name"]}',
                          color=discord.Color.from_rgb(123, 47, 181))

        e.set_image(url=module['image'])

        if len(module['description']) > 1024:
            module['description'] = module['description'][:1024]

        e.add_field(name='Description',
                    value=module['description'])
        e.add_field(name='Downloads',
                    value=f'{module["downloads"]}')

        release_text = ''

        for release in module['releases']:
            release_text += f'v{release["releaseVersion"]} for CT v{release["modVersion"]}'

        e.add_field(name='Releases',
                    value=release_text,
                    inline=False)
        e.set_footer(text=", ".join(module["tags"]))

        await self.bot.MODULE_CHANNEL.send(embed=e)

    @commands.command(aliases=['rtfm', 'rtfd', 'docs', 'search'],
                      brief="Searches for an object from the JavaDocs",
                      help="Searches through the available objects from ChatTriggers "
                           "and returns links to the JavaDocs")
    async def javadocs(self, ctx, query: str = None):
        e = discord.Embed(colour=discord.Color.blurple())
        e.set_author(name=f'Query made by: {ctx.author}',
                     icon_url=ctx.author.avatar_url)

        if not query:
            e.description = '[JavaDocs](https://www.chattriggers.com/javadocs/)'
            return await ctx.send(embed=e)

        e.title = f'Results for: {query}'
        results = 0
        description = ''
        query = query.lower()

        for _class, _functions in self.bot._cache.items():
            # Check to prevent over 5 results
            if results > 5:
                break

            # Takes out the package class
            _class_name = re.split(r'.*/', _class)[1].replace('.kt',
                                                              '')

            # Class result found
            if query in _class_name.lower():
                results += 1

                url = 'https://www.chattriggers.com/javadocs/' + _class.replace('.kt',
                                                                                '.html')
                description += f'[`{_class_name}`]({url})\n'

            for _function in _functions:
                # Checks don't occur in the outer for-loop so we have to check in here too
                if results > 5:
                    break

                # Function result found
                if query in _function.lower():
                    results += 1

                    url = 'https://www.chattriggers.com/javadocs/' + _class.replace('.kt',
                                                                                    '.html') + \
                          f'#{_function}'
                    _ = f'{_class_name}.{_function}()'

                    description += f'[`{_}`]({url})\n'

        if results == 0:
            e.description = 'No Results!'
            await ctx.send(embed=e)

        else:
            e.description = description
            await ctx.send(embed=e)

    @commands.command()
    async def module(self, ctx, query: str):
        async with self.bot.session.get('https://chattriggers.com/api/modules',
                                        params={'q': query}) as response:
            info = await response.json()

        pages = menus.MenuPages(source=ModulePaginator(info['modules']),
                                clear_reactions_after=True)
        await pages.start(ctx)

    @commands.command()
    async def source(self, ctx, repo: str = ''):
        e = discord.Embed(color=discord.Color.from_rgb(123, 47, 181))

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

        await ctx.send(embed=e)

    @commands.command()
    async def patreon(self, ctx):
        e = discord.Embed(title='Patreon', url='https://www.patreon.com/ChatTriggers',
                          description='Thanks for being interested in becoming a Patreon! '
                                      'It really means a lot, it helps us keep the website running.'
                                      ' To learn more about the cool perks click the link above.',
                          color=discord.Color.from_rgb(123, 47, 181))

        await ctx.send(embed=e)

    @commands.command()
    async def migrating(self, ctx):
        e = discord.Embed(title='Migrating', url='https://github.com/ChatTriggers/ct.js/blob/master/MIGRATION.md',
                          description='Lots of changes are coming, ' 
                                      'so be sure to be prepared check out the migrating guide to be ready for 1.0.0!',
                          color=discord.Color.from_rgb(123, 47, 181))

        await ctx.send(embed=e)

    @commands.command()
    async def crank(self, ctx):
        e = discord.Embed(title='CustomRank', url='https://www.chattriggers.com/modules/v/CustomRank',
                          description="1. Are you using Labymod? If so, it's not supported.\n"
                                      "2. Are you using a supported ChatTriggers version? "
                                      "Versions allowed are `0.18.4` & `1.0.0`.\n"
                                      "3. Are you on Minecraft Version `1.8.9`?"
                                      '4. Did you use `/ct import CustomRank` **EXACTLY**\n'
                                      '5. Did you use `/crank` after importing CustomRank?\n',
                          color=discord.Color.from_rgb(123, 47, 181))

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(ChatTriggers(bot))
