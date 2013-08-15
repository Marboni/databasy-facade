from databasyfacade.rpc import RpcClient
from databasyfacade.testing import DatabasyTest, fixtures
from databasyfacade.testing.testdata import UserData, ProfileData, ModelInfoData

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
    def test_profile(self, data):
        profile = self.rpc('profile', UserData.hero.id)
        self.assertEqual(ProfileData.hero.email, profile.email)
        profile = self.rpc('profile', -1)
        self.assertIsNone(profile)

    @fixtures(UserData, ModelInfoData)
    def test_database_type(self, data):
        db_type = self.rpc('database_type', ModelInfoData.psql.id)
        self.assertEqual(ModelInfoData.psql.database_type, db_type)
        db_type = self.rpc('database_type', -1)
        self.assertIsNone(db_type)