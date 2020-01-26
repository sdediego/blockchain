# encoding: utf-8

from unittest.mock import Mock, patch

from src.app.utils import parse, stringify
from src.exceptions import P2PServerError
from tests.unit.logging import LoggingMixin


class P2PServerUtilsTest(LoggingMixin):

    def setUp(self):
        super(P2PServerUtilsTest, self).setUp()
        self.message = {'channel': 'test_channel', 'content': 'test_content'}

    def test_p2p_server_stringify(self):
        stringified = stringify(self.message)
        self.assertIsInstance(self.message, dict)
        self.assertIsInstance(stringified, str)
        self.assertIn('channel', stringified)
        self.assertIn('content', stringified)

    @patch('src.app.utils.json.dumps')
    def test_p2p_server_stringify_error(self, mock_json_dumps):
        err_message = 'Could not encode message data.'
        mock_json_dumps.side_effect = Mock(side_effect=P2PServerError(err_message))
        with self.assertRaises(P2PServerError) as err:
            stringify(self.message)
            self.assertTrue(mock_json_dumps.called)
            self.assertIsInstance(err, P2PServerError)
            self.assertIn(err_message, err.message)

    def test_p2p_server_parse(self):
        stringified = stringify(self.message)
        self.assertIsInstance(self.message, dict)
        self.assertIsInstance(stringified, str)
        message = parse(stringified)
        self.assertIsInstance(message, dict)
        self.assertIn('channel', message)
        self.assertIn('content', message)
        self.assertEqual(message.get('channel'), 'test_channel')
        self.assertEqual(message.get('channel'), 'test_channel')

    @patch('src.app.utils.json.loads')
    def test_p2p_server_parse_error(self, mock_json_loads):
        err_message = 'Could not decode message data.'
        mock_json_loads.side_effect = Mock(side_effect=P2PServerError(err_message))
        stringified = stringify(self.message)
        with self.assertRaises(P2PServerError) as err:
            parse(stringified)
            self.assertTrue(mock_json_loads.called)
            self.assertIsInstance(err, P2PServerError)
            self.assertIn(err_message, err.message)
