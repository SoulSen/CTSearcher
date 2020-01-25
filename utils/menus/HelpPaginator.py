from discord.ext import menus


class HelpPaginator(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
        # Just to make Pagination for the Help command easier

        entries.set_footer(text=f'Current Page: {self.entries.index(entries) + 1}/{len(self.entries)}')

        return entries
