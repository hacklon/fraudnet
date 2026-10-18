
from seed import connect, GRAPH

db = connect()
try:
    graph = db.select_graph(GRAPH)

    result = graph.query("""
    MATCH (a:Account)
    RETURN count(a) AS accounts
    """)

    print("Accounts in FalkorDB:", result.result_set)

    result = graph.query("""
    MATCH (a:Account)-[r:SENT]->(b:Account)
    RETURN count(r) AS transfers
    """)

    print("Transfers in FalkorDB:", result.result_set)

    result = graph.query("""
    MATCH (a:Account)-[:SENT]->(m:Account)-[:SENT]->(c:Account)
    WHERE m.id CONTAINS 'MULE'
      AND c.id CONTAINS 'CASH'
    RETURN a.id, m.id, c.id
    LIMIT 10
    """)

    print("Potential mule-to-cashout paths:", result.result_set)
finally:
    pass
