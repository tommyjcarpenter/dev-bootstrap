from jsonschema import validate

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "comments": {
            "description": "this is just a list of strings for your own keeping since JSON has no native commenting mechanism. IE remind yourself why you install something etc.",
            "type": "array",
            "items": {"type": "string"},
        },
        "initial_mkdirs": {
            "description": "directories to be recursively made, organized by OS type. Use 'all' for cross-platform dirs, and 'mac'/'arch'/'ubuntu'/'windows' for OS-specific dirs.",
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
                "mac": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
                "arch": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
                "ubuntu": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
                "windows": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
            },
        },
        "links": {
            "description": "softlinked dotfiles from ~/dotfiles, organized by OS type. Use 'all' for cross-platform links, and 'mac'/'arch'/'ubuntu'/'windows' for OS-specific links. For work/private specific links, put them in the respective bootstrap_config_work.json or bootstrap_config_private.json files under links.all.",
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "mac": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "arch": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "ubuntu": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "windows": {"type": "array", "items": {"$ref": "#/definitions/link"}},
            },
        },
        "commands": {
            "description": "a list of arbitrary commands to run, which can be specified as os-agnostic, or by OS type. Warning, whatever you put here will be executed!. Each entry can be a plain string or an object with cmd, check, and label fields. Runs *before* packages — use it for things package install depends on (e.g. installing scoop).",
            "$ref": "#/definitions/commands_section",
        },
        "post_commands": {
            "description": "Same shape as `commands`, but runs *after* packages and file_associations. Use this for steps that depend on packages already being installed — e.g. registering a font file that scoop installed but didn't put in the user font registry.",
            "$ref": "#/definitions/commands_section",
        },
        "packages": {
            "description": "a list of packages to install, which can be specified as os-agnostic, or by OS type. Examples of agnostic installs include `npm`. Examples of `mac` include `brew`. You can also include 'agnostic' installs in the os-specific sections, for example, 'I only want this NPM package installed on my mac'.",
            "type": "object",
            "properties": {
                "mac": {"$ref": "#/definitions/package_section"},
                "arch": {"$ref": "#/definitions/package_section"},
                "ubuntu": {"$ref": "#/definitions/package_section"},
                "windows": {"$ref": "#/definitions/package_section"},
                "all": {"$ref": "#/definitions/package_section"},
            },
            "additionalProperties": False,
        },
        "prereq_packages": {
            "description": "packages that provide language toolchains (rust/cargo, go, uv) needed before other packages can be installed. These are installed before `packages`.",
            "type": "object",
            "properties": {
                "mac": {"$ref": "#/definitions/package_section"},
                "arch": {"$ref": "#/definitions/package_section"},
                "ubuntu": {"$ref": "#/definitions/package_section"},
                "windows": {"$ref": "#/definitions/package_section"},
            },
            "additionalProperties": False,
        },
        "file_associations": {
            "description": "Register file extension associations. Currently Windows-only — writes per-user keys under HKCU\\Software\\Classes so Explorer double-click opens the right app. No admin needed.",
            "type": "object",
            "properties": {
                "windows": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/file_assoc"},
                },
            },
            "additionalProperties": False,
        },
        "shell_menu_cleanup": {
            "description": "Windows right-click menu cleanup state. Three arrays cover the three places shell verbs hide: com_handlers_blocked writes CLSIDs to the HKLM Shell Extensions Blocked list, static_verbs_disabled writes an empty LegacyDisable REG_SZ under a verb key, appx_packages_removed passes a wildcard pattern to Get-AppxPackage | Remove-AppxPackage for MSIX-packaged shell extensions.",
            "type": "object",
            "properties": {
                "windows": {
                    "type": "object",
                    "properties": {
                        "com_handlers_blocked": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/shell_menu_com_handler"},
                        },
                        "static_verbs_disabled": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/shell_menu_static_verb"},
                        },
                        "appx_packages_removed": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/shell_menu_appx_package"},
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
    },
    "definitions": {
        "dir": {
            "type": "object",
            "required": ["dir"],
            "properties": {
                "dir": {"type": "string", "description": "The dir to make. "},
                "delfirst": {
                    "type": "boolean",
                    "description": "try to remove the directory before making?",
                    "default": False,
                },
                "sudo": {
                    "type": "boolean",
                    "description": "run with sudo (for system directories outside ~)",
                    "default": False,
                },
            },
        },
        "link": {
            "type": "object",
            "required": ["src", "dst"],
            "properties": {
                "src": {"type": "string"},
                "dst": {"type": "string"},
                "sudo": {
                    "type": "boolean",
                    "description": "run with sudo (for system directories outside ~)",
                    "default": False,
                },
            },
        },
        "command_with_check": {
            "type": "object",
            "required": ["cmd"],
            "properties": {
                "cmd": {"type": "string", "description": "The command to run."},
                "check": {"type": "string", "description": "Shell command — if exit 0, skip cmd."},
                "label": {"type": "string", "description": "Human-readable name for logs (defaults to truncated cmd)."},
            },
            "additionalProperties": False,
        },
        "commands_section": {
            "type": "object",
            "properties": {
                "all": {
                    "type": "array",
                    "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]},
                },
                "mac": {
                    "type": "array",
                    "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]},
                },
                "arch": {
                    "type": "array",
                    "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]},
                },
                "ubuntu": {
                    "type": "array",
                    "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]},
                },
                "windows": {
                    "type": "array",
                    "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]},
                },
            },
        },
        "package_list": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of package names. For some types (e.g. snap) per-entry flags can be appended, e.g. 'code --classic'.",
        },
        "package_section": {
            "type": "object",
            "description": "Map of package-type → list of packages. Keys are restricted to known package types — typos like 'brews' fail validation rather than silently skipping.",
            "properties": {
                "brew_tap": {"$ref": "#/definitions/package_list"},
                "brew": {"$ref": "#/definitions/package_list"},
                "brew_cask": {"$ref": "#/definitions/package_list"},
                "pacman": {"$ref": "#/definitions/package_list"},
                "yay": {"$ref": "#/definitions/package_list"},
                "ppa": {"$ref": "#/definitions/package_list"},
                "apt": {"$ref": "#/definitions/package_list"},
                "snap": {"$ref": "#/definitions/package_list"},
                "winget": {"$ref": "#/definitions/package_list"},
                "scoop_bucket": {"$ref": "#/definitions/package_list"},
                "scoop": {"$ref": "#/definitions/package_list"},
                "pip": {"$ref": "#/definitions/package_list"},
                "npm": {"$ref": "#/definitions/package_list"},
                "go_install": {"$ref": "#/definitions/package_list"},
                "cargo": {"$ref": "#/definitions/package_list"},
                "fisher": {"$ref": "#/definitions/package_list"},
            },
            "additionalProperties": False,
        },
        "file_assoc": {
            "type": "object",
            "required": ["ext", "progid", "cmd"],
            "properties": {
                "ext": {"type": "string", "description": "Extension including the dot, e.g. '.yaml'"},
                "progid": {"type": "string", "description": "Class identifier, e.g. 'Neovim.YAML'"},
                "cmd": {"type": "string", "description": "Launch command — Windows substitutes %1 with the file path"},
                "name": {
                    "type": "string",
                    "description": "Friendly app name shown in the 'Open with' picker (otherwise Windows reads metadata from the first .exe in `cmd`, which is often blank or labeled 'Shim')",
                },
                "icon": {
                    "type": "string",
                    "description": "Icon for files of this type in Explorer. Format: '<path>,<index>' to pull a PE resource (e.g. 'C:\\\\Program Files\\\\Neovim\\\\bin\\\\nvim.exe,0'), or a path to a .ico file.",
                },
                "label": {"type": "string", "description": "Human-readable label for logs"},
            },
            "additionalProperties": False,
        },
        "shell_menu_com_handler": {
            "type": "object",
            "required": ["clsid"],
            "properties": {
                "clsid": {
                    "type": "string",
                    "description": "CLSID like '{3D1975AF-48C6-4f8e-A182-BE0E08FA86A9}'. Written as a value name (empty REG_SZ) under HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Shell Extensions\\Blocked.",
                },
                "name": {"type": "string", "description": "Human-readable label for logs"},
            },
            "additionalProperties": False,
        },
        "shell_menu_static_verb": {
            "type": "object",
            "required": ["path"],
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Registry path to the verb key, e.g. 'HKLM:\\\\Software\\\\Classes\\\\Directory\\\\shell\\\\AnyCode'. An empty LegacyDisable REG_SZ is written under the key, hiding the verb from the menu without deleting it. Treated as already-done if the key doesn't exist on the current machine.",
                },
                "name": {"type": "string", "description": "Human-readable label for logs"},
            },
            "additionalProperties": False,
        },
        "shell_menu_appx_package": {
            "type": "object",
            "required": ["name_pattern"],
            "properties": {
                "name_pattern": {
                    "type": "string",
                    "description": "Wildcard package name pattern for Get-AppxPackage, e.g. '*Mp3tag.ShellExtension*'. Matching packages are uninstalled with Remove-AppxPackage.",
                },
                "name": {"type": "string", "description": "Human-readable label for logs"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}


def config_validate(config):
    validate(instance=config, schema=schema)
