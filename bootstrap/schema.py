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
            "description": "directories to be recursively made, organized by OS type. Use 'all' for cross-platform dirs, and 'mac'/'arch'/'ubuntu' for OS-specific dirs.",
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
                "mac": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
                "arch": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
                "ubuntu": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
            },
        },
        "links": {
            "description": "softlinked dotfiles from ~/dotfiles, organized by OS type. Use 'all' for cross-platform links, and 'mac'/'arch'/'ubuntu' for OS-specific links. For work/private specific links, put them in the respective bootstrap_config_work.json or bootstrap_config_private.json files under links.all.",
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "mac": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "arch": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "ubuntu": {"type": "array", "items": {"$ref": "#/definitions/link"}},
            },
        },
        "commands": {
            "description": "a list of arbitrary commands to run, which can be specified as os-agnostic, or by OS type. Warning, whatever you put here will be executed!. Each entry can be a plain string or an object with cmd, check, and label fields.",
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]}},
                "mac": {"type": "array", "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]}},
                "arch": {"type": "array", "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]}},
                "ubuntu": {"type": "array", "items": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/command_with_check"}]}},
            },
        },
        "packages": {
            "description": "a list of packages to install, which can be specified as os-agnostic, or by OS type. Examples of agnostic installs include `npm`. Examples of `mac` include `brew`. You can also include 'agnostic' installs in the os-specific sections, for example, 'I only want this NPM package installed on my mac'.",
            "type": "object",
            "properties": {
                "mac": {"type": "object"},
                "arch": {"type": "object"},
                "ubuntu": {"type": "object"},
                "all": {"type": "object"},
            },
        },
        "prereq_packages": {
            "description": "packages that provide language toolchains (rust/cargo, go, poetry) needed before other packages can be installed. These are installed before `packages`.",
            "type": "object",
            "properties": {
                "mac": {"type": "object"},
                "arch": {"type": "object"},
                "ubuntu": {"type": "object"},
            },
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
    },
    "additionalProperties": False,
}


def config_validate(config):
    validate(instance=config, schema=schema)
