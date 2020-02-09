# encoding: utf-8

from unittest.mock import Mock, patch

from src.client.models import utils
from src.exceptions import WalletError
from tests.unit.logging import LoggingMixin


class ClientUtilsTest(LoggingMixin):

    def setUp(self):
        self.data = {'test_data_key': 'test_data_value'}

    def test_get_utcnow_timestamp(self):
        timestamp = utils.get_utcnow_timestamp()
        self.assertIsInstance(timestamp, int)

    def test_utils_serialize(self):
        serialized = utils.serialize(self.data)
        self.assertIsInstance(self.data, dict)
        self.assertIsInstance(serialized, str)

    @patch('src.client.models.utils.json.dumps')
    def test_utils_serialize_error(self, mock_json_dumps):
        err_message = 'Could not encode data'
        mock_json_dumps.side_effect = Mock(side_effect=WalletError(err_message))
        with self.assertRaises(WalletError) as err:
            utils.serialize(self.data)
            self.assertTrue(mock_json_dumps.called)
            self.assertIsInstance(err, WalletError)
            self.assertIn(err_message, err.message)
