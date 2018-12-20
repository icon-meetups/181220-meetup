import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, TransactionBuilder, CallTransactionBuilder
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestScrooge(IconIntegrateTestBase):
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))
    SAMPLE_TOKEN = os.path.abspath(os.path.join(DIR_PATH, '../../standard_token'))

    def setUp(self):
        super().setUp()
        self.icon_service = None
        self._score_address = self._deploy_score(scorepath=self.SCORE_PROJECT)['scoreAddress']

    def _deploy_score(self, scorepath: str, to: str = SCORE_INSTALL_ADDRESS, _params: dict = None) -> dict:
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(scorepath)) \
            .params(_params) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def test_score_update(self):
        tx_result = self._deploy_score(scorepath=self.SCORE_PROJECT, to=self._score_address)

        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)
        self.assertEqual(self._score_address, tx_result['scoreAddress'])

    def test_fallback(self):
        transaction = TransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address) \
            .value(1) \
            .step_limit(10000000000) \
            .nid(3) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

    def test_token_fallback(self):
        input_params = {"initialSupply": 1000, "decimals": 1}
        token_deploy_result = self._deploy_score(scorepath=self.SAMPLE_TOKEN, _params=input_params)
        score_address = token_deploy_result['scoreAddress']

        transaction = CallTransactionBuilder().from_(self._test1.get_address()) \
            .to(score_address) \
            .step_limit(10000000000) \
            .nid(3) \
            .method("transfer") \
            .params({"_to": self._score_address, "_value": 10}) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertEqual(1, tx_result['status'])

        call = CallBuilder().from_(self._test1.get_address()) \
            .to(score_address) \
            .method("balanceOf") \
            .params({"_owner": self._score_address}) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual('0xa', response)
