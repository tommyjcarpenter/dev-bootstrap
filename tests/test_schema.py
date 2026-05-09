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


if __name__ == "__main__":
    unittest.main()
