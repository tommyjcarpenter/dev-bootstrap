"""Schema regression tests"""

import unittest

from jsonschema import ValidationError

from bootstrap.schema import config_validate


class TestPackageSchema(unittest.TestCase):
    def test_valid_minimal(self):
        config_validate({"packages": {"all": {"npm": ["typescript", "prettier"]}}})

    def test_valid_per_os_with_cross_platform(self):
        config_validate(
            {
                "packages": {
                    "mac": {
                        "brew": ["git"],
                        "brew_cask": ["firefox"],
                        "npm": ["typescript"],
                    },
                    "arch": {"pacman": ["git"], "yay": ["spotify"]},
                    "ubuntu": {
                        "apt": ["git"],
                        "ppa": ["ppa:foo/bar"],
                        "snap": ["code --classic"],
                    },
                    "windows": {"winget": ["Git.Git"], "scoop": ["fzf"]},
                }
            }
        )

    def test_unknown_package_type_rejected(self):
        # typo: "brews" instead of "brew" — exactly the class of bug #11 was about
        with self.assertRaises(ValidationError):
            config_validate({"packages": {"mac": {"brews": ["git"]}}})

    def test_non_array_value_rejected(self):
        with self.assertRaises(ValidationError):
            config_validate({"packages": {"all": {"npm": "typescript"}}})

    def test_non_string_item_rejected(self):
        with self.assertRaises(ValidationError):
            config_validate({"packages": {"all": {"npm": [123]}}})

    def test_unknown_os_section_rejected(self):
        with self.assertRaises(ValidationError):
            config_validate({"packages": {"freebsd": {"pkg": ["git"]}}})

    def test_prereq_packages_validated_too(self):
        # prereq_packages shares the same package_section definition
        with self.assertRaises(ValidationError):
            config_validate({"prereq_packages": {"mac": {"bogus_type": ["x"]}}})


class TestShellMenuCleanupSchema(unittest.TestCase):
    def test_valid_full(self):
        config_validate(
            {
                "shell_menu_cleanup": {
                    "windows": {
                        "com_handlers_blocked": [{"clsid": "{3D1975AF-48C6-4f8e-A182-BE0E08FA86A9}", "name": "Foo"}],
                        "static_verbs_disabled": [
                            {"path": "HKLM:\\Software\\Classes\\Directory\\shell\\AnyCode", "name": "AnyCode"}
                        ],
                        "appx_packages_removed": [{"name_pattern": "*Mp3tag.ShellExtension*", "name": "Mp3tag"}],
                    }
                }
            }
        )

    def test_valid_minimal_required_only(self):
        # name is optional everywhere; only the required key per definition is needed
        config_validate(
            {
                "shell_menu_cleanup": {
                    "windows": {
                        "com_handlers_blocked": [{"clsid": "{abc}"}],
                        "static_verbs_disabled": [{"path": "HKLM:\\x"}],
                        "appx_packages_removed": [{"name_pattern": "*x*"}],
                    }
                }
            }
        )

    def test_missing_required_clsid_rejected(self):
        with self.assertRaises(ValidationError):
            config_validate({"shell_menu_cleanup": {"windows": {"com_handlers_blocked": [{"name": "Foo"}]}}})

    def test_missing_required_path_rejected(self):
        with self.assertRaises(ValidationError):
            config_validate({"shell_menu_cleanup": {"windows": {"static_verbs_disabled": [{"name": "Foo"}]}}})

    def test_unknown_property_rejected(self):
        # typo'd array key under windows is not in properties → additionalProperties False
        with self.assertRaises(ValidationError):
            config_validate({"shell_menu_cleanup": {"windows": {"com_handlers_blockd": [{"clsid": "{x}"}]}}})

    def test_unknown_os_section_rejected(self):
        with self.assertRaises(ValidationError):
            config_validate({"shell_menu_cleanup": {"linux": {"com_handlers_blocked": [{"clsid": "{x}"}]}}})


if __name__ == "__main__":
    unittest.main()
