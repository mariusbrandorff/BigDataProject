from atransformer import ATransformer

class OpenSkinTransformer(ATransformer):
    """docstring for OpenSkinTransformer."""

    def __init__(self, in_topic: str, bootstrap_servers: str, hive_host: str):
        super().__init__(in_topic, bootstrap_servers, hive_host)
    
