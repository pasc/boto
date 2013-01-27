#!/usr/bin env python

from tests.unit import unittest
from httpretty import HTTPretty
import urlparse

import boto.cloudsearch
from boto.cloudsearch.domain import Domain

class CloudSearchConnectionTest(unittest.TestCase):

    def setUp(self):
        HTTPretty.enable()
        HTTPretty.register_uri(HTTPretty.POST, "https://cloudsearch.us-east-1.amazonaws.com/",
            body=CREATE_DOMAIN_XML,
            content_type="text/xml")

    def tearDown(self):
        HTTPretty.disable()

    def test_cloudsearch_connection(self):
        conn = boto.cloudsearch.connect_to_region("us-east-1", aws_access_key_id='key_id', aws_secret_access_key='access_key')
        domain = Domain(conn, conn.create_domain('demo'))

        args = urlparse.parse_qs(HTTPretty.last_request.body)
        
        self.assertEqual(args['AWSAccessKeyId'], ['key_id'])
        self.assertEqual(args['Action'], ['CreateDomain'])
        self.assertEqual(args['DomainName'], ['demo'])

    def test_cloudsearch_connect_result_endpoints(self):
        conn = boto.cloudsearch.connect_to_region("us-east-1", aws_access_key_id='key_id', aws_secret_access_key='access_key')
        domain = Domain(conn, conn.create_domain('demo'))

        self.assertEqual(domain.doc_service_arn, "arn:aws:cs:us-east-1:1234567890:doc/demo")
        self.assertEqual(domain.doc_service_endpoint, "doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")
        self.assertEqual(domain.search_service_arn, "arn:aws:cs:us-east-1:1234567890:search/demo")
        self.assertEqual(domain.search_service_endpoint, "search-demo-userdomain.us-east-1.cloudsearch.amazonaws.com")

    def test_cloudsearch_connect_result_statuses(self):
        conn = boto.cloudsearch.connect_to_region("us-east-1", aws_access_key_id='key_id', aws_secret_access_key='access_key')
        domain = Domain(conn, conn.create_domain('demo'))

        self.assertEqual(domain.created, True)
        self.assertEqual(domain.processing, False)
        self.assertEqual(domain.requires_index_documents, False)

    def test_cloudsearch_connect_result_details(self):
        conn = boto.cloudsearch.connect_to_region("us-east-1", aws_access_key_id='key_id', aws_secret_access_key='access_key')
        domain = Domain(conn, conn.create_domain('demo'))

        self.assertEqual(domain.id, "1234567890/demo")
        self.assertEqual(domain.name, "demo")

CREATE_DOMAIN_XML="""
<CreateDomainResponse xmlns="http://cloudsearch.amazonaws.com/doc/2011-02-01">
  <CreateDomainResult>
    <DomainStatus>
      <SearchPartitionCount>0</SearchPartitionCount>
      <SearchService>
        <Arn>arn:aws:cs:us-east-1:1234567890:search/demo</Arn>
        <Endpoint>search-demo-userdomain.us-east-1.cloudsearch.amazonaws.com</Endpoint>
      </SearchService>
      <NumSearchableDocs>0</NumSearchableDocs>
      <Created>true</Created>
      <DomainId>1234567890/demo</DomainId>
      <Processing>false</Processing>
      <SearchInstanceCount>0</SearchInstanceCount>
      <DomainName>demo</DomainName>
      <RequiresIndexDocuments>false</RequiresIndexDocuments>
      <Deleted>false</Deleted>
      <DocService>
        <Arn>arn:aws:cs:us-east-1:1234567890:doc/demo</Arn>
        <Endpoint>doc-demo-userdomain.us-east-1.cloudsearch.amazonaws.com</Endpoint>
      </DocService>
    </DomainStatus>
  </CreateDomainResult>
  <ResponseMetadata>
    <RequestId>00000000-0000-0000-0000-000000000000</RequestId>
  </ResponseMetadata>
</CreateDomainResponse>
"""

