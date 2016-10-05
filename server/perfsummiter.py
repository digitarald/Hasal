import json
import operator
import random
import string
import time
from thclient import (TreeherderClient, TreeherderResultSetCollection,
                      TreeherderJobCollection)


def geometric_mean(iterable):
    filtered = list(filter(lambda x: x > 0, iterable))
    return (reduce(operator.mul, filtered)) ** (1.0 / len(filtered))


class PerfherderSummiter(object):
    def __init__(self, credentials, platform_info):
        self.host_server = 'local.treeherder.mozilla.org'  # 'treeherder.allizom.org'
        self.author = 'Hasal Bot'
        self.email = 'hasal-dev@mozilla.com'
        self.subject = 'Update Hasal Result'
        self.timestamp = int(time.time())
        self.platform = platform_info.get('platform')
        self.os_name = platform_info.get('os_name')
        self.architecture = platform_info.get('architecture')
        self.cred = credentials

    @staticmethod
    def gen_guid(length=32):
        return ''.join(random.choice(string.letters + string.digits) for _ in xrange(length))

    def submit(self, perf_data, revision_hash, link=None):
        job_guid = PerfherderSummiter.gen_guid(len(revision_hash))

        trsc = TreeherderResultSetCollection()

        author = "{} <{}>".format(self.author, self.email)

        dataset = [
            {
                # The top-most revision in the list of commits for a push.
                'revision': revision_hash,
                'author': author,
                'push_timestamp': self.timestamp,
                'type': 'push',
                # a list of revisions associated with the resultset. There should
                # be at least one.
                'revisions': [
                    {
                        'comment': self.subject,
                        'revision': revision_hash,
                        'repository': 'mozilla-central',
                        'author': author
                    }
                ]
            }
        ]

        for data in dataset:

            trs = trsc.get_resultset()

            trs.add_push_timestamp(data['push_timestamp'])
            trs.add_revision(data['revision'])
            trs.add_author(data['author'])
            # trs.add_type(data['type'])

            revisions = []
            for rev in data['revisions']:
                tr = trs.get_revision()

                tr.add_revision(rev['revision'])
                tr.add_author(rev['author'])
                tr.add_comment(rev['comment'])
                tr.add_repository(rev['repository'])

                revisions.append(tr)

            trs.add_revisions(revisions)

            trsc.add(trs)

        dataset = [
            {
                'project': 'mozilla-central',
                'revision': revision_hash,
                'job': {
                    'job_guid': job_guid,
                    'product_name': 'hasal',
                    'reason': 'scheduler',
                    # TODO:What is `who` for?
                    'who': 'Hasal',
                    'desc': 'Hasal Regression f Median',
                    'name': 'Hasal Regression f Median',
                    # The symbol representing the job displayed in
                    # treeherder.allizom.org
                    'job_symbol': 'RfM',

                    # The symbol representing the job group in
                    # treeherder.allizom.org
                    'group_symbol': 'H',
                    'group_name': 'Hasal Perf Test',

                    # TODO: get the real timing from the test runner
                    'submit_timestamp': self.timestamp,
                    'start_timestamp': self.timestamp,
                    'end_timestamp': self.timestamp,

                    'state': 'completed',
                    'result': 'success',

                    'machine': 'local-machine',
                    # TODO: read platform test result
                    'build_platform': {
                        'platform': self.platform,
                        'os_name': self.os_name,
                        'architecture': self.architecture
                    },
                    'machine_platform': {
                        'platform': self.platform,
                        'os_name': self.os_name,
                        'architecture': self.architecture
                    },

                    'option_collection': {'opt': True},

                    # jobs can belong to different tiers
                    # setting the tier here will determine which tier the job
                    # belongs to.  However, if a job is set as Tier of 1, but
                    # belongs to the Tier 2 profile on the server, it will still
                    # be saved as Tier 2.
                    'tier': 1,

                    # the ``name`` of the log can be the default of "buildbot_text"
                    # however, you can use a custom name.  See below.
                    # TODO: point this to the log when we have them uploaded
                    'log_references': [
                        {
                            'url': 'TBD',
                            'name': 'test log'
                        }
                    ],
                    # The artifact can contain any kind of structured data
                    # associated with a test.
                    'artifacts': [
                        {
                            'type': 'json',
                            'name': 'performance_data',
                            'job_guid': job_guid,
                            'blob': perf_data
                        },
                        {
                            'type': 'json',
                            'name': 'Job Info',
                            'job_guid': job_guid,
                            'blob': {
                                'job_details': [
                                    {
                                        'url': link,
                                        'value': 'website',
                                        'content_type': 'link',
                                        'title': 'Dashboard'
                                    }
                                ]
                            }
                        }
                    ],
                    # List of job guids that were coalesced to this job
                    'coalesced': []
                }
            }
        ]

        tjc = TreeherderJobCollection()

        for data in dataset:

            tj = tjc.get_job()

            tj.add_revision(data['revision'])
            tj.add_project(data['project'])
            tj.add_coalesced_guid(data['job']['coalesced'])
            tj.add_job_guid(data['job']['job_guid'])
            tj.add_job_name(data['job']['name'])
            tj.add_job_symbol(data['job']['job_symbol'])
            tj.add_group_name(data['job']['group_name'])
            tj.add_group_symbol(data['job']['group_symbol'])
            tj.add_description(data['job']['desc'])
            tj.add_product_name(data['job']['product_name'])
            tj.add_state(data['job']['state'])
            tj.add_result(data['job']['result'])
            tj.add_reason(data['job']['reason'])
            tj.add_who(data['job']['who'])
            tj.add_tier(data['job']['tier'])
            tj.add_submit_timestamp(data['job']['submit_timestamp'])
            tj.add_start_timestamp(data['job']['start_timestamp'])
            tj.add_end_timestamp(data['job']['end_timestamp'])
            tj.add_machine(data['job']['machine'])

            tj.add_build_info(
                data['job']['build_platform']['os_name'],
                data['job']['build_platform']['platform'],
                data['job']['build_platform']['architecture']
            )

            tj.add_machine_info(
                data['job']['machine_platform']['os_name'],
                data['job']['machine_platform']['platform'],
                data['job']['machine_platform']['architecture']
            )

            tj.add_option_collection(data['job']['option_collection'])

            # for log_reference in data['job']['log_references']:
            #    tj.add_log_reference( 'buildbot_text', log_reference['url'])

            # data['artifact'] is a list of artifacts
            for artifact_data in data['job']['artifacts']:
                tj.add_artifact(
                    artifact_data['name'],
                    artifact_data['type'],
                    artifact_data['blob']
                )
            tjc.add(tj)

        client = TreeherderClient(protocol='http',
                                  host=self.host_server,
                                  client_id=self.cred['client_id'],
                                  secret=self.cred['secret'])

        # data structure validation is automatically performed here, if validation
        # fails a TreeherderClientError is raised
        client.get_job_groups()
        client.post_collection('mozilla-central', trsc)
        client.post_collection('mozilla-central', tjc)


