from discord.ext import menus
import discord


class ModulePaginator(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
        # Organizes each module into an embed

        e = discord.Embed(title=f'Module: {entries["name"]}',
                          description=f'Owner: {entries["owner"]["name"]}',
                          url=f'https://www.chattriggers.com/modules/v/{entries["name"]}',
                          color=discord.Color.from_rgb(123, 47, 181))

        e.set_image(url=entries['image'])

        if len(entries['description']) > 1024:
            entries['description'] = entries['description'][:1024]

        e.add_field(name='Description',
                    value=entries['description'])
        e.add_field(name='Downloads',
                    value=f'{entries["downloads"]}')

        release_text = ''

        for release in entries['releases']:
            release_text += f'v{release["releaseVersion"]} for CT v{release["modVersion"]}'

        e.add_field(name='Releases',
                    value=release_text,
                    inline=False)
        e.set_footer(text=", ".join(entries["tags"]))

        return e
