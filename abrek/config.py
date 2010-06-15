import os

def config_dir():
    basedir = os.path.expanduser("~")
    configdir = os.path.join(basedir, '.abrek')
    if not os.path.exists(configdir):
        os.makedirs(configdir)
    return configdir

def config_installed_dir():
    installdir = os.path.join(config_dir(), 'installed-tests')
    if not os.path.exists(installdir):
        os.makedirs(installdir)
    return installdir

def config_download_dir():
    downloaddir = os.path.join(config_dir(), 'download')
    if not os.path.exists(downloaddir):
        os.makedirs(downloaddir)
    return downloaddir

def config_results_dir():
    resultsdir = os.path.join(config_dir(), 'results')
    if not os.path.exists(resultsdir):
        os.makedirs(resultsdir)
    return resultsdir
