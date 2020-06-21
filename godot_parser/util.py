""" Utils """


def stringify_object(value):
    """ Serialize a value to the godot file format """
    if value is None:
        return "null"
    elif isinstance(value, str):
        return '"' + value + '"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, dict):
        return (
            "{\n"
            + ",\n".join(
                ['"%s": %s' % (k, stringify_object(v)) for k, v in value.items()]
            )
            + "\n}"
        )
    elif isinstance(value, list):
        return "[ " + ", ".join([stringify_object(v) for v in value]) + " ]"
    else:
        return str(value)
