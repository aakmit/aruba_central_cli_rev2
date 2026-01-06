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

import logging
from urllib.parse import urlencode, urlparse, urlunparse
from .url_utils import NewCentralURLs

urls = NewCentralURLs()
try:
    import colorlog  # type: ignore

    COLOR = True
except (ImportError, ModuleNotFoundError):
    COLOR = False
C_LOG_LEVEL = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0,
}

SUPPORTED_APPS = ["new_central", "glp"]
NEW_CENTRAL_C_DEFAULT_ARGS = {
    "base_url": None,
    "client_id": None,
    "client_secret": None,
    "access_token": None,
}
URL_BASE_ERR_MESSAGE = "Please provide the base_url of API Gateway where Central account is provisioned!"


def new_parse_input_args(token_info):
    apps_token_info = {}
    for app in token_info:
        print (app)
        if app in SUPPORTED_APPS:
            if app == "glp":
                if "base_url" not in token_info[app]:
                    token_info[app]["base_url"] = urls.GLP["BaseURL"]

            token_info[app]["base_url"] = valid_url(
                token_info[app]["base_url"]
            )

            app_token_info = token_info[app]

            if "base_url" not in app_token_info:
                exit(
                    f"Missing base_url for {app}. Please provide base_url of the API gateway in order to make API calls with the SDK."
                )

            token_keys = list(NEW_CENTRAL_C_DEFAULT_ARGS.keys())
            if "access_token" not in app_token_info:
                token_creation_required_keys = list(
                    set(token_keys) - set(["access_token", "base_url"])
                )
                if not all(
                    key in app_token_info
                    for key in token_creation_required_keys
                ):
                    exit_string = (
                        "Missing Required token creation parameters "
                        + ", ".join(token_creation_required_keys)
                        + ". Please provide either a valid access token or "
                        + "client_id and client_secret required to generate an access token"
                    )
                    exit(exit_string)
            default_dict = dict(NEW_CENTRAL_C_DEFAULT_ARGS)
            for key in default_dict.keys():
                if key in app_token_info:
                    default_dict[key] = app_token_info[key]
            apps_token_info[app] = default_dict
        else:
            exit(
                f"Unknown app name provided. Please provide an application that is supported by the SDK. These are applications that are supported by the SDK - {', '.join(SUPPORTED_APPS)}"
            )
    if len(apps_token_info) == 0:
        exit(
            f"No token information provided. This is required to for the SDK to make API calls to the supported apps - {', '.join(SUPPORTED_APPS)}"
        )
    return apps_token_info


def get_url(base_url, path="", params="", query={}, fragment=""):
    """This method constructs complete URL based on multiple parts of URL.

    :param base_url: base url for a HTTP request
    :type base_url: str
    :param path: API endpoint path, defaults to ''
    :type path: str, optional
    :param params: API endpoint path parameters, defaults to ''
    :type params: str, optional
    :param query: HTTP request url query parameters, defaults to {}
    :type query: dict, optional
    :param fragment: URL fragment identifier, defaults to ''
    :type fragment: str, optional
    :return: Parsed URL
    :rtype: class:`urllib.parse.ParseResult`
    """
    base_url = valid_url(base_url)
    parsed_baseurl = urlparse(base_url)
    scheme = parsed_baseurl.scheme
    netloc = parsed_baseurl.netloc
    query = urlencode(query)
    url = urlunparse((scheme, netloc, path, params, query, fragment))
    return url


def console_logger(name, level="DEBUG"):
    """This method create an instance of python logging and sets the following\
        format for log messages.\n<date> <time> - <name> - <level> - <message>

    :param name: String displayed after data and time. Define it to identify\
        from which part of the code, log message is generated.
    :type name: str
    :param level: Loggin level set to display messages from a certain logging\
        level. Refer Python logging library man page, defaults to "DEBUG"
    :type level: str, optional
    :return: An instance of class logging
    :rtype: class:`logging.Logger`
    """
    channel_handler = logging.StreamHandler()
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    f = format
    if COLOR:
        cformat = "%(log_color)s" + format
        f = colorlog.ColoredFormatter(
            cformat,
            date_format,
            log_colors={
                "DEBUG": "bold_cyan",
                "INFO": "blue",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    else:
        f = logging.Formatter(format, date_format)
    channel_handler.setFormatter(f)

    logger = logging.getLogger(name)
    logger.setLevel(C_LOG_LEVEL[level])
    logger.addHandler(channel_handler)

    return logger


def valid_url(url):
    """This method verifies & returns the URL in a valid format. If the URL is\
        missing the https prefix, the function will prepend the prefix after\
        verifiying that its a valid base URL of an Aruba Central cluster.

    :param base_url: base url for a HTTP request
    :type base_url: str
    :return: Valid Base URL
    :rtype: str
    """
    parsed_url = urlparse(url)
    if all([parsed_url.scheme, parsed_url.netloc]):
        return parsed_url.geturl()
    elif bool(parsed_url.scheme) is False and bool(parsed_url.path):
        parsed_url = parsed_url._replace(
            **{"scheme": "https", "netloc": parsed_url.path, "path": ""}
        )
        return parsed_url.geturl()
    else:
        errorMessage = (
            "Invalid Base URL - " + f"{url}\n" + URL_BASE_ERR_MESSAGE
        )
        raise ValueError(errorMessage)
