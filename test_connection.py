
import os
import traceback
from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()

def main():
    print("STEP 1: Checking environment...", flush=True)

    host = os.getenv("FALKORDB_HOST")
    port = os.getenv("FALKORDB_PORT")
    username = os.getenv("FALKORDB_USERNAME")
    password = os.getenv("FALKORDB_PASSWORD")
    ssl_enabled = os.getenv("FALKORDB_SSL", "true").lower() == "true"

    if not all([host, port, username, password]):
        raise ValueError(
            "Missing FalkorDB environment variables. Check your .env file."
        )

    print(f"Host: {host}", flush=True)
    print(f"Port: {port}", flush=True)
    print(f"TLS enabled: {ssl_enabled}", flush=True)
    print("Credentials loaded (values hidden).", flush=True)

    print("STEP 2: Connecting to FalkorDB...", flush=True)

    db = FalkorDB(
        host=host,
        port=int(port),
        username=username,
        password=password,
        ssl=ssl_enabled,
        socket_connect_timeout=10,
        socket_timeout=10,
    )

    print("STEP 3: Sending test query...", flush=True)

    graph = db.select_graph("neuralnodes_test")
    result = graph.query("RETURN 1 AS connected")

    print("STEP 4: Query result:", result.result_set, flush=True)
    print("SUCCESS: FalkorDB connection works!", flush=True)
    db.close()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("CONNECTION FAILED:", flush=True)
        traceback.print_exc()
