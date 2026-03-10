import yaml

# yaml dumper to format specific data structures
class Dumper(yaml.SafeDumper):
    pass

#---------------#
# InlineList
#---------------#
class InlineList:
    def __init__(self, value):
        if not isinstance(value, list):
            raise TypeError(f"InlineList expected list, got {type(value)}.")
        self.value = value

# function to represent InlineList objects inline
def _f_represent_inlinelist(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', 
                                     data.value, 
                                     flow_style=True)

# register InlineList in the Dumper
_INLINE_LIST_REGISTERED = False
def _register_inlinelist():
    global _INLINE_LIST_REGISTERED
    if not _INLINE_LIST_REGISTERED:
        Dumper.add_representer(InlineList, _f_represent_inlinelist)
        _INLINE_LIST_REGISTERED = True

#---------------#
# InlineDict
#---------------#
class InlineDict:
    def __init__(self, value):
        if not isinstance(value, dict):
            raise TypeError(f"InlineDict expected dict, got {type(value)}.")
        self.value = value

# function to represent InlineDict objects inline
def _f_represent_inlinedict(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map",
                                    data.value,
                                    flow_style=True)

# register InlineDict in the Dumper
_INLINE_DICT_REGISTERED = False
def _register_inlinedict():
    global _INLINE_DICT_REGISTERED
    if not _INLINE_DICT_REGISTERED:
        Dumper.add_representer(InlineDict, _f_represent_inlinedict)
        _INLINE_DICT_REGISTERED = True 

#---------------#
# load file
#---------------#
def load_file(file):
    with open(file, "r") as f:
        data = yaml.safe_load(f)
    return data

#---------------#
# save file
#---------------#
def save_file(file, data):
    # register the InlineList class
    _register_inlinelist()
    # register the InlineDict class
    _register_inlinedict()
    with open(file, "w", encoding="utf-8") as f:
        yaml.dump(
            data, 
            f,
            Dumper=Dumper,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )