
#for the entry point to locate natlink.grammars folders

def where_are_my_grammars() -> str:
    """returns the folder where there are at least 0 natlink grammars to load.  
    see pyprojct.toml for the entry point"""
    return __path__[0]

