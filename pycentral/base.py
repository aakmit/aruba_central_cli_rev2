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
import oauthlib
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
import json
import requests
from .utils.base_utils import get_url, new_parse_input_args, console_logger
from .utils.url_utils import NewCentralURLs
from .exceptions import LoginError, ResponseError

urls = NewCentralURLs()
SUPPORTED_API_METHODS = ("POST", "PATCH", "DELETE", "GET", "PUT")


class NewCentralBase:
    def __init__(self, token_info, logger=None, log_level="DEBUG"):
        """
        Initialize the NewCentralBase class.

        :param token_info: Dictionary containing token information for supported applications - new_central, glp.
        :type token_info: dict
        :param logger: Logger instance, defaults to None.
        :type logger: logging.Logger, optional
        :param log_level: Logging level, defaults to "DEBUG".
        :type log_level: str, optional
        """
    
        self.token_info = new_parse_input_args(token_info)
        self.logger = self.set_logger(log_level, logger)
        for app in self.token_info:
            app_token_info = self.token_info[app]
            if (
                "access_token" not in app_token_info
                or app_token_info["access_token"] is None
            ):
                self.token_info[app]["access_token"] = self.create_token(app)
            

    def set_logger(self, log_level, logger=None):
        """
        Set the logger for the class.

        :param log_level: Logging level.
        :type log_level: str
        :param logger: Logger instance, defaults to None.
        :type logger: logging.Logger, optional
        :return: Logger instance.
        :rtype: logging.Logger
        """
        if logger:
            return logger
        else:
            return console_logger("NEW CENTRAL BASE", log_level)

    def create_token(self, app_name):
        """
        Create a new access token for the specified application.

        :param app_name: Name of the application.
        :type app_name: str
        :return: Access token.
        :rtype: str
        :raises LoginError: If there is an error during token creation.
        """
        client_id, client_secret = self._return_client_credentials(app_name)
        client = BackendApplicationClient(client_id)

        oauth = OAuth2Session(client=client)
        auth = HTTPBasicAuth(client_id, client_secret)

        try:
            self.logger.info(f"Attempting to create new token from {app_name}")
            token = oauth.fetch_token(
                token_url=urls.Authentication["OAUTH"], auth=auth
            )

            if "access_token" in token:
                self.logger.info(
                    f"{app_name} Login Successful.. Obtained Access Token!"
                )
                return token["access_token"]
        except oauthlib.oauth2.rfc6749.errors.InvalidClientError:
            exitString = (
                "Invalid client_id or client_secret provided for "
                + app_name
                + ". Please provide valid credentials to create an access token"
            )
            exit(exitString)
        except Exception as e:
            raise LoginError(e)

    def handle_expired_token(self, app_name):
        """
        Handle expired access token for the specified application.

        :param app_name: Name of the application.
        :type app_name: str
        """
        self.logger.info(f"{app_name} access Token has expired.")
        self.logger.info("Handling Token Expiry...")
        client_id, client_secret = self._return_client_credentials(app_name)
        if any(
            credential is None for credential in [client_id, client_secret]
        ):
            exit(
                f"Please provide client_id and client_secret in {app_name} required to generate an access token"
            )
        else:
            self.token_info[app_name]["access_token"] = self.create_token(
                app_name
            )

    def command(
        self,
        api_method,
        api_path,
        app_name="new_central",
        api_data={},
        api_params={},
        headers={},
        files={},
    ):
        """
        Execute an API command.

        :param api_method: HTTP method for the API request.
        :type api_method: str
        :param api_path: API endpoint path.
        :type api_path: str
        :param app_name: Name of the application, defaults to "new_central".
        :type app_name: str, optional
        :param api_data: Data to be sent in the API request, defaults to {}.
        :type api_data: dict, optional
        :param api_params: URL query parameters for the API request, defaults to {}.
        :type api_params: dict, optional
        :param headers: HTTP headers for the API request, defaults to {}.
        :type headers: dict, optional
        :param files: Files to be sent in the API request, defaults to {}.
        :type files: dict, optional
        :return: API response.
        :rtype: dict
        :raises ResponseError: If there is an error during the API request.
        """
        retry = 0
        result = ""
        self._validate_method(api_method)
        limit_reached = False
        try:
            while not limit_reached:
                url = get_url(self.token_info[app_name]["base_url"], api_path)
                
                if not headers and not files:
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                if api_data and headers["Content-Type"] == "application/json":
                    api_data = json.dumps(api_data)

                resp = self.request_url(
                    url=url,
                    data=api_data,
                    method=api_method,
                    headers=headers,
                    params=api_params,
                    files=files,
                    access_token=self.token_info[app_name]["access_token"],
                )
                if resp.status_code == 401:
                    self.logger.error(
                        "Received error 401 on requesting url "
                        "%s with resp %s" % (str(url), str(resp.text))
                    )
                    if retry >= 1:
                        limit_reached = True
                        break
                    self.handle_expired_token(app_name)
                    retry += 1
                else:
                    break

            result = {
                "code": resp.status_code,
                "msg": resp.text,
                "headers": dict(resp.headers),
            }

            try:
                result["msg"] = json.loads(result["msg"])
            except BaseException:
                result["msg"] = str(resp.text)

            return result

        except Exception as err:
            err_str = f"{api_method} FAILURE "
            self.logger.error(err)
            raise ResponseError(err_str, err)

    def request_url(
        self,
        url,
        access_token,
        data={},
        method="GET",
        headers={},
        params={},
        files={},
    ):
        """
        Make an API call to New Central or GLP.

        :param url: HTTP Request URL string.
        :type url: str
        :param access_token: Access token for authentication.
        :type access_token: str
        :param data: HTTP Request payload, defaults to {}.
        :type data: dict, optional
        :param method: HTTP Request Method supported by New Central & GLP, defaults to "GET".
        :type method: str, optional
        :param headers: HTTP Request headers, defaults to {}.
        :type headers: dict, optional
        :param params: HTTP url query parameters, defaults to {}.
        :type params: dict, optional
        :param files: Files dictionary with file pointer depending on API endpoint as accepted by New Central or GLP, defaults to {}.
        :type files: dict, optional
        :return: HTTP response of API call using requests library.
        :rtype: requests.models.Response
        :raises ResponseError: If there is an error during the API request.
        """
        resp = None

        auth = BearerAuth(access_token)
        s = requests.Session()
        req = requests.Request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            auth=auth,
            params=params,
            data=data,
        )
        prepped = s.prepare_request(req)
        settings = s.merge_environment_settings(
            prepped.url, {}, None, True, None
        )
        try:
            resp = s.send(prepped, **settings)
            return resp
        except Exception as err:
            str1 = "Failed making request to URL %s " % url
            str2 = "with error %s" % str(err)
            err_str = f"{str1} {str2}"
            self.logger.error(str1 + str2)
            raise ResponseError(err_str, err)

    def _validate_method(self, method):
        """
        Validate the HTTP method.

        :param method: HTTP method.
        :type method: str
        :raises SystemExit: If the method is not supported.
        """
        if method not in SUPPORTED_API_METHODS:
            str1 = "HTTP method '%s' not supported.. " % method
            self.logger.error(str1)
            exit(
                f'Please provide an API with one of the supported methods - {", ".join(SUPPORTED_API_METHODS)}'
            )

    def _return_client_credentials(self, app_name):
        """
        Return client credentials for the specified application.

        :param app_name: Name of the application.
        :type app_name: str
        :return: Client ID and client secret.
        :rtype: tuple
        """
        app_token_info = self.token_info[app_name]
        if all(
            client_key in app_token_info
            for client_key in ("client_id", "client_secret")
        ):
            client_id = app_token_info["client_id"]
            client_secret = app_token_info["client_secret"]
            return client_id, client_secret


class BearerAuth(requests.auth.AuthBase):
    """This class uses Bearer Auth method to generate the authorization header
    from New Central & GLP Access Token.

    :param token: New Central or GLP Access Token
    :type token: str
    """

    def __init__(self, token):
        """Constructor Method"""
        self.token = token

    def __call__(self, r):
        """Internal method returning auth"""
        r.headers["authorization"] = "Bearer " + self.token
        return r
