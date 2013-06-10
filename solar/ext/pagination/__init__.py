# coding: utf-8
from __future__ import unicode_literals


class SolrQueryWrapper(object):
    """Solr returns total count with response.
    So we can get documents and count with one request.
    """
    def __init__(self, query, grouped_by=None):
        self.query = query
        self.grouped_by = grouped_by
        self.sliced_query = None
        self.items = None
        self.count = None

    def __getitem__(self, range):
        if not isinstance(range, slice):
            raise ValueError('__getitem__ without slicing not supported')
        self.sliced_query = self.query[range]
        if self.grouped_by:
            grouped = self.sliced_query.results.get_grouped(self.grouped_by)
            self.items = grouped.groups
            self.count = grouped.ngroups
        else:
            self.items = list(self.sliced_query)
            self.count = len(self.sliced_query)
        return self.items

    def __iter__(self):
        if self.items is None:
            raise ValueError('Slice first')
        return iter(self.items)
    
    def __len__(self):
        if self.count is None:
            raise ValueError('Slice first')
        return self.count

    @property
    def results(self):
        if self.sliced_query is None:
            raise ValueError('Slice first')
        return self.sliced_query.results
