"""Seed FalkorDB with a fraud graph: normal users, benign decoys, and 3 planted rings.

Schema
  (:Account {id, age_days, kind})   kind is NOT stored; ground truth goes to ground_truth.json
  (:Device {id})   (:IP {id})
  (Account)-[:USES]->(Device)
  (Account)-[:LOGGED_FROM]->(IP)
  (Account)-[:SENT {amount, day}]->(Account)

Run: python seed.py
"""
import json
import os
import random

from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()
random.seed(42)

GRAPH = "fraudnet"
BATCH = 500


def connect():
    return FalkorDB(
        host=os.getenv("FALKORDB_HOST"),
        port=int(os.getenv("FALKORDB_PORT")),
        username=os.getenv("FALKORDB_USERNAME"),
        password=os.getenv("FALKORDB_PASSWORD"),
        ssl=os.getenv("FALKORDB_SSL", "false").lower() == "true",
        socket_connect_timeout=10,
        socket_timeout=60,
    )


def run_batches(g, query, rows):
    for i in range(0, len(rows), BATCH):
        g.query(query, {"rows": rows[i : i + BATCH]})


def main():
    db = connect()
    g = db.select_graph(GRAPH)
    try:
        g.delete()
    except Exception:
        pass
    g = db.select_graph(GRAPH)

    accounts, devices, ips = {}, set(), set()
    uses, logged, sent = [], [], []
    truth = {"rings": {}, "decoys": {}}

    def add_account(aid, age):
        accounts[aid] = age

    # --- 1. Normal accounts: own device, mostly own IP, a few transfers
    normal = []
    for i in range(400):
        aid = f"A{i:04d}"
        add_account(aid, random.randint(120, 2500))
        normal.append(aid)
        d = f"D{i:04d}"
        devices.add(d)
        uses.append({"a": aid, "d": d})
        ip = f"IP{random.randint(0, 600):04d}"
        ips.add(ip)
        logged.append({"a": aid, "i": ip})

    for _ in range(900):
        s, t = random.sample(normal, 2)
        sent.append({"s": s, "t": t, "amt": random.randint(200, 20000), "day": random.randint(1, 60)})

    # --- 2. Decoy A: family of 4 sharing one device (benign)
    fam = normal[10:14]
    uses = [u for u in uses if u["a"] not in fam]
    for a in fam:
        uses.append({"a": a, "d": "D_FAMILY"})
    devices.add("D_FAMILY")
    truth["decoys"]["family_shared_device"] = fam

    # --- 3. Decoy B: corporate IP shared by 40 normal accounts (supernode)
    corp = normal[100:140]
    logged = [l for l in logged if l["a"] not in corp]
    for a in corp:
        logged.append({"a": a, "i": "IP_CORP"})
    ips.add("IP_CORP")
    truth["decoys"]["corporate_ip"] = {"ip": "IP_CORP", "n": len(corp)}

    # --- 4. Planted fraud rings
    for r in range(3):
        n_members = random.randint(6, 8)
        members = [f"R{r}M{k:02d}" for k in range(n_members)]
        mule = f"R{r}MULE"
        cashout = f"R{r}CASH"
        ring_devs = [f"D_R{r}_{k}" for k in range(2)]
        ring_ips = [f"IP_R{r}_{k}" for k in range(2)]
        for a in members + [mule, cashout]:
            add_account(a, random.randint(1, 20))  # very new accounts
        for d in ring_devs:
            devices.add(d)
        for ip in ring_ips:
            ips.add(ip)
        for a in members + [mule]:
            for d in random.sample(ring_devs, random.randint(1, 2)):
                uses.append({"a": a, "d": d})
            logged.append({"a": a, "i": random.choice(ring_ips)})
        # fan-in: members -> mule in small rapid transfers, then mule -> cashout
        day0 = random.randint(40, 55)
        for a in members:
            for _ in range(random.randint(2, 4)):
                sent.append({"s": a, "t": mule, "amt": random.randint(900, 4900), "day": day0 + random.randint(0, 3)})
        sent.append({"s": mule, "t": cashout, "amt": random.randint(25000, 60000), "day": day0 + 4})
        # a few victims pay into ring members
        for a in random.sample(members, 3):
            sent.append({"s": random.choice(normal), "t": a, "amt": random.randint(1000, 8000), "day": day0 - 1})
        truth["rings"][f"ring_{r}"] = {"members": members, "mule": mule, "cashout": cashout}

    # --- 5. Write to graph
    g.query("CREATE INDEX FOR (a:Account) ON (a.id)")
    g.query("CREATE INDEX FOR (d:Device) ON (d.id)")
    g.query("CREATE INDEX FOR (i:IP) ON (i.id)")

    run_batches(g, "UNWIND $rows AS r CREATE (:Account {id:r.id, age_days:r.age})",
                [{"id": k, "age": v} for k, v in accounts.items()])
    run_batches(g, "UNWIND $rows AS r CREATE (:Device {id:r.id})", [{"id": d} for d in devices])
    run_batches(g, "UNWIND $rows AS r CREATE (:IP {id:r.id})", [{"id": i} for i in ips])
    run_batches(g, "UNWIND $rows AS r MATCH (a:Account {id:r.a}), (d:Device {id:r.d}) CREATE (a)-[:USES]->(d)", uses)
    run_batches(g, "UNWIND $rows AS r MATCH (a:Account {id:r.a}), (i:IP {id:r.i}) CREATE (a)-[:LOGGED_FROM]->(i)", logged)
    run_batches(g, "UNWIND $rows AS r MATCH (a:Account {id:r.s}), (b:Account {id:r.t}) "
                   "CREATE (a)-[:SENT {amount:r.amt, day:r.day}]->(b)", sent)

    with open("ground_truth.json", "w") as f:
        json.dump(truth, f, indent=2)

    alert = truth["rings"]["ring_0"]["members"][0]
    print(f"Accounts={len(accounts)} Devices={len(devices)} IPs={len(ips)} Transfers={len(sent)}")
    print(f"Ground truth saved to ground_truth.json. Demo alert account: {alert}")


if __name__ == "__main__":
    main()
