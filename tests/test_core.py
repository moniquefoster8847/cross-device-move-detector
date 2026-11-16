import os
import tempfile
import unittest

from cross_device_move_detector import is_cross_device


class TestCrossDeviceMoveDetector(unittest.TestCase):
    def test_same_directory_is_not_cross_device(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "a.txt")
            dst = os.path.join(tmp, "b.txt")
            with open(src, "w"):
                pass
            with open(dst, "w"):
                pass
            self.assertFalse(is_cross_device(src, dst))

    def test_same_directory_symlink_is_not_cross_device(self):
        with tempfile.TemporaryDirectory() as tmp:
            real = os.path.join(tmp, "real")
            os.mkdir(real)
            link = os.path.join(tmp, "link")
            os.symlink(real, link)
            src = os.path.join(real, "a.txt")
            dst = os.path.join(link, "b.txt")
            with open(src, "w"):
                pass
            with open(dst, "w"):
                pass
            self.assertFalse(is_cross_device(src, dst))

    def test_nonexistent_source_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = os.path.join(tmp, "b.txt")
            with open(dst, "w"):
                pass
            self.assertFalse(is_cross_device(os.path.join(tmp, "missing.txt"), dst))

    def test_nonexistent_destination_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "a.txt")
            with open(src, "w"):
                pass
            self.assertFalse(is_cross_device(src, os.path.join(tmp, "missing.txt")))

    def test_both_nonexistent_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(
                is_cross_device(
                    os.path.join(tmp, "missing-src.txt"),
                    os.path.join(tmp, "missing-dst.txt"),
                )
            )

    def test_cross_device_when_devices_differ(self):
        # /dev/shm is a tmpfs on Linux and is usually a different device from
        # the directory containing the test. If it is not available or is on
        # the same device, skip rather than assert a false positive.
        try:
            shm_dev = os.stat("/dev/shm").st_dev
        except OSError:
            self.skipTest("/dev/shm is not available on this system")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dev = os.stat(tmp).st_dev
            if tmp_dev == shm_dev:
                self.skipTest("/dev/shm and temporary directory are on the same device")
            src = os.path.join(tmp, "a.txt")
            dst = os.path.join("/dev/shm", "cross-device-move-detector-test.txt")
            with open(src, "w"):
                pass
            try:
                self.assertTrue(is_cross_device(src, dst))
            finally:
                # The destination file is not created by the check, but remove
                # it if a previous run left one behind.
                try:
                    os.unlink(dst)
                except FileNotFoundError:
                    pass

    def test_destination_parent_missing_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "a.txt")
            with open(src, "w"):
                pass
            self.assertFalse(
                is_cross_device(src, os.path.join(tmp, "no-such-dir", "b.txt"))
            )

    def test_symlink_to_different_device(self):
        # A symlink on the same device that points to a file on another device
        # should be treated as cross-device because realpath resolves the link.
        try:
            shm_dev = os.stat("/dev/shm").st_dev
        except OSError:
            self.skipTest("/dev/shm is not available on this system")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dev = os.stat(tmp).st_dev
            if tmp_dev == shm_dev:
                self.skipTest("/dev/shm and temporary directory are on the same device")
            real = os.path.join("/dev/shm", "cross-device-move-detector-real.txt")
            link = os.path.join(tmp, "link.txt")
            with open(real, "w"):
                pass
            os.symlink(real, link)
            try:
                self.assertTrue(is_cross_device(link, os.path.join(tmp, "b.txt")))
            finally:
                try:
                    os.unlink(real)
                except FileNotFoundError:
                    pass


if __name__ == "__main__":
    unittest.main()
