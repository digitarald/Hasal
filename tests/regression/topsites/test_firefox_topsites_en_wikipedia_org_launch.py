
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_topsites_en_wikipedia_org_launch(self):
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target="https://en.wikipedia.org/wiki/Barack_Obama", script_dp=self.env.test_script_py_dp)
