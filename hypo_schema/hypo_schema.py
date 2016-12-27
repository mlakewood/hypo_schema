from copy import deepcopy
from random import randint

from hypothesis import strategies as hs



def gen_int(prop):
    min_value = prop.get("minimum", None)
    max_value = prop.get("maximum", None)
    return hs.integers(min_value=min_value, max_value=max_value)

def gen_string(prop):
    return hs.text()

def should_include(key, required_list):
    if key in required_list:
        return True
    else:
        return bool(randint(0, 1))

def gen_array(prop):
    min_value = prop.get("minimum", None)
    max_value = prop.get("maximum", None)

    if prop.get("items", {}).get("type", False) is not False:
        generator = get_generator(prop.get("items"))
        return hs.lists(elements=generator, min_size=min_value, max_size=max_value)
    return hs.lists(elements=gen_anything(), min_size=min_value, max_size=max_value)

def gen_anything():
    return hs.one_of(hs.text(), hs.booleans(), hs.integers(), hs.none())

def gen_object(prop):

    required = prop["required"]
    output = {}

    for k in prop["properties"].keys():
        json_prop = prop["properties"][k]

        if should_include(k, required):
            output[k] = get_generator(prop["properties"][k])

    return hs.fixed_dictionaries(output)

def gen_enum(prop):
    enum = prop["enum"]
    return hs.sampled_from(enum)

def get_generator(prop):
    disp = { "string": gen_string,
             "integer": gen_int,
             "number": gen_int,
             "object": gen_object,
             "array": gen_array,
             "enum": gen_enum,
    }

    enum = prop.get("enum", None)
    if enum is not None:
        return gen_enum(prop)


    json_type = prop.get("type", None)
    if json_type is None:
        raise JsonTypeError("Couldnt find type in prop {0}".format(prop))

    return disp[json_type](prop)

def generate_from_schema(json_schema):
    example_data = get_generator(json_schema)
    return example_data


class JsonTypeError(Exception):
    pass
