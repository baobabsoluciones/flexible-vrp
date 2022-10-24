# Class instance is used to store the problem input data.

from cornflow_client import InstanceCore, get_empty_schema
from cornflow_client.core.tools import load_json
import os


class Instance(InstanceCore):
    schema = load_json(
        os.path.join(os.path.dirname(__file__), "../schemas/instance.json")
    )
    schema_checks = get_empty_schema()
