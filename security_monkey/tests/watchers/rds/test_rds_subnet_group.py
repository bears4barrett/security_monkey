#     Copyright 2016 Bridgewater Associates
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
"""
.. module: security_monkey.tests.watchers.rds.test_rds_subnet_group
    :platform: Unix

.. version:: $$VERSION$$
.. moduleauthor:: Bridgewater OSS <opensource@bwater.com>


"""
from security_monkey.tests import SecurityMonkeyTestCase
from security_monkey.watchers.rds.rds_subnet_group import RDSSubnetGroup
from security_monkey.datastore import Account
from security_monkey.tests.db_mock import MockAccountQuery

import boto
from moto import mock_sts, mock_rds, mock_ec2
from freezegun import freeze_time
from mock import patch

mock_query = MockAccountQuery()


class RDSSubnetGroupWatcherTestCase(SecurityMonkeyTestCase):

    @freeze_time("2016-07-18 12:00:00")
    @mock_sts
    @mock_rds
    @mock_ec2
    @patch('security_monkey.datastore.Account.query', new=mock_query)
    def test_slurp(self):
        test_account = Account()
        test_account.name = "TEST_ACCOUNT"
        test_account.notes = "TEST ACCOUNT"
        test_account.s3_name = "TEST_ACCOUNT"
        test_account.number = "012345678910"
        test_account.role_name = "TEST_ACCOUNT"
        mock_query.add_account(test_account)

        vpc_conn = boto.vpc.connect_to_region("us-east-1")
        vpc = vpc_conn.create_vpc("10.0.0.0/16")
        subnet = vpc_conn.create_subnet(vpc.id, "10.1.0.0/24")

        subnet_ids = [subnet.id]
        conn = boto.rds.connect_to_region("us-east-1")
        conn.create_db_subnet_group("db_subnet", "my db subnet", subnet_ids)

        watcher = RDSSubnetGroup(accounts=[test_account.name])
        item_list, exception_map = watcher.slurp()

        self.assertIs(
            expr1=len(item_list),
            expr2=1,
            msg="Watcher should have 1 item but has {}".format(len(item_list)))
