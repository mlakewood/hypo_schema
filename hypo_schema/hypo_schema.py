from random import randint

from hypothesis import strategies as hs

from hypo_schema.regex import regex


def gen_int(prop):
    min_value = prop.get("minimum", None)
    max_value = prop.get("maximum", None)
    return hs.integers(min_value=min_value, max_value=max_value)


def gen_string(prop):
    min_value = prop.get("minLength", None)
    max_value = prop.get("maxLength", None)
    pattern = None
    if prop.get("pattern", None):
        pattern = prop["pattern"]
        if min_value is not None:
            return hs.just(regex(pattern).filter(lambda x: min_value <= len(x)).example())
        return hs.just(regex(pattern).example())

    else:
        return hs.text(alphabet=pattern,
                       min_size=min_value,
                       max_size=max_value)


def should_include(key, required_list):
    if key in required_list:
        return True
    else:
        return bool(randint(0, 1))


def gen_array(prop):
    min_items = prop.get("minItems", None)
    max_items = prop.get("maxItems", None)
    if prop.get("items", {}).get("type", False) is not False:
        generator = get_generator(prop.get("items"))
        return hs.lists(elements=generator,
                        min_size=min_items,
                        max_size=max_items)
    return hs.lists(elements=gen_anything(),
                    min_size=min_items,
                    max_size=max_items)


def gen_anything():
    return hs.one_of(hs.text(), hs.booleans(), hs.integers(), hs.none(),
                     hs.floats())

def gen_json_values():
    return hs.text() | hs.booleans() | hs.integers() | hs.none() | hs.floats()

def gen_any_obj():
    return hs.recursive(hs.dictionaries(hs.text(), gen_json_values()),
                        lambda children: hs.dictionaries(hs.text(), children),
                        max_leaves=10)

def gen_object(prop):

    required = prop.get("required", [])
    output = {}
    prop_key = "properties"
    if prop.get("properties", None) is None:
        if prop["additionalProperties"] is True or prop["additionalProperties"] == {}:
            return gen_any_obj()
        return hs.dictionaries(hs.text(min_size=1),
                               get_generator(prop["additionalProperties"]))

    for k in prop[prop_key].keys():
        json_prop = prop[prop_key][k]

        if should_include(k, required):
            output[k] = get_generator(json_prop)

    return hs.fixed_dictionaries(output)


def gen_enum(prop):
    enum = prop["enum"]
    return hs.sampled_from(enum)

def gen_bool(prop):
    return hs.booleans()

def gen_one_of(prop):
    possible_values = []
    for value in prop["oneOf"]:
        possible_values.append(get_generator(value))

    return hs.one_of(possible_values)



def get_generator(prop):
    disp = {"string": gen_string,
            "integer": gen_int,
            "number": gen_int,
            "boolean": gen_bool,
            "object": gen_object,
            "array": gen_array,
    }

    enum = prop.get("enum", None)
    if enum is not None:
        return gen_enum(prop)

    one_of = prop.get("oneOf", None)
    if one_of is not None:
        return gen_one_of(prop)

    json_type = prop.get("type", None)
    if json_type is None:
        raise JsonTypeError("Couldnt find type in prop {0}".format(prop))

    return disp[json_type](prop)

def generate_from_schema(json_schema):
    example_data = get_generator(json_schema)
    return example_data


class JsonTypeError(Exception):
    pass
