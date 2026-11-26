"""Exact stored node and edge properties, from fixed Cypher queries."""
NODE_FIELDS={"Customer":["id"],"Touchpoint":["id","at"],"Campaign":["id","name","channel","spend"],"Product":["id","name","price","cost","stock"],"Order":["id","at","revenue"]}
RELATIONSHIPS=[("Customer","HAS_TOUCH","Touchpoint"),("Touchpoint","FROM_CAMPAIGN","Campaign"),("Campaign","PROMOTES","Product"),("Customer","PLACED","Order"),("Order","CONTAINS","Product")]
NODE_QUERIES={label:"MATCH (n:"+label+") RETURN "+", ".join("n."+f+" AS "+f for f in fields)+" ORDER BY id" for label,fields in NODE_FIELDS.items()}
EDGE_QUERIES={rel:f"MATCH (a:{a})-[:{rel}]->(b:{b}) RETURN a.id AS source, b.id AS target ORDER BY source, target" for a,rel,b in RELATIONSHIPS}

def network(db):
    nodes=[]
    edges=[]
    for label,query in NODE_QUERIES.items():
        for row in db.execute(query):
            p=dict(row)
            nodes.append({"id":p["id"],"type":label,"properties":p})
    for a,rel,b in RELATIONSHIPS:
        for row in db.execute(EDGE_QUERIES[rel]):
            edges.append({"source":row["source"],"target":row["target"],"type":rel})
    return {"nodes":nodes,"edges":edges,"queries":list(NODE_QUERIES.values())+list(EDGE_QUERIES.values())}
