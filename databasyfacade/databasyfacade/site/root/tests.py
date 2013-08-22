from flask import url_for
import lxml.html
from databasyfacade.testing import DatabasyTest

__author__ = 'Marboni'

class RootTest(DatabasyTest):
    def test_root(self):
        response = self.client.get(url_for('root.home'))
        self.assert200(response)
        html = lxml.html.fromstring(response.data)
        login_links = html.xpath('//a[@href="%s"]' % url_for('auth.login'))
        self.assertTrue(login_links)