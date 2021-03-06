# -*- coding: utf-8 -*-
from pyes.tests import ESTestCase
from pyes.query import MatchAllQuery, Search

class ResultsetTestCase(ESTestCase):
    def setUp(self):
        super(ResultsetTestCase, self).setUp()
        self.init_default_index()

        for i in range(1000):
            self.conn.index(
                    {"name": "Joe Tester%d" % i, "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": i},
                self.index_name, self.document_type, i, bulk=True)
        self.conn.indices.refresh(self.index_name)

    def test_iterator(self):
        resultset = self.conn.search(Search(MatchAllQuery(), size=20), self.index_name, self.document_type)
        self.assertEqual(len([p for p in resultset]), 20)
        resultset = self.conn.search(Search(MatchAllQuery(), size=10), self.index_name, self.document_type)
        self.assertEqual(len([p for p in resultset[:10]]), 10)
        self.assertEqual(resultset[10].uuid, "11111")
        self.assertEqual(resultset.total, 1000)

    def test_iterator_offset(self):
        # Query for a block of 10, starting at position 10:
        #
        resultset = self.conn.search(Search(MatchAllQuery(), start=10, size=10, sort={'position': {'order': 'asc'}}),
            self.index_name, self.document_type,
            start=10, size=10)

        self.assertGreater(resultset.took, 0.0)
        # Ensure that there are 1000 results:
        #
        self.assertEqual(len(resultset), 1000)

        # Now check that we actually have records 10-19, rather than 0-9:
        #
        position = 0
        for r in resultset:
            self.assertEqual(r.position, position + 10)
            position += 1

        range = resultset[0:1]
        self.assertEqual(len(range), 1)
        self.assertEqual(range[0].position, 10)
        range = resultset[1:1]
        self.assertEqual(len(range), 0)

        range = resultset[9:10]
        self.assertEqual(len(range), 1)
        self.assertEqual(range[0].position, 19)


if __name__ == "__main__":
    import unittest
    unittest.main()