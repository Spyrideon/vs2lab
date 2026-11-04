# pylint: disable=missing-docstring, protected-access
import threading
import unittest

import clientserver
import const_cs

SMALL_BOOK = {"Alice": "0151-123456", "Bob": "0170-987654"}

BOOK_500 = {f"Name{i}": f"0721-{i:04d}" for i in range(499)}
BOOK_500["Müller"] = "0721-9251000"


def handle(book, request):
    server = clientserver.Server(book)
    server.sock.close()
    return server.handle(request)


class TestBackend(unittest.TestCase):

    def test_get(self):
        self.assertEqual(handle(SMALL_BOOK, {"command": "GET", "name": "Alice"}), "0151-123456")

    def test_get_unknown_name(self):
        self.assertIsNone(handle(SMALL_BOOK, {"command": "GET", "name": "Zoe"}))

    def test_get_is_case_sensitive(self):
        self.assertIsNone(handle(SMALL_BOOK, {"command": "GET", "name": "alice"}))

    def test_getall(self):
        self.assertEqual(handle(SMALL_BOOK, {"command": "GETALL"}), SMALL_BOOK)

    def test_getall_empty_book(self):
        self.assertEqual(handle({}, {"command": "GETALL"}), {})

    def test_default_book(self):
        self.assertEqual(handle(None, {"command": "GETALL"}), const_cs.PHONE_BOOK)

    def test_unknown_command(self):
        self.assertIsNone(handle(SMALL_BOOK, {"command": "DELETE", "name": "Alice"}))


class TestService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._server = clientserver.Server(BOOK_500)
        cls._server_thread = threading.Thread(target=cls._server.serve)
        cls._server_thread.start()

    def setUp(self):
        self.client = clientserver.Client()

    def test_get(self):
        self.assertEqual(self.client.get("Name42"), "0721-0042")

    def test_get_unknown_name(self):
        self.assertIsNone(self.client.get("Nobody"))

    def test_get_umlaut(self):
        self.assertEqual(self.client.get("Müller"), "0721-9251000")

    def test_getall_500_entries(self):
        entries = self.client.get_all()
        self.assertEqual(len(entries), 500)
        self.assertEqual(entries, BOOK_500)

    def test_several_requests_one_connection(self):
        self.assertEqual(self.client.get("Name1"), "0721-0001")
        self.assertEqual(len(self.client.get_all()), 500)
        self.assertEqual(self.client.get("Name2"), "0721-0002")

    def tearDown(self):
        self.client.close()

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False
        cls._server_thread.join()


if __name__ == '__main__':
    unittest.main()