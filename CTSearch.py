from discord.ext import commands
import aiohttp
import discord

import collections
import base64
import re
import os


class CTSearch(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cache = collections.defaultdict(list)
        self.session = None
        self.counter = 0

        self._latest_module = None

        self._username = os.environ['USERNAME']
        self._password = os.environ['PASSWORD']

        self.BASE = 'https://api.github.com/repos/ChatTriggers/ct.js/contents'
        self.MODULE_CHANNEL = None
        
        # This was found in the `build.gradle` of the repository
        self.IGNORED = ['com/chattriggers/ctjs/engine/langs', 'com/chattriggers/ctjs/engine/loader',
                        'com/chattriggers/ctjs/engine/module', 'com/chattriggers/ctjs/utils',
                        'com/chattriggers/ctjs/listeners', 'com/chattriggers/ctjs/minecraft/imixins',
                        'com/chattriggers/ctjs/loader', 'com/chattriggers/ctjs/launch',
                        'com/chattriggers/ctjs/commands', 'com/chattriggers/ctjs/minecraft/wrappers/objects/threading',
                        'com/chattriggers/ctjs/minecraft/mixins']

    async def on_ready(self):
        self.session = aiohttp.ClientSession()

        await self.change_presence(activity=discord.Activity(name="Reading JavaDocs | //help",
                                                             type=discord.ActivityType.playing))
        await self._prepare_cache()
        self.MODULE_CHANNEL = self.get_channel(366740283943157760)
        
        self.load_extension('cogs.ChatTriggers')

        print('READY')
    
    async def on_message(self, message):
        if message.channel.id == 119493402902528000 and message.content == 'bot':
            await message.channel.send('land')
            
        await bot.process_commands(message)

    async def _prepare_cache(self):
        # We get the initial contents of the root folder
        async with self.session.get(f'{self.BASE}/src/main/kotlin/com/chattriggers/ctjs',
                                    auth=aiohttp.BasicAuth(self._username,
                                                           self._password)
                                    ) as response:
            self._cache = await self._create_cache((await response.json()))

    async def _create_cache(self, initial, classes=None):
        if classes is None:
            # This is recycled because it's used to keep track of all the classes
            classes = collections.defaultdict(list)

        for file_or_dir in initial:
            # Check if item is a file which should be a Kotlin class
            # where we add it to cache, but we also check for all the
            # public functions that can be access by the JS API
            # in order for better RTFM searches
            if file_or_dir['type'] == 'file':
                file = file_or_dir['path'].replace('src/main/kotlin/', '')

                # We get the contents of the Kotlin file and extract the public functions
                # with REGEX
                async with await self.session.get(f'{file_or_dir["url"]}',
                                                  auth=aiohttp.BasicAuth(self._username,
                                                                         self._password)
                                                  ) as response:
                    content = base64.b64decode(
                        (await response.json())['content']
                    ).decode('utf-8')

                # REGEX: (.*)fun\s(.*?\)) TO INCLUDE PARAMETERS, THIS DOES NOT CAPTURE EACH INDIVIDUAL PARAM!
                matches = re.findall(r'(.*)fun\s(.*?)\(', content)

                for func_type, func_name in matches:
                    if 'private' or 'internal' not in func_type.lower():
                        classes[file].append(func_name)

                self.counter += 1

                # This print is needed in order to identify if something is stuck
                print(f'Retrieved {self.counter}')

            # Check if item is directory, if so call method again in order to iterate
            # the directory and extract its files
            elif file_or_dir['type'] == 'dir':
                if not any(pkg in file_or_dir['path'] for pkg in self.IGNORED):
                    async with await self.session.get(f'{self.BASE}/{file_or_dir["path"]}',
                                                      auth=aiohttp.BasicAuth(self._username,
                                                                             self._password)
                                                      ) as response:
                        await self._create_cache((await response.json()), classes)

        return classes


CTSearch(command_prefix="//").run(os.environ['TOKEN'])
