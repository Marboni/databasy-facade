from databasyfacade.testing import DatabasyTest

__author__ = 'Marboni'

class RootTest(DatabasyTest):
    def test_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
