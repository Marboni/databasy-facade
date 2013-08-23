import time
from sqlalchemy.orm.exc import NoResultFound
from databasyfacade.mq import RpcClient
from databasyfacade.mq.client import Subscriber
from databasyfacade.mq.engine import pub_server
from databasyfacade.services import models_service
from databasyfacade.testing import DatabasyTest, fixtures
from databasyfacade.testing.testdata import UserData, ProfileData, ModelInfoData, InvitationData, ModelRoleData

__author__ = 'Marboni'

class RpcTest(DatabasyTest):
    def setUp(self):
        super(RpcTest, self).setUp()
        self.rpc = RpcClient('tcp://localhost:6666')

    def test_echo(self):
        for i in range(1000):
            echo = self.rpc('echo', i)
            self.assertEqual(i, echo)

    @fixtures(UserData, ProfileData)
    def test_user_info(self, data):
        info = self.rpc('user_info', UserData.first.id)
        self.assertEqual(ProfileData.first.user_id, info['user_id'])
        self.assertEqual(ProfileData.first.name, info['name'])
        self.assertEqual(ProfileData.first.email, info['email'])
        self.assertEqual(UserData.first.active, info['active'])
        info = self.rpc('user_info', -1)
        self.assertIsNone(info)

    @fixtures(UserData, ModelInfoData)
    def test_database_type(self, data):
        db_type = self.rpc('database_type', ModelInfoData.model_a.id)
        self.assertEqual(ModelInfoData.model_a.database_type, db_type)
        db_type = self.rpc('database_type', -1)
        self.assertIsNone(db_type)

    @fixtures(UserData, ProfileData, ModelInfoData, ModelRoleData, InvitationData)
    def test_delete_model(self, data):
        model_id = ModelInfoData.model_b.id

        model_info = self.rpc('delete_model', model_id)
        self.assertEqual(ModelInfoData.model_b.schema_name, model_info['schema_name'])
        self.assertEqual(ModelInfoData.model_b.description, model_info['description'])
        self.assertEqual(ModelInfoData.model_b.database_type, model_info['database_type'])
        self.assertRaises(NoResultFound, lambda: models_service.model(model_id))
        self.assertFalse(models_service.model_roles(model_id))
        self.assertFalse(models_service.invitation_by_hex(InvitationData.invitation.hex).active)

        self.assertRaises(NoResultFound, lambda: self.rpc('delete_model', -1))


class TestSubscriber(Subscriber):
    def __init__(self):
        super(TestSubscriber, self).__init__('tcp://localhost:6667')
        self.message = None

    def handle_echo(self, message):
        self.message = message

class PubSubTest(DatabasyTest):
    def setUp(self):
        super(PubSubTest, self).setUp()
        self.sub1 = TestSubscriber()
        self.sub1.run()

        self.sub2 = TestSubscriber()
        self.sub2.run()

    def test_echo(self):
        pub_server().publish('echo', 'Hello!')
        time.sleep(0.5)

        self.assertEqual('Hello!', self.sub1.message)