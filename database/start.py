import os
#
import yaml
from py2neo import neo4j
from py2neo.packages.urimagic import URI
from py2neo.neo4j import GraphDatabaseService, CypherQuery

def relpath (path):
    return os.path.join(os.path.dirname(__file__), path)

def ENV ():
    with open(relpath('config.yaml'), 'r') as ENV_file:
        ENV = yaml.load(ENV_file)
    for k, v in ENV.items():
        try:
            os.environ[str(k)]
        except KeyError:
            os.environ[str(k)] = v
            #print(' * adding '+str(k)+' to environment')

class database (object):
    def __init__ (self):
        ENV()
        graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
        service_root = neo4j.ServiceRoot(URI(graphenedb_url).resolve("/"))
        graph_db = service_root.graph_db
        print(graph_db.neo4j_version)
        self.db = graph_db

if __name__ == "__main__":
    from py2neo import node, rel
    db = database().db
    print(db.create(node(name="Bruce Willis", type="throwaway")))
