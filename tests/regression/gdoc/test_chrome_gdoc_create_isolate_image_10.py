from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.pre_run_script = "test_chrome_gdoc_read_blank_page"
        self.pre_run_script_test_url_id = "TEST_TARGET_ID_BLANK_PAGE"
        super(TestSikuli, self).setUp()

    def test_chrome_gdoc_create_isolate_image_10(self):
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.test_url, script_dp=self.env.test_script_py_dp)
