from jsonschema import validate

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "comments": {"type": "array", "items": {"type": "string"}},
        "initial_mkdirs": {"type": "array", "items": {"$ref": "#/definitions/dir"}},
        "links": {
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "work": {"type": "array", "items": {"$ref": "#/definitions/link"}},
                "private": {"type": "array", "items": {"$ref": "#/definitions/link"}},
            },
        },
        "commands": {
            "type": "object",
            "properties": {
                "all": {"type": "array", "items": {"type": "string"}},
                "mac": {"type": "array", "items": {"type": "string"}},
                "arch": {"type": "array", "items": {"type": "string"}},
            },
        },
        "packages": {
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
