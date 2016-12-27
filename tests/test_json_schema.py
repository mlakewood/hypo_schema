import unittest
from pprint import pprint

from jsonschema import validate

from hypothesis import given, settings
from hypo_schema.hypo_schema import generate_from_schema


EXAMPLE_JSON_SCHEMA= {
    "title": "Example Schema",
    "type": "object",
    "properties": {
        "firstName": {
            "type": "string"
        },
                "lastName": {
                    "type": "string"
                },
                "age": {
                    "description": "Age in years",
                    "type": "integer",
                    "minimum": 0
                },
                "listOfElements": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                "listOfRandom": {
                    "min": 4,
                    "max": 10,
                    "type": "array"
                },
                "type": {
                    "type": "string",
                    "enum": ["string", "int", "bool"]
                },
                "nestedMap": {
                    "type": "object",
                    "properties": {
                        "firstProp": {
                            "type": "string"
                        }
                    },
                    "required": ["firstProp"]
                }
            },
            "required": ["firstName", "lastName", "nestedMap", "listOfElements"]
}


class TestJsonSchema(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None


    @given(generate_from_schema(EXAMPLE_JSON_SCHEMA))
    @settings(max_examples=500)
    def test_basic_map(self, example_data):


#        example_data = generate_from_schema(example_json_schema).example()
#        pprint(example_data)

        validate(example_data, EXAMPLE_JSON_SCHEMA)
