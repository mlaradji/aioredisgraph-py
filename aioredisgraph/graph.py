from .util import *
from .query_result import QueryResult
class Graph(object):
    """
    Graph, collection of nodes and edges.
    """

    def __init__(self, name, redis_con):
        """
        Create a new graph.
        """
        self.name = name
        self.redis_con = redis_con
        self.nodes = {}
        self.edges = []
        self._labels = []            # List of node labels.
        self._properties = []        # List of properties.
        self._relationshipTypes = [] # List of relation types.

    async def get_label(self, idx):
        try:
            label = self._labels[idx]
        except IndexError:
            # Refresh graph labels.
            lbls = await self.labels()
            # Unpack data.
            self._labels = [None] * len(lbls)
            for i, l in enumerate(lbls):
                self._labels[i] = l[0]

            label = self._labels[idx]
        return label

    async def get_relation(self, idx):
        try:
            relationshipType = self._relationshipTypes[idx]
        except IndexError:
            # Refresh graph relations.
            rels = await self.relationshipTypes()
            # Unpack data.
            self._relationshipTypes = [None] * len(rels)
            for i, r in enumerate(rels):
                self._relationshipTypes[i] = r[0]

            relationshipType = self._relationshipTypes[idx]
        return relationshipType

    async def get_property(self, idx):
        try:
            propertie = self._properties[idx]
        except IndexError:
            # Refresh properties.
            props = await self.propertyKeys()
            # Unpack data.
            self._properties = [None] * len(props)
            for i, p in enumerate(props):
                self._properties[i] = p[0]

            propertie = self._properties[idx]
        return propertie

    def add_node(self, node):
        """
        Adds a node to the graph.
        """
        if node.alias is None:
            node.alias = random_string()
        self.nodes[node.alias] = node

    def add_edge(self, edge):
        """
        Addes an edge to the graph.
        """

        # Make sure edge both ends are in the graph
        assert self.nodes[edge.src_node.alias] is not None and self.nodes[edge.dest_node.alias] is not None
        self.edges.append(edge)

    def commit(self):
        """
        Create entire graph.
        """
        if len(self.nodes) == 0 and len(self.edges) == 0:
            return None

        query = 'CREATE '
        for _, node in self.nodes.items():
            query += str(node) + ','

        query += ','.join([str(edge) for edge in self.edges])

        # Discard leading comma.
        if query[-1] is ',':
            query = query[:-1]

        return self.query(query)

    async def flush(self):
        """
        Commit the graph and reset the edges and nodes to zero length
        """
        await self.commit()
        self.nodes = {}
        self.edges = []

    def build_params_header(self, params):
        assert type(params) == dict
        # Header starts with "CYPHER"
        params_header = "CYPHER "
        for key, value in params.items():
            # If value is string add quotation marks.
            if type(value) == str:
                value = quote_string(value)
            # Value is None, replace with "null" string.
            elif value is None:
                value = "null"
            params_header += str(key) + "=" + str(value) + " "
        return params_header

    async def query(self, q, params=None):
        """
        Executes a query against the graph.
        """
        if params is not None:
            q = self.build_params_header(params) + q

        statistics = None
        result_set = None

        response = await self.redis_con.execute("GRAPH.QUERY", self.name, q, "--compact")
        return QueryResult(self, response)

    def _execution_plan_to_string(self, plan):
        return "\n".join(plan)

    async def execution_plan(self, query):
        """
        Get the execution plan for given query,
        GRAPH.EXPLAIN returns an array of operations.
        """
        plan = await self.redis_con.execute("GRAPH.EXPLAIN", self.name, query)
        return self._execution_plan_to_string(plan)

    async def delete(self):
        """
        Deletes graph.
        """
        return await self.redis_con.execute("GRAPH.DELETE", self.name)
    
    def merge(self, pattern):
        """
        Merge pattern.
        """

        query = 'MERGE '
        query += str(pattern)

        return self.query(query)

    # Procedures.
    def call_procedure(self, procedure, *args, **kwagrs):
        args = [quote_string(arg) for arg in args]
        q = 'CALL %s(%s)' % (procedure, ','.join(args))

        y = kwagrs.get('y', None)
        if y:
            q += ' YIELD %s' % ','.join(y)

        return self.query(q)

    async def labels(self):
        return (await self.call_procedure("db.labels")).result_set

    async def relationshipTypes(self):
        return (await self.call_procedure("db.relationshipTypes")).result_set

    async def propertyKeys(self):
        return (await self.call_procedure("db.propertyKeys")).result_set
