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

import datetime
import functools
import logging
import os
import pdb
import shutil
import subprocess
import tempfile

from linaro_dashboard_bundle.evolution import DocumentEvolution
from linaro_dashboard_bundle.io import DocumentIO

from lava_android_test.config import get_config


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

        The two special entries, . and .., are omitted
        """
        for line in self(['ls', dirname]).splitlines():
            # a, b and c are various pieces of stat data
            # but we don't need that here.
            a, b, c, pathname = line.split(' ', 3)
            if pathname not in ('.', '..'):
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

    def setadb(self, adb=None):
        if self.adb is None and adb is not None:
            self.adb = adb
        else:
            self.adb = adb
        self.super_adb = SuperAdb(adb)

    def getadb(self):
        return self.adb


class Sponge(object):
    """
    A simple namespace-like object that anyone can assign and read freely.

    To get some understanding of what is going on both reads and writes are
    logged.
    """

    def __getattr__(self, attr):
        return super(Sponge, self).__getattr__(attr)

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

    def install(self, install_options=None):
        """
        "Install" blackbox on the test device.

        Black box tests cannot be installed, they must be pre-baked into the
        image. To conform to the 'protocol' used by lava-android-test we will
        perform a fake 'installation' of the black box tests by creating a
        directory that lava-android-test is checking for. We do that only if
        the lava-blackbox executable, which is the entry point to black box
        tests exists in the image.

        ..note::
            This method is part of the lava-android-test framework API.
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

    def uninstall(self):
        """
        Conformance method to keep up with the API required by
        lava-android-test. It un-does what install() did by removing the
        _fake_install_path directory from the device.

        ..note::
            This method is part of the lava-android-test framework API.
        """
        if self.adb.exists(self._fake_install_path):
            self.adb.rmtree(self._fake_install_path)

    @debuggable
    def run(self, quiet=False, run_options=None):
        """
        Run the black-box test on the target device.

        Use ADB to run the black-box executable on the device. Keep the results
        in the place that lava-android-test expects us to use.

        ..note::
            This method is part of the lava-android-test framework API.
        """
        # The blackbox test runner will create a directory each time it is
        # started. All of those directories will be created relative to a so
        # called spool directory. Instead of using the default spool directory
        # (which can also change) we will use the directory where
        # lava-android-test keeps all of the results.
        spool_dir = get_config().resultsdir_android
        logging.debug("Using spool directory for black-box testing: %r", spool_dir)
        stuff_before = frozenset(self.super_adb.listdir(spool_dir))
        blackbox_command = [
            'shell', self._blackbox_pathname,
            '--spool', spool_dir,
            '--run-all-tests']
        # Let's run the blackbox executable via ADB
        logging.debug("Starting black-box tests...")
        self.super_adb(blackbox_command, stdout=None)
        logging.debug("Black-box tests have finished!")
        stuff_after = frozenset(self.super_adb.listdir(spool_dir))
        # Check what got added to the spool directory
        new_entries = stuff_after - stuff_before
        if len(new_entries) == 0:
            raise RuntimeError("Nothing got added to the spool directory")
        elif len(new_entries) > 1:
            raise RuntimeError("Multiple items added to the spool directory")
        result_id = list(new_entries)[0]
        print "The blackbox test have finished running, the result id is %r" % result_id
        return result_id

    def parse(self, result_id):
        """
        UNIMPLEMENTED METHOD

        Sadly this method is never called as lava-android-test crashes before
        it gets to realize it is processing blackbox results and load this
        class. This crash _may_ be avoided by hiding the real results of
        blackbox and instead populating the results directory with dummy test
        results that only let LAVA figure out that blackbox is the test to
        load. Then we could monkey patch other parts and it could be
        implemented.

        ONCE THIS IS FIXED THE FOLLOWING DESCRIPTION SHOULD APPLY

        Parse and save results of previous test run.

        The result_id is a name of a directory on the Android device (
        relative to the resultsdir_android configuration option).

        ..note::
            This method is part of the lava-android-test framework API.
        """
        # Sadly since the goal is integration with lava lab I don't have the
        # time to do it. In the lab we use lava-android-test run -o anyway.
        raise NotImplementedError()

    def _get_combined_bundle(self, result_id):
        """
        Compute the combined bundle of a past run and return it
        """
        config = get_config()
        temp_dir = tempfile.mkdtemp()
        remote_bundle_dir = os.path.join(config.resultsdir_android, result_id)
        try:
            self._copy_all_bundles(remote_bundle_dir, temp_dir)
            bundle = self._combine_bundles(temp_dir)
        finally:
            shutil.rmtree(temp_dir)
        return bundle

    # Desired format name, used in a few methods below
    _desired_format = "Dashboard Bundle Format 1.3"

    def _copy_all_bundles(self, android_src, host_dest):
        """
        Use adb pull to copy all the files from android_src (android
        fileystem) to host_dest (host filesystem).
        """
        logging.debug("Saving bundles from %s to %s", android_src, host_dest)
        for name in self.super_adb.listdir(android_src):
            logging.debug("Considering file %s", name)
            # NOTE: We employ simple filtering for '.json' files. This prevents
            # spurious JSON parsing errors if the result directory has
            # additional files of any kind.
            #
            # We _might_ want to lessen that eventually restriction but at this
            # time blackbox is really designed to be self-sufficient so there
            # is no point of additional files.
            if not name.endswith('.json'):
                continue
            remote_pathname = os.path.join(android_src, name)
            local_pathname = os.path.join(host_dest, name)
            try:
                logging.debug(
                    "Copying %s to %s", remote_pathname, local_pathname)
                self.adb.pull(remote_pathname, local_pathname)
            except:
                logging.exception("Unable to copy bundle %s", name)

    def _combine_bundles(self, dirname):
        """
        Combine all bundles from a previous test run into one bundle.

        Returns the aggregated bundle object

        Load, parse and validate each bundle from the specified directory and
        combine them into one larger bundle. This is somewhat tricky. Each
        bundle we coalesce may be generated by a different, separate programs
        and may, thus, use different formats.

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
        # Iterate over all files there
        for name in os.listdir(dirname):
            bundle_pathname = os.path.join(dirname, name)
            # Process bundle one by one
            try:
                format, bundle = self._load_bundle(bundle_pathname)
                self._convert_to_common_format(format, bundle)
                self._combine_with_aggregated(aggregated_bundle, bundle)
            except:
                logging.exception("Unable to process bundle %s", name)
        # Return the aggregated bundle
        return aggregated_bundle

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

    def _monkey_patch_lava(self):
        """
        Monkey patch the implementation of
        lava_android_test.commands.generate_bundle

        This change is irreversible but given the one-off nature of
        lava-android-test this is okay. It should be safe to do this since
        LAVA will only load the blackbox test module if we explicitly request
        to run it. At that time no other tests will run in the same process.

        This method should not be used once lava-android-test grows a better
        API to allow us to control how bundles are generated.
        """
        from lava_android_test import commands
        def _phony_generate_bundle(serial=None, result_id=None,
                   test=None, test_id=None, attachments=[]):
            if result_id is None:
                raise NotImplementedError
            return self._get_combined_bundle(result_id)
        commands.generate_bundle = _phony_generate_bundle 
        logging.warning(
            "The 'blackbox' test definition has monkey-patched the function"
            " lava_android_test.commands.generate_bundle() if you are _not_"
            " running the blackbox test or are experiencing odd problems/crashes"
            " below please look at this method first")


# initialize the blackbox test definition object
testobj = BlackBoxTestBridge()

# Then monkey patch lava-android-test so that parse keeps working
testobj._monkey_patch_lava()
