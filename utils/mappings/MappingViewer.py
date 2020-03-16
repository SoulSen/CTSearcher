from ..types import MCObfuscatedClass, MCObfuscatedMethod, MCObfuscatedField
import pandas as pd
import re


class MappingViewer:
    def __init__(self):
        self.mappings = []

    async def setup_mappings(self, file, mapping_type: str):
        # mapping_reader = csv.reader(mapping)
        mapping_reader = pd.read_csv(file, error_bad_lines=False)

        # Obfuscated Name, Debobfuscated Name, Class
        for row in mapping_reader.itertuples():
            package = re.split(r'(.*/)', row.mc_class)

            if any((mc_class := obf_class).name == package[2] for obf_class in self.mappings):
                mc_class = mc_class
            else:
                mc_class = MCObfuscatedClass(package[1], package[2])
                self.mappings.append(mc_class)

            if mapping_type == 'methods':
                mc_class.add_method(MCObfuscatedMethod(mc_class, row.obfuscated, row.deobfuscated))

            elif mapping_type == 'fields':
                mc_class.add_field(MCObfuscatedField(mc_class, row.obfuscated, row.deobfuscated))
