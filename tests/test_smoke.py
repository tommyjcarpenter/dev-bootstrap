"""Smoke tests: import every bootstrap submodule and assert its public helpers exist.

These tests intentionally do NOT exercise behavior — they exist only to catch import-time
breakage (syntax errors, wrong import paths, accidentally renamed helpers) on every CI run.
The OS-specific modules import cleanly on any platform; only their inner functions actually
shell out to OS-specific tools, so import-only assertions are safe to run on the Linux runner.
"""

import unittest


class TestModuleImports(unittest.TestCase):
    def test_arch_module(self):
        from bootstrap.os_specific import arch

        self.assertTrue(callable(arch.install_pacman_packages))
        self.assertTrue(callable(arch.install_yay_packages))

    def test_mac_module(self):
        from bootstrap.os_specific import mac

        self.assertTrue(callable(mac.install_brew_taps))
        self.assertTrue(callable(mac.install_brew_packages))
        self.assertTrue(callable(mac.install_brew_cask_packages))

    def test_ubuntu_module(self):
        from bootstrap.os_specific import ubuntu

        self.assertTrue(callable(ubuntu.install_ppas))
        self.assertTrue(callable(ubuntu.install_apt_packages))
        self.assertTrue(callable(ubuntu.install_snap_packages))

    def test_windows_module(self):
        from bootstrap.os_specific import windows

        self.assertTrue(callable(windows.refresh_path))
        self.assertTrue(callable(windows.install_winget_packages))
        self.assertTrue(callable(windows.install_file_associations))
        self.assertTrue(callable(windows.set_file_assoc))

    def test_core_modules(self):
        from bootstrap import boot, log, runboot, schema, utils

        self.assertTrue(callable(boot.boot))
        self.assertTrue(callable(boot.boot_config))
        self.assertTrue(callable(runboot.detect_systype))
        self.assertTrue(callable(schema.config_validate))
        self.assertTrue(callable(utils.packages))
        self.assertTrue(hasattr(log, "header"))


if __name__ == "__main__":
    unittest.main()
