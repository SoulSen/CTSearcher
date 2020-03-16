class MCObfuscatedClass:
    def __init__(self, package, name):
        self.package = package
        self.name = name

        self.methods = []
        self.fields = []

    def add_method(self, method):
        self.methods.append(method)

    def add_field(self, field):
        self.fields.append(field)


class MCObfuscatedMethod:
    def __init__(self, mc_class, obfuscated_name, deobfucasted_name):
        self.mc_class = mc_class

        self.obfuscated_name = obfuscated_name
        self.deobfuscated_name = deobfucasted_name


class MCObfuscatedField:
    def __init__(self, mc_class, obfuscated_name, deobfucasted_name):
        self.mc_class = mc_class

        self.obfuscated_name = obfuscated_name
        self.deobfuscated_name = deobfucasted_name
