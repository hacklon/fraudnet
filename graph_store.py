import os
from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()
GRAPH_NAME = os.getenv("FALKORDB_GRAPH", "fraudnet")


def connect_graph():
    """Connect to the configured FalkorDB instance and select the fraud graph."""
    required = ["FALKORDB_HOST", "FALKORDB_PORT", "FALKORDB_USERNAME", "FALKORDB_PASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError("Missing environment variables: " + ", ".join(missing))

    client = FalkorDB(
        host=os.environ["FALKORDB_HOST"],
        port=int(os.environ["FALKORDB_PORT"]),
        username=os.environ["FALKORDB_USERNAME"],
        password=os.environ["FALKORDB_PASSWORD"],
        ssl=os.getenv("FALKORDB_SSL", "true").lower() == "true",
        socket_connect_timeout=10,
        socket_timeout=60,
    )
    return client, client.select_graph(GRAPH_NAME)
