from flask import url_for
import lxml.html
from databasyfacade.db import models
from databasyfacade.db.models import ModelRole
from databasyfacade.services import models_service
from databasyfacade.testing import DatabasyTest, fixtures
from databasyfacade.testing.testdata import UserData, ProfileData, ModelInfoData, ModelRoleData

__author__ = 'Marboni'

class ModelsTest(DatabasyTest):
    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData)
    def test_empty_dashboard(self, data):
        self.login(UserData.third)
        response = self.client.get(url_for('root.home'))
        self.assert_200(response)
        self.assertTrue('You have no models yet.' in response.data)

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData)
    def test_dashboard_with_models(self, data):
        self.login(UserData.first)
        response = self.client.get(url_for('root.home'))
        self.assert_200(response)
        html = lxml.html.fromstring(response.data)

        ##### Own models #####
        own_model_rows = html.xpath('//table[@id="ownModels"]//tr')
        self.assertEqual(1, len(own_model_rows))

        own_model_row = own_model_rows[0]
        own_model_cells = own_model_row.findall('td')
        self.assertEqual(2, len(own_model_cells))

        model_name_and_desc_cell = own_model_cells[0]
        # Model link.
        model_link = model_name_and_desc_cell.find('a')
        self.assertEqual(ModelInfoData.model_a.schema_name, model_link.text)
        self.assertEqual(url_for('models.model', model_id=ModelInfoData.model_a.id), model_link.attrib.get('href'))
        # Model description.
        model_desc = model_name_and_desc_cell.find('em')
        self.assertEqual(ModelInfoData.model_a.description, model_desc.text)

        model_links_cell = own_model_cells[1]
        actions_div = model_links_cell.find_class('modelActions')[0]
        properties_link = actions_div.xpath('a[contains(@class,"modelProperties")]')[0]
        self.assertEqual(url_for('models.properties', model_id=ModelInfoData.model_a.id), properties_link.attrib.get('href'))
        delete_link = actions_div.xpath('a[contains(@class,"deleteModel")]')[0]
        self.assertEqual(ModelInfoData.model_a.schema_name, delete_link.attrib.get('data-schemaname'))
        self.assertEqual(str(ModelInfoData.model_a.id), delete_link.attrib.get('data-modelid'))


        ##### Shared models #####
        shared_model_rows = html.xpath('//table[@id="sharedModels"]//tr')
        self.assertEqual(1, len(shared_model_rows))

        shared_model_row = shared_model_rows[0]
        shared_model_cells = shared_model_row.findall('td')
        self.assertEqual(1, len(shared_model_cells))

        model_name_and_desc_cell = shared_model_cells[0]
        # Model link.
        model_link = model_name_and_desc_cell.find('a')
        self.assertEqual(ModelInfoData.model_b.schema_name, model_link.text)
        self.assertEqual(url_for('models.model', model_id=ModelInfoData.model_b.id), model_link.attrib.get('href'))
        # Model description.
        model_desc = model_name_and_desc_cell.find('em')
        self.assertEqual(ModelInfoData.model_b.description, model_desc.text)

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData)
    def test_new_model(self, data):
        self.login(UserData.third)

        db_type = models.DB_TYPES[0][0]
        response = self.client.post(url_for('models.new_model'), data={
            'schema_name': 'Schema',
            'description': 'Schema description',
            'database_type': db_type
        })
        self.assertRedirects(response, url_for('root.home'))
        roles = models_service.user_roles(UserData.third.id)
        self.assertEqual(1, len(roles))

        owner_role = roles[0]
        self.assertEqual(ModelRole.OWNER, owner_role.role)
        model = owner_role.model
        self.assertEqual('Schema', model.schema_name)
        self.assertEqual('Schema description', model.description)
        self.assertEqual(db_type, model.database_type)

