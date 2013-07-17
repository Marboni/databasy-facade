from databasyfacade.rpc import RpcClient
from databasyfacade.testing import DatabasyTest, fixtures
from databasyfacade.testing.testdata import UserData, ProfileData

__author__ = 'Marboni'

class RpcTest(DatabasyTest):
    def test_echo(self):
        rpc = RpcClient('tcp://localhost:5555')
        for i in range(1000):
            echo = rpc('echo', i)
            self.assertEqual(i, echo)

    @fixtures(UserData, ProfileData)
    def test_profile(self, data):
        rpc = RpcClient('tcp://localhost:5555')
        profile = rpc('profile', UserData.hero.id)
        self.assertEqual(ProfileData.hero.email, profile.email)
