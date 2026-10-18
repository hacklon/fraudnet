from graph_store import connect_graph


def investigate(account_id: str):
    """Investigate an account using live FalkorDB queries and return evidence."""
    client, graph = connect_graph()
    try:
        account_result = graph.query(
            """
            MATCH (a:Account {id: $account_id})
            RETURN a.id, a.age_days
            """,
            {"account_id": account_id},
        )
        if not account_result.result_set:
            return {"account_id": account_id, "error": "Account not found in FalkorDB."}

        account_id, age_days = account_result.result_set[0]

        device_result = graph.query(
            """
            MATCH (a:Account {id: $account_id})-[:USES]->(d:Device)
                  <-[:USES]-(other:Account)
            WHERE other.id <> $account_id
            RETURN d.id, count(DISTINCT other) AS shared_count,
                   collect(DISTINCT other.id)[0..10] AS accounts
            """,
            {"account_id": account_id},
        )
        ip_result = graph.query(
            """
            MATCH (a:Account {id: $account_id})-[:LOGGED_FROM]->(ip:IP)
                  <-[:LOGGED_FROM]-(other:Account)
            WHERE other.id <> $account_id
            RETURN ip.id, count(DISTINCT other) AS shared_count,
                   collect(DISTINCT other.id)[0..10] AS accounts
            """,
            {"account_id": account_id},
        )
        outgoing_result = graph.query(
            """
            MATCH (a:Account {id: $account_id})-[r:SENT]->(b:Account)
            RETURN b.id, r.amount, r.day
            ORDER BY r.day
            LIMIT 100
            """,
            {"account_id": account_id},
        )
        flow_result = graph.query(
            """
            MATCH (a:Account {id: $account_id})-[r1:SENT]->(m:Account)-[r2:SENT]->(c:Account)
            WHERE m.id CONTAINS 'MULE' AND c.id CONTAINS 'CASH'
            RETURN a.id, m.id, c.id, r1.amount, r2.amount, r1.day, r2.day
            ORDER BY r1.day
            LIMIT 50
            """,
            {"account_id": account_id},
        )

        devices = [
            {"id": row[0], "shared_count": row[1], "accounts": row[2]}
            for row in device_result.result_set
        ]
        ips = [
            {"id": row[0], "shared_count": row[1], "accounts": row[2]}
            for row in ip_result.result_set
        ]
        outgoing = [
            {"to": row[0], "amount": row[1], "day": row[2]}
            for row in outgoing_result.result_set
        ]
        flows = [
            {
                "source": row[0],
                "mule": row[1],
                "cashout": row[2],
                "to_mule_amount": row[3],
                "to_cashout_amount": row[4],
                "first_day": row[5],
                "cashout_day": row[6],
            }
            for row in flow_result.result_set
        ]

        # Transparent demo heuristic, not a calibrated probability or trained model.
        score = 0
        reasons = []
        warnings = []

        if age_days is not None and age_days <= 30:
            score += 20
            reasons.append("+20: account is 30 days old or newer")

        if flows:
            score += 50
            reasons.append("+50: account has a graph path to a mule and cashout")

        # Shared infrastructure only adds support when a suspicious flow exists.
        if flows and any(1 <= item["shared_count"] <= 10 for item in devices):
            score += 10
            reasons.append("+10: shared device supports the transfer-path evidence")

        if flows and any(1 <= item["shared_count"] <= 10 for item in ips):
            score += 10
            reasons.append("+10: shared IP supports the transfer-path evidence")

        if any(item["shared_count"] >= 20 for item in ips):
            warnings.append(
                "A high-degree shared IP may be corporate/public infrastructure; do not treat it alone as fraud evidence."
            )
        if (devices or ips) and not flows:
            warnings.append(
                "Shared devices/IPs without a suspicious transfer path are weak signals and may be benign."
            )

        score = min(score, 100)
        risk_level = "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"

        if not reasons:
            reasons.append("No strong signals found by the current demo rules.")

        return {
            "account_id": account_id,
            "age_days": age_days,
            "risk_score": score,
            "risk_level": risk_level,
            "reasons": reasons,
            "warnings": warnings,
            "shared_devices": devices,
            "shared_ips": ips,
            "outgoing_transfers": outgoing,
            "transfer_flow": flows,
            "graph_name": "fraudnet",
        }
    finally:
        # The installed FalkorDB client has no close() method in this environment.
        pass
