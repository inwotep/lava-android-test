import os

class AbrekConfig(object):
    def __init__(self):
        home = os.environ.get('HOME', '/')
        baseconfig = os.environ.get('XDG_CONFIG_HOME',
                     os.path.join(home, '.config'))
        basedata = os.environ.get('XDG_DATA_HOME',
                     os.path.join(home, '.local', 'share'))
        self.configdir = os.path.join(baseconfig, 'abrek')
        self.installdir = os.path.join(basedata, 'abrek', 'installed-tests')
        self.resultsdir = os.path.join(basedata, 'abrek', 'results')

_config = None

def get_config():
    global _config
    if _config is not None:
        return _config
    return AbrekConfig()

def set_config(config):
    global _config
    _config = config

