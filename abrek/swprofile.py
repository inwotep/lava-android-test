import apt
import lsb_release

def get_packages(apt_cache=None):
    """ Get information about the packages installed

    apt_cache - if not provided, this will be read from the system
    """
    if apt_cache == None:
        apt_cache = apt.Cache()
    packages = []
    for apt_pkg in apt_cache:
        if hasattr(apt_pkg, 'is_installed'):
            is_installed = apt_pkg.is_installed
        else:
            is_installed = apt_pkg.isInstalled # old style API
        if is_installed:
            pkg = {"name":apt_pkg.name, "version":apt_pkg.installed.version}
            packages.append(pkg)
    return packages

def get_sw_context(test_id, time_check=False, apt_cache=None,
                  lsb_information=None):
    """ Return dict used for storing sw_context information

    test_id - Unique identifier for this test
    time_check - whether or not a check was performed to see if
            the time on the system was synced with a time server
    apt_cache - if not provided, this will be read from the system
    lsb_information - if not provided, this will be read from the system
    """
    sw_context = {}
    sw_context['sw_image'] = get_sw_image(lsb_information)
    sw_context['packages'] = get_packages(apt_cache)
    sw_context['time_check_performed'] = time_check
    sw_context['test_id'] = test_id
    return sw_context

def get_sw_image(lsb_information=None):
    """ Get information about the image we are running

    For now, this just uses the description from lsb-release.  This will
    be extended to provide more detailed information about the image if
    it becomes available

    lsb_information - if not provided, this will be read from the system
    """
    if lsb_information == None:
        lsb_information = lsb_release.get_lsb_information()
    desc = lsb_information['DESCRIPTION']
    return {"desc":desc}
