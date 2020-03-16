import re


class KotlinMethod:
    def __init__(self, kotlin_class, name: str, parameters: str, cleaned_parameters: str):
        self.name = name
        self.kotlin_class = kotlin_class

        self.parameters = parameters
        self.cleaned_parameters = cleaned_parameters

        self.url = f'https://www.chattriggers.com/javadocs/' \
                   f'{self.kotlin_class.name.replace(".kt", ".html")}#{self.name}-'

        for params in self.cleaned_parameters.split(','):
            param_name = params.replace(' ', '').split(':')[0]
            self.url += f'{param_name}-'


class KotlinClass:
    def __init__(self, full_name: str):
        self.name = re.split(r'.*/', full_name)[1]

        self.clean_name = self.name.replace('.kt', '')
        self.package = re.split(r'.*/', full_name)[0]
        self.name_with_package = full_name

        self.url = f'https://www.chattriggers.com/javadocs/' \
                   f'{self.package}{self.name.replace("kt", "html")}'

        self.methods = []

    def add_method(self, method: KotlinMethod):
        method.kotlin_class = self
        self.methods.append(method)

