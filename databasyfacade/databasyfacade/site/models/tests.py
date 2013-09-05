from flask import url_for
import lxml.html
from sqlalchemy.orm.exc import NoResultFound
from databasyfacade.db import models
from databasyfacade.db.models import ModelRole
from databasyfacade.services import models_service
from databasyfacade.testing import DatabasyTest, fixtures
from databasyfacade.testing.testdata import UserData, ProfileData, ModelInfoData, ModelRoleData, InvitationData

__author__ = 'Marboni'

class ModelsTest(DatabasyTest):
    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData)
    def test_empty_dashboard(self, data):
        self.login(UserData.third)
        response = self.client.get(url_for('root.home'))
        self.assert_200(response)
        self.assertTrue('You have no models yet.' in response.data)

        html = lxml.html.fromstring(response.data)
        user_menu = html.xpath('//li[@id="userMenu"]')[0]
        user_menu_label = user_menu.xpath('./a')[0]
        self.assertEqual(user_menu_label.text.strip(), UserData.third.username)

        self.assertTrue(user_menu.xpath('.//a[@href="%s"]' % url_for('auth.change_password')))
        self.assertTrue(user_menu.xpath('.//a[@href="%s"]' % url_for('auth.logout')))

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
        self.assertEqual(ModelInfoData.model_a.schema_name, model_link.text_content())
        self.assertEqual(url_for('models.model', model_id=ModelInfoData.model_a.id), model_link.attrib.get('href'))
        # Model description.
        model_desc = model_name_and_desc_cell.find('em')
        self.assertEqual(ModelInfoData.model_a.description, model_desc.text)

        model_links_cell = own_model_cells[1]
        actions_div = model_links_cell.find_class('ownModelActions')[0]
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
        self.assertEqual(2, len(shared_model_cells))

        model_name_and_desc_cell = shared_model_cells[0]
        # Model link.
        model_link = model_name_and_desc_cell.find('a')
        self.assertEqual(ModelInfoData.model_b.schema_name, model_link.text_content())
        self.assertEqual(url_for('models.model', model_id=ModelInfoData.model_b.id), model_link.attrib.get('href'))
        # Model description.
        model_desc = model_name_and_desc_cell.find('em')
        self.assertEqual(ModelInfoData.model_b.description, model_desc.text)

        model_links_cell = shared_model_cells[1]
        actions_div = model_links_cell.find_class('sharedModelActions')[0]
        properties_link = actions_div.xpath('a[contains(@class,"modelProperties")]')[0]
        self.assertEqual(url_for('models.properties', model_id=ModelInfoData.model_b.id), properties_link.attrib.get('href'))
        give_up_link = actions_div.xpath('a[contains(@class,"giveUp")]')[0]
        self.assertEqual(ModelInfoData.model_b.schema_name, give_up_link.attrib.get('data-schemaname'))
        self.assertEqual(str(ModelInfoData.model_b.id), give_up_link.attrib.get('data-modelid'))


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

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData)
    def test_model_properties(self, data):
        self.login(UserData.first)
        model_id = ModelInfoData.model_b.id

        # Developer can edit.
        response = self.client.get(url_for('models.properties', model_id=model_id))
        self.assert_200(response)
        html = lxml.html.fromstring(response.data)
        self.assertFalse('readonly' in html.xpath('//input[@id="nmf_schema_name"]')[0].attrib)
        self.assertFalse('readonly' in html.xpath('//input[@id="nmf_description"]')[0].attrib)
        self.assertTrue(html.xpath('//form[@id="modelForm"]//button[@type="submit"]'))

        response = self.client.post(url_for('models.properties', model_id=model_id), data={
            'schema_name': 'New name',
            'description': 'New description'
        })
        self.assert_200(response)
        model = models_service.model(model_id)
        self.assertEqual('New name', model.schema_name)
        self.assertEqual('New description', model.description)

        # Viewer can't edit, fields are disabled.
        self.login(UserData.fourth)
        response = self.client.get(url_for('models.properties', model_id=model_id))
        self.assert_200(response)
        html = lxml.html.fromstring(response.data)
        self.assertTrue('readonly' in html.xpath('//input[@id="nmf_schema_name"]')[0].attrib)
        self.assertTrue('readonly' in html.xpath('//input[@id="nmf_description"]')[0].attrib)
        self.assertFalse(html.xpath('//form[@id="modelForm"]//button[@type="submit"]'))

        model_id = ModelInfoData.model_b.id
        response = self.client.post(url_for('models.properties', model_id=model_id), data={
            'schema_name': 'New name',
            'description': 'New description'
        })
        self.assert_401(response)

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData, InvitationData)
    def test_team_for_owner(self, data):
        self.login(UserData.second)

        model_id = ModelInfoData.model_b.id

        response = self.client.get(url_for('models.team', model_id=model_id))
        self.assert_200(response)
        html = lxml.html.fromstring(response.data)

        self.assertTrue(html.xpath('//a[@id="inviteBtn"]'))

        ##### Model members #####
        member_rows = html.xpath('//table[@id="members"]//tbody//tr')
        self.assertEqual(3, len(member_rows))

        owner_row = member_rows[0]
        owner_cells = owner_row.findall('td')
        self.assertEqual(4, len(owner_cells))

        self.assertEqual(UserData.second.username, owner_cells[0].text)
        self.assertEqual(ProfileData.second.email, owner_cells[1].text)
        self.assertTrue('Owner' in owner_cells[2].text_content())
        owner_member_actions = owner_cells[3].xpath('./div[contains(@class, "memberActions")]')[0]
        self.assertFalse(owner_member_actions.xpath('./*'))

        developer_row = member_rows[1]
        developer_cells = developer_row.findall('td')
        self.assertEqual(4, len(developer_cells))
        self.assertEqual(UserData.first.username, developer_cells[0].text)
        self.assertEqual(ProfileData.first.email, developer_cells[1].text)
        selected_role = developer_cells[2].xpath('.//button[@disabled="disabled"]')[0].attrib['data-role']
        self.assertEqual(ModelRoleData.first_developer_model_b.role, selected_role)
        remove_member_action = developer_cells[3].xpath('.//a[contains(@class, "removeMember")]')[0]
        self.assertEqual(url_for('models.remove_member', user_id=ProfileData.first.id, model_id=model_id), remove_member_action.attrib['href'])

        ##### Pending invitations #####
        invitation_rows = html.xpath('//table[@id="invitations"]//tbody//tr')
        self.assertEqual(1, len(invitation_rows))

        invitation_row = invitation_rows[0]
        invitation_cells = invitation_row.findall('td')
        self.assertEqual(3, len(invitation_cells))
        self.assertEqual(InvitationData.invitation.email_lower, invitation_cells[0].text)
        selected_role = invitation_cells[1].xpath('.//button[@disabled="disabled"]')[0].attrib['data-role']
        self.assertEqual(InvitationData.invitation.role, selected_role)
        cancel_invitation_action = invitation_cells[2].xpath('.//a[contains(@class, "cancelInvitation")]')[0]
        self.assertEqual(url_for('models.cancel_invitation', invitation_id=InvitationData.invitation.id, model_id=model_id), cancel_invitation_action.attrib['href'])


    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData, InvitationData)
    def test_team_for_developer(self, data):
        self.login(UserData.first)

        model_id = ModelInfoData.model_b.id

        response = self.client.get(url_for('models.team', model_id=model_id))
        self.assert_200(response)
        html = lxml.html.fromstring(response.data)

        self.assertFalse(html.xpath('//a[@id="inviteBtn"]'))

        ##### Model members #####
        member_rows = html.xpath('//table[@id="members"]//tbody//tr')
        self.assertEqual(3, len(member_rows))

        developer_row = member_rows[1]
        developer_cells = developer_row.findall('td')
        self.assertEqual(4, len(developer_cells))
        self.assertFalse(developer_cells[3].xpath('.//a[contains(@class, "removeMember")]'))

        ##### Pending invitations #####
        invitation_rows = html.xpath('//table[@id="invitations"]//tbody//tr')
        self.assertEqual(1, len(invitation_rows))

        invitation_row = invitation_rows[0]
        invitation_cells = invitation_row.findall('td')
        self.assertEqual(3, len(invitation_cells))
        self.assertFalse(invitation_cells[2].xpath('.//a[contains(@class, "cancelInvitation")]'))


    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData, InvitationData)
    def test_invite(self, data):
        model_id = ModelInfoData.model_b.id

        self.login(UserData.first)
        response = self.client.get(url_for('models.invite', model_id=model_id))
        self.assert_401(response)

        response = self.client.post(url_for('models.invite', model_id=model_id))
        self.assert_401(response)

        self.login(UserData.second)
        guest_email = 'guest@example.com'
        with self.mail.record_messages() as outbox:
            self.client.post(url_for('models.invite', model_id=model_id), data={
                'emails': ', '.join((ProfileData.second.email, InvitationData.invitation.email_lower, ProfileData.third.email,
                                     guest_email)),
                'role': ModelRole.VIEWER
            })
            roles = models_service.model_roles(model_id)
            for role in roles:
                if role.user_id == ProfileData.third.id:
                    self.assertEqual(ModelRole.VIEWER, role.role)
                    break
            else:
                self.fail('Unable to find role for existent user that was invited to the model.')

            invitations = models_service.active_invitations_by_model(model_id)
            self.assertEqual(2, len(invitations))

            guest_invitation = models_service.invitations_by_email(guest_email)[0]
            self.assertEqual(ModelRole.VIEWER, guest_invitation.role)
            self.assertEqual(model_id, guest_invitation.model_id)

            self.wait_letter(outbox, 2, 0.5)
            recipient_letters = {letter.recipients[0]: letter for letter in outbox}

            notification_letter = recipient_letters[ProfileData.third.email]
            content = notification_letter.body
            self.assertTrue(UserData.second.username in content)
            self.assertTrue(UserData.third.username in content)
            self.assertTrue(ModelInfoData.model_b.schema_name in content)
            model_link = self.app.config['ENDPOINT'] + url_for('models.model', model_id=ModelInfoData.model_b.id)
            self.assertTrue(model_link in content)

            invitation_letter = recipient_letters[guest_email]
            content = invitation_letter.body
            self.assertTrue(UserData.second.username in content)
            self.assertTrue(ModelInfoData.model_b.schema_name in content)
            sign_up_link = self.app.config['ENDPOINT'] + url_for('auth.sign_up') + '?invitation=%s' % guest_invitation.hex
            self.assertTrue(sign_up_link in content)

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData)
    def test_delete_role(self, data):
        model_id = ModelRoleData.first_developer_model_b.model_id

        self.login(UserData.first)
        user_id = ModelRoleData.first_developer_model_b.user_id
        response = self.client.get(url_for('models.remove_member', model_id=model_id, user_id=user_id))
        self.assert_401(response)

        self.login(UserData.second)
        user_id = ModelRoleData.first_developer_model_b.user_id
        response = self.client.get(url_for('models.remove_member', model_id=model_id, user_id=user_id))
        self.assertRedirects(response, url_for('models.team', model_id=model_id))
        self.assertRaises(NoResultFound, lambda: models_service.role(model_id, user_id))

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData, InvitationData)
    def test_cancel_invitation(self, data):
        model_id = InvitationData.invitation.model_id
        invitation_id = InvitationData.invitation.id

        self.login(UserData.first)
        response = self.client.get(url_for('models.cancel_invitation', model_id=model_id, invitation_id=invitation_id))
        self.assert_401(response)

        self.login(UserData.second)
        response = self.client.get(url_for('models.cancel_invitation', model_id=model_id, invitation_id=invitation_id))
        self.assertRedirects(response, url_for('models.team', model_id=model_id))
        invitation = models_service.invitation(invitation_id)
        self.assertFalse(invitation.active)

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData)
    def test_change_member_role(self, data):
        model_id = ModelRoleData.first_developer_model_b.model_id
        user_id = ModelRoleData.first_developer_model_b.user_id

        self.login(UserData.first)
        response = self.client.post(url_for('models.change_member_role', model_id=model_id, user_id=user_id))
        self.assert_401(response)

        subscriber = self.subscribe()

        self.login(UserData.second)
        response = self.client.post(url_for('models.change_member_role', model_id=model_id, user_id=user_id), data={
            'role': ModelRole.VIEWER
        })
        self.assert_200(response)
        self.assertEqual(ModelRole.VIEWER, models_service.role(model_id, user_id).role)
        subscriber.wait_message('change_role', (model_id, user_id,), 0.5)

        response = self.client.post(url_for('models.change_member_role', model_id=model_id, user_id=user_id), data={
            'role': ModelRole.OWNER
        })
        self.assert_400(response)

        model_id = ModelRoleData.second_owner_model_b.model_id
        user_id = ModelRoleData.second_owner_model_b.user_id
        response = self.client.post(url_for('models.change_member_role', model_id=model_id, user_id=user_id), data={
            'role': ModelRole.VIEWER
        })
        self.assert_400(response)

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData, InvitationData)
    def test_change_invitation_role(self, data):
        model_id = InvitationData.invitation.model_id
        invitation_id = InvitationData.invitation.id

        self.login(UserData.first)
        response = self.client.post(url_for('models.change_invitation_role', model_id=model_id, invitation_id=invitation_id))
        self.assert_401(response)

        self.login(UserData.second)
        response = self.client.post(url_for('models.change_invitation_role', model_id=model_id, invitation_id=invitation_id), data={
            'role': ModelRole.VIEWER
        })
        self.assert_200(response)
        self.assertEqual(ModelRole.VIEWER, models_service.invitation(invitation_id).role)

        response = self.client.post(url_for('models.change_invitation_role', model_id=model_id, invitation_id=invitation_id), data={
            'role': ModelRole.OWNER
        })
        self.assert_400(response)