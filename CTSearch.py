from discord.ext import commands
import aiohttp
import discord
import os


class CTSearch(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cache = []
        self.session = None

        self._username = os.environ['USERNAME']
        self._password = os.environ['PASSWORD']

        self.BASE = 'https://api.github.com/repos/ChatTriggers/ct.js/contents/'
        self.IGNORED = ['com/chattriggers/ctjs/engine/langs', 'com/chattriggers/ctjs/engine/loader', 
                        'com/chattriggers/ctjs/engine/module', 'com/chattriggers/ctjs/utils',
                        'com/chattriggers/ctjs/listeners', 'com/chattriggers/ctjs/minecraft/imixins',
                        'com/chattriggers/ctjs/loader', 'com/chattriggers/ctjs/launch',
                        'com/chattriggers/ctjs/commands', 'com/chattriggers/ctjs/minecraft/wrappers/objects/threading',
                        'com/chattriggers/ctjs/minecraft/mixins']

    async def on_ready(self):
        self.session = aiohttp.ClientSession()
        await self.change_presence(status=discord.Game("Reading Documentation | *help"))
        await self._prepare_cache()

        print('READY')

    async def _prepare_cache(self):
        async with self.session.get('https://api.github.com/repos/ChatTriggers/ct.js/contents/src/main/kotlin/com'
                                    '/chattriggers/ctjs',
                                    auth=aiohttp.BasicAuth(self._username,
                                                           self._password)
                                    ) as response:
            self._cache = await self._create_cache((await response.json()))

    async def _create_cache(self, initial, classes=None):
        if classes is None:
            classes = []

        for file_or_dir in initial:
            if file_or_dir['type'] == 'file':
                file = file_or_dir['path'].replace('src/main/kotlin/', '')
                classes.append(file)

            elif file_or_dir['type'] == 'dir':
                if not any(pkg in file_or_dir['path'] for pkg in self.IGNORED):
                    async with await self.session.get(self.BASE + '/' + file_or_dir['path'], 
                                                      auth=aiohttp.BasicAuth(self._username,
                                                                             self._password)
                                                      ) as response:
                        await self._create_cache((await response.json()), classes)

        return classes


bot = CTSearch(command_prefix="*")


@bot.command(aliases=['rtfm', 'rtfd', 'docs', 'search'],
             brief="Searches for an object from the JavaDocs",
             help="Searches through the available objects from ChatTriggers "
                  "and returns links to the JavaDocs")
async def javadocs(ctx, query: str = None):
    e = discord.Embed(colour=discord.Colour.blurple())
    e.set_author(name=f'Query made by: {ctx.author}', icon_url=ctx.author.avatar_url)

    if not query:
        e.description = '[JavaDocs](https://www.chattriggers.com/javadocs/)'
        return await ctx.send(embed=e)
    
    e.title = f'Results for: {query}'
    results = 0
    description = ''

    for _class in bot._cache:
        if results > 5:
            break

        else:
            if query in _class:
                results += 1

                url = 'https://www.chattriggers.com/javadocs/' + _class.replace('.kt', '.html')
                description += f'[`{_class}`]({url})\n'

    if results == 0:
        e.description = 'No Results!'
        await ctx.send(embed=e)
    else:
        e.description = description
        await ctx.send(embed=e)


bot.run(os.environ['TOKEN'])
