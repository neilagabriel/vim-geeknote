import unittest
import vim_geeknote as sut


@unittest.skip("Don't forget to test!")
class VimGeeknoteTests(unittest.TestCase):

    def test_example_fail(self):
        result = sut.vim_geeknote_example()
        self.assertEqual("Happy Hacking", result)
