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
            "description": "directories to be recursively made. For example, `~/.ssh/..`. You can specify whether to try deleting the directory first, which is sometimes helpful for rebootstrapping",
            "type": "array",
            "items": {"$ref": "#/definitions/dir"},
        },
        "links": {
            "description": "this is a list of softlinked dotfiles, from you `~/dotfiles` directory, that can vary by location if you want. IE, if you have a `.gitconfig` that you use on work machines, and a seperate one you use on private machines, you can specify these seperately, and when you run the script, you specify the location. There is also a generic `all` key for specifying location-agnostic keys.",
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "work": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "private": {"type": "array", "items": {"$ref": "#/definitions/link"}},
            },
        },
        "commands": {
            "description": "a list of arbitrary commands to run, which can be specified as os-agnostic, or by OS type. Warning, whatever you put here will be executed!.",
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"type": "string"}},
                "mac": {"type": "array", "items": {"type": "string"}},
                "arch": {"type": "array", "items": {"type": "string"}},
            },
        },
        "packages": {
            "description": "a list of packages to install, which can be specified as os-agnostic, or by OS type. Examples of agnostic installs include `npm` and `pip`. Examples of `mac` include `brew`. You can also include 'agnostic' installs in the os-specific sections, for example, 'I only want this NPM package installed on my mac'.",
            "type": "object",
            "properties": {
                "mac": {"type": "object"},
                "arch": {"type": "object"},
                "all": {"type": "object"},
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
            },
        },
        "link": {
            "type": "object",
            "required": ["src", "dst"],
            "properties": {
                "src": {"type": "string"},
                "dst": {"type": "string"},
            },
        },
    },
    "additionalProperties": False,
}


def config_validate(config):
    validate(instance=config, schema=schema)
