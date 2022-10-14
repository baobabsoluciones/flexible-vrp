from cornflow_client import InstanceCore
from cornflow_client.core.tools import load_json
import os


class Instance(InstanceCore):
    schema = load_json(
        os.path.join(os.path.dirname(__file__), "../schemas/instance.json")
    )
