import operator
from itertools import chain, izip_longest, starmap


class SolrResults(object):
    def __init__(self, query, raw_results):
        self.query = query
        self.searcher = self.query.searcher
        self.raw_results = raw_results
        self.ndocs = self.hits = self.raw_results.hits
        self.docs = []
        self.facet_fields = self.query._facet_fields
        self.facet_queries = self.query._facet_queries
        self.facet_dates = self.query._facet_dates
        self.facet_ranges = self.query._facet_ranges
        self.facet_pivots = self.query._facet_pivots
        self.stats_fields = self.query._stats_fields
        self.groupeds = self.query._groupeds

        for facet in chain(self.facet_fields, self.facet_queries,
                           self.facet_dates, self.facet_ranges,
                           self.facet_pivots):
            facet.process_data(self)
        
        for grouped in self.groupeds:
            grouped.process_data(self)

        for stats in self.stats_fields:
            stats.process_data(self)
        
        for raw_doc in self.raw_results.docs:
            doc = self.searcher.document_cls(_results=self, **raw_doc)
            self.docs.append(doc)

        self.debug_info = self.raw_results.debug

    def get_grouped(self, key):
        for grouped in self.groupeds:
            if grouped.field == key:
                return grouped

    def get_stats_field(self, field):
        for st in self.stats_fields:
            if st.field == field:
                return st
        
    def get_facet_field(self, key):
        for facet in self.facet_fields:
            if facet.key == key:
                return facet

    def get_facet_pivot(self, key):
        for facet in self.facet_pivots:
            if facet.key == key:
                return facet

    def _populate_instances(self):
        all_docs = []
        for doc in self.docs:
            all_docs.append(doc)
        for grouped in self.groupeds:
            for group in grouped.groups:
                for doc in group.docs:
                    all_docs.append(doc)
            for doc in grouped.docs:
                all_docs.append(doc)

        ids = [doc.id for doc in all_docs]
        if self.query._instance_mapper:
            instances = self.query._instance_mapper(
                ids, db_query=self.query._db_query)
        else:
            instances = self.searcher.instance_mapper(
                ids, db_query=self.query._db_query)

        for doc in all_docs:
            doc._instance = instances.get(doc.id)

    @property
    def instances(self):
        return [doc.instance for doc in self if doc.instance]
