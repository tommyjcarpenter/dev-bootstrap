"""Tests for the idempotent npm global install step in bootstrap.utils."""

import json
import subprocess
import unittest
from unittest import mock

from bootstrap import utils

INSTALLED_TREE = {
    "name": "npm",
    "dependencies": {
        "pyright": {"version": "1.1.411"},
        "@google/gemini-cli": {"version": "0.49.0"},
    },
}


def _completed(stdout: str, returncode: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=utils.NPM_LIST_GLOBALS_CMD, returncode=returncode, stdout=stdout)


class TestInstalledNpmGlobals(unittest.TestCase):
    def _run_with_stdout(self, stdout: str, returncode: int = 0) -> set[str]:
        with mock.patch.object(utils.subprocess, "run", return_value=_completed(stdout, returncode)):
            return utils._installed_npm_globals()

    def test_returns_package_names(self):
        self.assertEqual(self._run_with_stdout(json.dumps(INSTALLED_TREE)), {"pyright", "@google/gemini-cli"})

    def test_parses_tree_when_npm_ls_exits_nonzero(self):
        self.assertEqual(
            self._run_with_stdout(json.dumps(INSTALLED_TREE), returncode=1), {"pyright", "@google/gemini-cli"}
        )

    def test_no_globals_installed(self):
        self.assertEqual(self._run_with_stdout(json.dumps({"name": "npm"})), set())

    def test_empty_output_when_npm_missing(self):
        self.assertEqual(self._run_with_stdout("", returncode=1), set())


class TestInstallNpmPackages(unittest.TestCase):
    def setUp(self):
        installed = mock.patch.object(utils, "_installed_npm_globals", return_value={"pyright", "@google/gemini-cli"})
        run_cmd = mock.patch.object(utils, "_run_cmd")
        installed.start()
        self.run_cmd = run_cmd.start()
        self.addCleanup(mock.patch.stopall)

    def test_skips_install_when_all_present(self):
        utils._install_npm_packages(["pyright", "@google/gemini-cli"])
        self.run_cmd.assert_not_called()

    def test_installs_only_missing_on_windows(self):
        with mock.patch.object(utils.sys, "platform", "win32"):
            utils._install_npm_packages(["pyright", "yaml-language-server", "bash-language-server"])
        self.run_cmd.assert_called_once_with("npm install yaml-language-server bash-language-server -g")

    def test_installs_only_missing_with_sudo_on_posix(self):
        with mock.patch.object(utils.sys, "platform", "linux"):
            utils._install_npm_packages(["@google/gemini-cli", "yaml-language-server"])
        self.run_cmd.assert_called_once_with("sudo npm install yaml-language-server -g")

    def test_versioned_spec_always_installs(self):
        with mock.patch.object(utils.sys, "platform", "win32"):
            utils._install_npm_packages(["pyright@1.1.400"])
        self.run_cmd.assert_called_once_with("npm install pyright@1.1.400 -g")


if __name__ == "__main__":
    unittest.main()
