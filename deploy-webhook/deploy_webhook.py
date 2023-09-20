###############################################################################
#
# Copyright (c) 2023 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
###############################################################################

import hashlib
import hmac
import json
import logging
import os
import subprocess
from urllib.parse import unquote

BASEDIR = '/opt/demo.pycsw.org'
LOGGER = logging.getLogger(__name__)


def is_valid_secret(secret_server, secret, payload):
    """Validate a GitHub webhook secret token/payload"""

    is_valid = False

    if secret is None:
        return False

    sha_name, signature = secret.split('=')

    if sha_name != 'sha1':
        return False

    mac = hmac.new(secret_server, msg=payload.encode(), digestmod=hashlib.sha1)

    try:
        is_valid = hmac.compare_digest(str(mac.hexdigest()), signature)
    except AttributeError:
        is_valid = str(mac.hexdigest()) == str(signature)

    return is_valid


def application(environ, start_response):
    """WSGI application to update demo server from a Webhook"""

    error = 0
    response = {
        'status': '200 OK',
        'message': 'Success'
    }

    # read in request
    length = int(environ.get('CONTENT_LENGTH', '0'))
    secret_key = bytes(os.environ.get('DEMO_PYCSW_ORG_SECRET_KEY'), 'utf8')
    signature = environ.get('HTTP_X_HUB_SIGNATURE', None)
    payload = environ['wsgi.input'].read(length).decode('utf8')
    payload = unquote(payload).split('payload=')[-1]

    try:
        request = json.loads(payload)
    except ValueError as err:
        msg = 'Invalid request payload'
        LOGGER.error(f'{msg}: {err}')
        error = 1
        response = {
            'status': '400 Bad Request',
            'message': msg
        }

    if error == 0:
        if (is_valid_secret(secret_key, signature, payload) and
                not request['repository']['fork']):

            repository_full_name = request['repository']['full_name']
            commit_id = request['head_commit']['id']

            if repository_full_name == 'geopython/pycsw':
                LOGGER.debug('Triggering deployment update')

                try:
                    os.chdir(BASEDIR)
                    subprocess.check_output(['docker-compose', 'down'])
                    subprocess.check_output(['docker', 'pull', 'geopython/pycsw:latest'])  # noqa
                    subprocess.check_output(['git', 'pull', 'origin', 'master'])  # noqa
                    subprocess.check_output(['docker-compose', 'up', '-d'])
                except subprocess.CalledProcessError as err:
                    msg = 'Update failed'
                    LOGGER.error(f'{msg}: {err}')
                    response = {
                        'status': '500 Internal Server Error',
                        'message': msg
                    }

            msg = f'{repository_full_name}:{commit_id} successfully deployed'

            response = {
                'status': '200 OK',
                'message': msg
            }

    output = bytes(json.dumps(response).encode('utf-8'))

    response_headers = [('Content-Type', 'application/json'),
                        ('Content-Length', str(len(output)))]

    start_response(response['status'], response_headers)

    return [output]
