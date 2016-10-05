from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        super(TestSikuli, self).setUp()

    def test_firefox_facebook_load_homepage(self):
        args = [self.env.img_sample_dp, self.env.img_output_sample_1_fn, '0', '0',
                str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH), str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT)]
        self.sikuli_status = self.sikuli.run_test(self.env.test_name, self.env.output_name, test_target=self.env.TEST_FB_HOME, script_dp=self.env.test_script_py_dp, args_list=args)
