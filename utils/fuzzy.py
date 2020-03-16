import re
from .types import KotlinClass, KotlinMethod, MCObfuscatedField, MCObfuscatedMethod, MCObfuscatedClass


def finder(text, collection, *, key=None, lazy=True):
    suggestions = []
    text = str(text)
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)

    for item in collection:
        if isinstance(item, KotlinMethod):
            item_name = item.name

        elif isinstance(item, KotlinClass):
            item_name = item.clean_name

        elif isinstance(item, MCObfuscatedClass):
            item_name = item.name

        elif isinstance(item, (MCObfuscatedMethod, MCObfuscatedField)):
            item_name = item.deobfuscated_name

        to_search = key(item_name) if key else item_name
        r = regex.search(to_search)

        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup):
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]