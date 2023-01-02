def to_snake_case(name):
    import re
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()

def to_camel_case(name, capitalize_first=False):
    import re
    name = re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), name)
    if name.endswith("_"):
        name = name[:-1]
    if capitalize_first:
        name = name[0].upper() + name[1:]
    else:
        name = name[0].lower() + name[1:]
    return name
