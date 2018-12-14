# coding: utf-8
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

from testinfra.modules.base import Module

class Addr(Module):
    """Test connections"""

    def __init__(self, address, port="", protocol="icmp"):
        self.address = address
        self.port = port
        self.protocol = protocol
        super(Addr, self).__init__()

    def is_reachable(self):
        try:
            self.find_command("nc")
            has_nc = True
        except ValueError:
            has_nc = False

        if self.protocol == "tcp":
            if has_nc:
                result = self.run_test("echo | nc -vw 1 %s %s", self.address, self.port)
            else:
                result = self.run_test("timeout 1 bash -c \"< /dev/tcp/%s/%s\"", self.address, self.port)
        elif self.protocol == "udp":
            if has_nc:
                result = self.run_test("timeout 1 bash -c \"< /dev/udp/%s/%s\"", self.address, self.port)
            else:
                raise ValueError("can't test udp without netcat")
        else:
            result = self.run_test("ping -w 1 -c 1 %s", self.address)

        if result.rc != 0:
            # Had some issues with an LB, was getting connected and remained connected
            if "Connected to" in result.stderr.strip():
                return True
            return False

        return True