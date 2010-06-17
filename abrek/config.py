import os

class AbrekConfig(object):
    def __init__(self):
        home = os.environ.get('HOME', '/')
        baseconfig = os.environ.get('XDG_CONFIG_HOME',
                     os.path.join(home, '.config'))
        basedata = os.environ.get('XDG_DATA_HOME',
                     os.path.join(home, '.local', 'share'))
        basecache = os.environ.get('XDG_CACHE_HOME',
                     os.path.join(home, '.cache'))
        self.configdir = os.path.join(baseconfig, 'abrek')
        self.installdir = os.path.join(basedata, 'abrek', 'installed-tests')
        self.downloaddir = os.path.join(basecache, 'abrek', 'download')
        self.resultsdir = os.path.join(basedata, 'abrek', 'results')

