###############################################################################
#
# Copyright (c) 2020 Tom Kralidis
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
import os
import subprocess

BASEDIR = '/opt/demo.pycsw.org'


def is_valid_secret(secret_server, secret, payload):
    """Validate a GitHub webhook secret token/payload"""

    is_valid = False

    if secret is None:
        return False

    sha_name, signature = secret.split('=')

    if sha_name != 'sha1':
        return False

    mac = hmac.new(secret_server, msg=payload, digestmod=hashlib.sha1)

    try:
        is_valid = hmac.compare_digest(str(mac.hexdigest()), signature)
    except AttributeError:
        is_valid = str(mac.hexdigest()) == str(signature)

    return is_valid


def application(environ, start_response):
    """WSGI application to run off a Webhook"""

    error = 0
    response = {
        'status': '400 Bad Request',
        'message': 'Could not update repository'
    }

    # read in request
    length = int(environ.get('CONTENT_LENGTH', '0'))
    secret_key = environ.get('DEMO_PYWPS_ORG_SECRET_KEY')
    signature = environ.get('HTTP_X_HUB_SIGNATURE', None)
    payload = environ['wsgi.input'].read(length)

    try:
        request = json.loads(payload)
    except ValueError:
        error = 1

    if error == 0:
        if (is_valid_secret(secret_key, signature, payload) and
                not request['repository']['fork']):
            # trigger deployment update
            repository_full_name = request['repository']['full_name']

            if repository_full_name == 'geopython/pycsw':
                # update develop, install library  and touch .wsgi file to
                os.chdir(BASEDIR)
                subprocess.call(['docker-compose', 'down'])
                subprocess.call(['docker', 'pull', 'geopython/pycsw:latest'])
                subprocess.call(['git', 'pull', 'origin', 'master'])
                subprocess.call(['docker-compose', 'up', '-d'])

            message = 'Repository {} successfully updated to {}'.format(
                repository_full_name,
                request['head_commit']['id'])

            response = {
                'status': '200 OK',
                'message': message
            }

    output = bytes(json.dumps(response).encode('utf-8'))

    response_headers = [('Content-type', 'application/json'),
                        ('Content-Length', str(len(output)))]
    start_response(response['status'], response_headers)
    return [output]