with open('credentials.json', 'rb') as f:
    credentials = json.load(f)

platform_info = {
    'platform': 'OS X',
    'os_name': 'Mac',
    'architecture': 'x86_64'
}

dashboard_url = 'https://askeing.github.io/hasal-dashboard/?os=win32&target=firefox_47.0.1'

# {
#    "performance_data": {
#        # that is not `talos`?
#        "framework": {"name": "talos"},
#        "suites": [{
#            "name": "performance.timing.domComplete",
#            "value": random.choice(range(15,25)),
#            "subtests": [
#                {"name": "responseEnd", "value": 123},
#                {"name": "loadEventEnd", "value": 223}
#            ]
#        }]
#     }
# }
geometric_value = geometric_mean([8591, 9527])
perf_data = {
    'performance_data': {
        'framework': {
            'name': 'hasal-perf'
        },
        'suites': [
            {
                'name': 'Hasal Regression f Median',
                'value': geometric_value,
                'subtests': [
                    {'name': 'foo_homepage', 'value': 8591},
                    {'name': 'foo_headline', 'value': 9527},
                ]
            }
        ]
    }
}

print(credentials)

hash_string = '87cd291d2db621da6b3eb1057027cc0725b6eb1d'
ps = PerfherderSummiter(credentials, platform_info)
ps.submit(perf_data, hash_string, dashboard_url)
