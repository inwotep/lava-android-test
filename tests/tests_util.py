#!/usr/bin/env python
import os
import stat
import subprocess

test_tmp = '/tmp/lava-android-test-tmp'
def fake_adb(output_str='', target_path=test_tmp):
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    fake_adb_path = os.path.join(target_path, 'adb')
    adb_file = open(fake_adb_path, 'w')
    adb_file.write('#/bin/bash\n')
    adb_file.write('echo \'\n')
    adb_file.write(output_str)
    adb_file.write('\'\n')
    adb_file.close()
    os.chmod(fake_adb_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    os.chmod(target_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    os.environ['PATH'] = target_path + ':' + os.environ['PATH']

def clear_fake(target_path=test_tmp):
    if not os.path.exists(target_path):
        return
    if os.path.isdir(target_path):
        for sub_path in os.listdir(target_path):
            clear_fake(os.path.join(target_path, sub_path))
        os.rmdir(target_path)
    else:
        os.unlink(target_path)

def main():
    fake_adb('hello, \ntest');
    cmd = 'adb shell ls'
    p = subprocess.Popen(cmd, shell=True)
    p.wait()
    clear_fake()

if __name__ == '__main__':
    main()
