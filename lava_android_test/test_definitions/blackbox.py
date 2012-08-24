# Copyright (c) 2012 Linaro Limited 

# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Android Test.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Bridge for the black-box testing implemented by android-lava-wrapper.

See: https://github.com/zyga/android-lava-wrapper
"""

import functools
import logging
import os
import pdb
import subprocess
import tempfile

from linaro_dashboard_bundle.evolution import DocumentEvolution
from linaro_dashboard_bundle.io import DocumentIO

from lava_android_test.config import get_config


def warnoncall(func):
    @functools.wraps(func)
    def waroncall_decorator(*args, **kwargs):
        parts = []
        parts.append(func.__name__)
        parts.append('(')
        parts.append(", ".join([
            repr(arg) for arg in args]))
        parts.append(", ".join([
            "%s=%r" % (name, value) for name, value in kwargs.iteritems()]))
        parts.append(")")
        logging.warning("function called: %s", ''.join(parts))
        return func(*args, **kwargs)
    return waroncall_decorator


def debuggable_real(func):
    """
    Helper for debugging functions that otherwise have their exceptions
    consumed by the caller. Any exception raised from such a function will
    trigger a pdb session when 'DEBUG_DEBUGGABLE' environment is set.
    """
    @functools.wraps(func)
    def debuggable_decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logging.exception("exception in @debuggable function")
            pdb.post_mortem()
    return debuggable_decorator


def debuggable_noop(func):
    return func


if os.getenv("DEBUG_DEBUGGABLE"):
    debuggable = debuggable_real
else:
    debuggable = debuggable_noop


class SuperAdb(object):
    """
    Class that implements certain parts of ADB()-like API differently.
    """

    def __init__(self, stock_adb):
        # Name of the adb executable with any required arguments,
        # such as -s 'serial'
        self._adb_cmd = stock_adb.adb.split()

    def __call__(self, command, *args, **kwargs):
        """
        Invoke adb command.

        This call is somewhat special that it wraps two subprocess helper
        functions: check_call and check_output. They are called depending
        on the keyword argument 'stdout', if passed as None then output
        is _not_ saved and is instantly streamed to the stdout of the running
        program. In any other case stdout is buffered and saved, then returned
        """
        cmd = self._adb_cmd + command
        if "stdout" in kwargs and kwargs['stdout'] is None:
            del kwargs['stdout']
            return subprocess.check_call(cmd, *args, **kwargs)
        else:
            return subprocess.check_output(cmd, *args, **kwargs)

    def listdir(self, dirname):
        """
        List directory entries on the android device.

        Similar to adb.listdir() as implemented in ADB() but generates
        subsequent lines instead of returning a big lump of text for the
        developer to parse. Also, instead of using 'ls' on the target it
        uses the special 'ls' command built into adb.
        """
        for line in self(['ls', dirname]).splitlines():
            # a, b and c are various pieces of stat data
            # but we don't need that here.
            a, b, c, pathname = line.split(' ', 3)
            yield pathname


class AdbMixIn(object):
    """
    Mix-in class that assists in setting up ADB.

    lava-android-test uses the setadb()/getadb() methods to pass the ADB object
    (which encapsulates connection data for the specific device we will be
    talking to).

    Since the ADB object has fixed API and changes there are beyond the scope
    of this test any extra stuff we want from ADB will be provided by the
    SuperAdb class.

    This mix-in class that has methods expected by lava-android-test and
    exposes two properties, adb and super_adb.
    """

    adb = None

    @warnoncall
    def setadb(self, adb=None):
        if self.adb is None and adb is not None:
            self.adb = adb
        else:
            self.adb = adb
        self.super_adb = SuperAdb(adb)

    @warnoncall
    def getadb(self):
        return self.adb


class Sponge(object):
    """
    A simple namespace-like object that anyone can assign and read freely.

    To get some understanding of what is going on both reads and writes are
    logged.
    """

    @warnoncall
    def __getattr__(self, attr):
        return super(Sponge, self).__getattr__(attr)

    @warnoncall
    def __setattr__(self, attr, value):
        super(Sponge, self).__setattr__(attr, value)


class FutureFormatDetected(Exception):
    """
    Exception raised when the code detects a new, unsupported
    format that was created after this library was written.

    Since formats do not have partial ordering we can only detect
    a future format when the document format is already at the "latest"
    value, as determined by DocumentEvolution.is_latest(), but the actual
    format is not known to us.

    Typically this won't happen often as document upgrades are not performed
    unless necessary. The only case when this may happen is where the bundle
    loaded from the device was already using a future format to begin with.
    """

    def __init__(self, format):
        self.format = format

    def __str__(self):
        "Unsupported, future format: %s" % self.format

    def __repr__(self):
        return "FutureFormatDetected(%r)" % self.format


class BlackBoxTestBridge(AdbMixIn):
    """
    Bridge for interacting with black box tests implemented as something that
    looks like android test definition.
    """

    # NOTE: none of the tests will actually carry this ID, it is simply used
    # here so that it's not a magic value.
    testname = 'blackbox'

    def __init__(self):
        """
        Initialize black-box test bridge
        """
        # The sponge object is just a requirement from the API, it is not
        # actually used by us in any way. The framework assigns a skeleton
        # test result there but we don't really need it. The Sponge object
        # is a simple 'bag' or namespace that will happily accept and record
        # any values.
        self.parser = Sponge()

    @warnoncall
    def install(self, install_options=None):
        """
        Black box tests cannot be installed  they must be pre-baked into the
        image. To conform to the 'protocol' used by lava-android-test we will
        perform a fake 'installation' of the black box tests by creating a
        directory that lava-android-test is checking for. We do that only if
        the lava-wrapper executable, which is the entry point to black box
        tests exists in the image.
        """
        if not self.adb.exists(self._blackbox_pathname):
            # Sadly lava-android-test has no exception hierarchy that we can
            # use so all problems are reported as RuntimeError
            raise RuntimeError(
                'blackbox test cannot be "installed" as they must be built'
                ' into the image.'
                ' See https://github.com/zyga/android-lava-wrapper'
                ' for details.')
        else:
            self.adb.makedirs(self._fake_install_path)

    @warnoncall
    def uninstall(self):
        """
        Conformance method to keep up with the API required by
        lava-android-test. It un-does what install() did by removing the
        _fake_install_path directory from the device.
        """
        if self.adb.exists(self._fake_install_path):
            self.adb.rmtree(self._fake_install_path)

    @debuggable
    @warnoncall
    def run(self, quiet=False, run_options=None):
        """
        Use ADB to run the black-box executable on the device
        Wait for all the tests to finish then collect the results
        """
        # Spool dir, technically this is the same as used by the black box
        # executable but it can change in the future so we just pass whatever
        # we want, to know where to find the results later.
        spool_dir = '/sdcard/LAVA'
        stuff_before = frozenset(self.super_adb.listdir(spool_dir))
        blackbox_command = [
            'shell', self._blackbox_pathname,
            '--spool', spool_dir,
            '--run-all-tests']
        # Let's run the blackbox executable via ADB
        self.super_adb(blackbox_command, stdout=None)
        stuff_after = frozenset(self.super_adb.listdir(spool_dir))
        # Check what got added to the spool directory
        new_entries = stuff_after - stuff_before
        if len(new_entries) == 0:
            raise RuntimeError("Nothing got added to the spool directory")
        elif len(new_entries) > 1:
            raise RuntimeError("Multiple items added to the spool directory")
        new_dir = list(new_entries)[0]
        # Do all the heavy lifting to collect and combine all the bundles
        # together. TODO: perhaps save all the bundles (as they are)
        # and actually combine them later in parse()
        remote_bundle_dir = os.path.join(spool_dir, new_dir)
        bundle = self._collect_and_combine_bundles(remote_bundle_dir)
        # XXX: temporary hack
        with open('blackbox.json', 'wt') as stream:
            DocumentIO.dump(stream, bundle)

    def _collect_and_combine_bundles(self, remote_bundle_dir):
        """
        Collect bundles from the specified folder on the device.
        This is somewhat tricky. Each bundle we coalesce may be generated by
        a different, separate programs and may, thus, use different formats.

        To combine them all correctly we need to take two precautions:
        1) All bundles must be updated to a single, common format
        2) No bundle may be upgraded beyond the latest format known
           to this code. Since the hypothetical 2.0 format may be widely
           different that we cannot reliably interpret anything beyond
           the format field. To prevent this we use the evolution API
           to carefully upgrade only to the "sentinel" format, 1.3
           (at this time)
        """
        # Use DocumentIO.loads() to preserve the order of entries.
        # This is a very small touch but it makes reading the results
        # far more pleasant.
        aggregated_bundle = DocumentIO.loads(
            '{\n'
            '"format": "' + self._desired_format + '",\n'
            '"test_runs": []\n'
            '}\n')[1]
        temp_dir = tempfile.mkdtemp()
        try:
            for name in self.super_adb.listdir(remote_bundle_dir):
                # XXX: Simple filtering for '.json' files, prevents
                # spurious errors if the result directory has additional
                # files of any kind.
                if not name.endswith('.json'):
                    continue
                remote_pathname = os.path.join(remote_bundle_dir, name)
                local_pathname = os.path.join(temp_dir, name)
                try:
                    # Copy across adb...
                    self.adb.pull(remote_pathname, local_pathname)
                    # ...then deserialize, convert and combine the bundle
                    format, bundle = self._load_bundle(local_pathname)
                    self._convert_to_common_format(format, bundle)
                    self._combine_with_aggregated(aggregated_bundle, bundle)
                except:
                    logging.exception(
                        "Unable to process bundle %s", name)
                finally:
                    # Make sure we got rid of the local copy
                    os.unlink(local_pathname)
        finally:
            try:
                os.rmdir(temp_dir)
            except:
                logging.exception("Unable to remove temporary directory")
        return aggregated_bundle

    # Desired format name, used in two methods below
    _desired_format = "Dashboard Bundle Format 1.3"

    def _load_bundle(self, local_pathname):
        """
        Load the bundle from local_pathname.

        There are various problems that can happen here but
        they should all be treated equally, the bundle not
        being used. This also transparently does schema validation
        so the chance of getting wrong data is lower.
        """
        with open(local_pathname, 'rt') as stream:
            format, bundle = DocumentIO.load(stream)
            return format, bundle

    def _convert_to_common_format(self, format, bundle):
        """
        Convert the bundle to the common format.

        This is a careful and possibly fragile process that may
        raise FutureFormatDetected exception. If that happens
        then desired_format (encoded in the function itself) must be
        changed and the code reviewed for any possible changes
        required to support the more recent format.
        """

        while True:
            # Break conditions, encoded separately for clarity
            if format == self._desired_format:
                # This is our desired break condition, when format
                # becomes (or starts as) the desired format
                break
            if DocumentEvolution.is_latest(bundle):
                # This is a less desired break condition, if we
                # got here then the only possible explanation is
                # that some program started with format > desired_format
                # and the DocumentEvolution API is updated to understand
                # it but we are not. In that case let's raise an exception
                raise FutureFormatDetected(format)
            # As long as the document format is old keep upgrading it
            # step-by-step. Evolution is done in place
            DocumentEvolution.evolve_document(bundle, one_step=True)

    def _combine_with_aggregated(self, aggregated_bundle, bundle):
        """
        Combine the bundle with the contents of aggregated_bundle.

        This method simply transplants all the test runs as that is what
        the bundle format was designed to be - a simple container for test
        runs.
        """
        assert bundle["format"] == self._desired_format
        assert aggregated_bundle["format"] == self._desired_format
        aggregated_bundle["test_runs"].extend(bundle.get("test_runs", []))

    @warnoncall
    def parse(self, resultname):
        pass

    @property
    def _blackbox_pathname(self):
        """
        The path to the blackbox bridge on the device.
        """
        return "/system/bin/lava-blackbox"

    @property
    def _fake_install_path(self):
        """
        The path that we create on the android system to
        indicate that the black box test is installed.

        This is used by uninstall() and install()
        """
        config = get_config()
        return os.path.join(config.installdir_android, self.testname)


testobj = BlackBoxTestBridge()
