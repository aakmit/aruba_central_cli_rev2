# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def urlJoin(*args):
    trailing_slash = "/" if args[-1].endswith("/") else ""
    return (
        "/" + "/".join(map(lambda x: str(x).strip("/"), args)) + trailing_slash
    )


class NewCentralURLs:
    Authentication = {
        "OAUTH": "https://sso.common.cloud.hpe.com/as/token.oauth2"
    }

    GLP = {"BaseURL": "https://global.api.greenlake.hpe.com"}

    GLP_DEVICES = {
        "DEFAULT": "/devices/v1/devices",
        # full url requires {id} to be passed as param: /devices/v1/async-operations/{id}
        "GET_ASYNC": "/devices/v1/async-operations/",
    }

    GLP_SUBSCRIPTION = {
        "DEFAULT": "/subscriptions/v1/subscriptions",
        # full url requires {id} to be passed as param: /devices/v1/async-operations/{id}
        "GET_ASYNC": "/subscriptions/v1/async-operations/",
    }

    GLP_USER_MANAGEMENT = {
        "GET": "/identity/v1/users",
        # full url requires {id} to be passed as param: /identity/v1/users/{id}
        "GET_USER": "/identity/v1/users/",
        "POST": "/identity/v1/users",
        # full url requires {id} to be passed as param: /identity/v1/users/{id}
        "PUT": "/identity/v1/users/",
        # full url requires {id} to be passed as param: /identity/v1/users/{id}
        "DELETE": "/identity/v1/users/",
    }
