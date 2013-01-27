#!/usr/bin env python

from tests.unit import unittest
from httpretty import HTTPretty

import urlparse
import json

from boto.cloudsearch.document import DocumentServiceConnection

class CloudSearchDocumentTest(unittest.TestCase):
    def setUp(self):
        HTTPretty.enable()
        HTTPretty.register_uri(HTTPretty.POST, "http://doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com/2011-02-01/documents/batch",
            body=json.dumps(self.response),
            content_type="application/json")

    def tearDown(self):
        HTTPretty.disable()

class CloudSearchDocumentSingleTest(CloudSearchDocumentTest):

    response = {
        'status': 'success',
        'adds': 1,
        'deletes': 0,
    }

    def test_cloudsearch_add_basics(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        document.add("1234", 10, {"id": "1234", "title": "Title 1", "category": ["cat_a", "cat_b", "cat_c"]})
        document.commit()

        args = json.loads(HTTPretty.last_request.body)[0]

        self.assertEqual(args['lang'], 'en')
        self.assertEqual(args['type'], 'add')

    def test_cloudsearch_add_single_basic(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        document.add("1234", 10, {"id": "1234", "title": "Title 1", "category": ["cat_a", "cat_b", "cat_c"]})
        document.commit()

        args = json.loads(HTTPretty.last_request.body)[0]

        self.assertEqual(args['id'], '1234')
        self.assertEqual(args['version'], 10)
        self.assertEqual(args['type'], 'add')

    def test_cloudsearch_add_single_fields(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        document.add("1234", 10, {"id": "1234", "title": "Title 1", "category": ["cat_a", "cat_b", "cat_c"]})
        document.commit()

        args = json.loads(HTTPretty.last_request.body)[0]

        self.assertEqual(args['fields']['category'], ['cat_a', 'cat_b', 'cat_c'])
        self.assertEqual(args['fields']['id'], '1234')
        self.assertEqual(args['fields']['title'], 'Title 1')

    def test_cloudsearch_add_single_result(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        document.add("1234", 10, {"id": "1234", "title": "Title 1", "category": ["cat_a", "cat_b", "cat_c"]})
        doc = document.commit()

        self.assertEqual(doc.status, 'success')
        self.assertEqual(doc.adds, 1)
        self.assertEqual(doc.deletes, 0)

        self.assertEqual(doc.doc_service, document)

class CloudSearchDocumentMultipleAddTest(CloudSearchDocumentTest):

    response = {
        'status': 'success',
        'adds': 3,
        'deletes': 0,
    }
    
    objs = {
        '1234': {'version': 10, 'fields': {"id": "1234", "title": "Title 1", "category": ["cat_a", "cat_b", "cat_c"]}},
        '1235': {'version': 11, 'fields': {"id": "1235", "title": "Title 2", "category": ["cat_b", "cat_c", "cat_d"]}},
        '1236': {'version': 12, 'fields': {"id": "1236", "title": "Title 3", "category": ["cat_e", "cat_f", "cat_g"]}},
        }


    def test_cloudsearch_add_basics(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        for (key, obj) in self.objs.items():
            document.add(key, obj['version'], obj['fields'])
        document.commit()

        args = json.loads(HTTPretty.last_request.body)

        for arg in args:
            self.assertTrue(arg['id'] in self.objs)
            self.assertEqual(arg['version'], self.objs[arg['id']]['version'])
            self.assertEqual(arg['fields']['id'], self.objs[arg['id']]['fields']['id'])
            self.assertEqual(arg['fields']['title'], self.objs[arg['id']]['fields']['title'])
            self.assertEqual(arg['fields']['category'], self.objs[arg['id']]['fields']['category'])

    def test_cloudsearch_add_links(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        for (key, obj) in self.objs.items():
            document.add(key, obj['version'], obj['fields'])
        doc = document.commit()

        self.assertEqual(doc.status, 'success')
        self.assertEqual(doc.adds, len(self.objs))
        self.assertEqual(doc.deletes, 0)

class CloudSearchDocumentDelete(CloudSearchDocumentTest):

    response = {
        'status': 'success',
        'adds': 0,
        'deletes': 1,
    }

    def test_cloudsearch_delete(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        document.delete("5", "10")
        document.commit()
        args = json.loads(HTTPretty.last_request.body)[0]

        self.assertEqual(args['version'], '10')
        self.assertEqual(args['type'], 'delete')
        self.assertEqual(args['id'], '5')

    def test_cloudsearch_delete_results(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        document.delete("5", "10")
        doc = document.commit()

        self.assertEqual(doc.status, 'success')
        self.assertEqual(doc.adds, 0)
        self.assertEqual(doc.deletes, 1)

class CloudSearchDocumentDeleteMultiple(CloudSearchDocumentTest):
    response = {
        'status': 'success',
        'adds': 0,
        'deletes': 2,
    }

    def test_cloudsearch_delete_multiples(self):
        document = DocumentServiceConnection(endpoint="doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        document.delete("5", "10")
        document.delete("6", "11")
        document.commit()
        args = json.loads(HTTPretty.last_request.body)

        for arg in args:
            self.assertTrue(arg, True)
