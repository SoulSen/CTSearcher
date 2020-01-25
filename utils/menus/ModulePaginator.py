from discord.ext import menus
import discord
import re


class ModulePaginator(menus.ListPageSource):
    def __init__(self, data, new_module: bool = False):
        self.new_module = new_module

        super().__init__(data, per_page=1)

    @staticmethod
    def build_embed(data, new_module: bool = False):
        # Easy building embeds everywhere
        e = discord.Embed(title=f'{"New Module Posted" if new_module else "Module"}: {data["name"]}',
                          url=f'https://www.chattriggers.com/modules/v/{data["name"]}',
                          color=discord.Color.from_rgb(123, 47, 181))

        e.set_image(url='' if not data['image'] else data['image'])

        e.add_field(name='Owner',
                    value=data['owner']['name'])

        release_text = ''

        for release in data['releases']:
            version_link = 'https://github.com/ChatTriggers/ct.js/releases'

            if release['modVersion'] == '1.0.0':
                version_link = 'https://github.com/ChatTriggers/ct.js/releases/download/1.0.0RC4/' \
                               'ctjs-1.0.0-RC4-1.8.9.jar'
            elif release['modVersion'] == '0.18.4':
                version_link = 'https://github.com/ChatTriggers/ct.js/releases/download/0.18.4/' \
                               'ctjs-0.18.4-SNAPSHOT-1.8.9.jar'
            elif release['modVersion'] == '0.16.6':
                version_link = 'https://github.com/ChatTriggers/ct.js/releases/download/0.16.6/' \
                               'ctjs-0.16.6-SNAPSHOT-1.8.9.jar'

            release_text += f'[v{release["releaseVersion"]}]' \
                            f'(https://chattriggers.com/api/modules/{data["id"]}/releases/' \
                            f'{release["id"]}?files=scripts) ' \
                            f'for CT [v{release["modVersion"]}]' \
                            f'({version_link})\n'

        e.add_field(name='Releases',
                    value='No releases' if not release_text else release_text,
                    inline=True)

        e.add_field(name='Downloads',
                    value=f'{data["downloads"]}',
                    inline=True)

        if len(data['description']) > 1024:
            data['description'] = data['description'][:950] + f'\n[**...**]' \
                                                              f'(https://www.chattriggers.com/modules/v/{data["name"]})'

        sanitize = re.sub(r"\|\|([\S\s]*)\|\|", '\\1', data['description'])

        e.add_field(name='Description',
                    value=sanitize)

        if not data['tags']:
            data['tags'].append('None')

        e.set_footer(text=', '.join(data['tags']))

        return e

    async def format_page(self, menu, entries):
        # Organizes each module into an embed

        e = self.build_embed(entries, self.new_module)
        e.set_footer(text=e._footer['text'] + f' | Current Page {self.entries.index(entries) + 1}/{len(self.entries)}')

        return e
