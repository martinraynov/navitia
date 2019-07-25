# coding: utf-8
# Copyright (c) 2001-2018, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io

from __future__ import absolute_import, print_function, division

from tyr import app
from navitiacommon import models
from tests.check_utils import api_get, api_delete, api_put

import pytest
import ujson


@pytest.fixture
def default_streetnetwork_backend():
    with app.app_context():
        kraken = models.StreetNetworkBackend('kraken')
        kraken.klass = 'kraken.klass'
        kraken.args = {'url': 'http://kraken.url', 'fail_max': 5, 'timeout': 2}
        models.db.session.add(kraken)

        asgard = models.StreetNetworkBackend('asgard')
        asgard.klass = 'asgard.klass'
        asgard.args = {'url': 'http://asgard.url', 'fail_max': 10, 'timeout': 1}
        models.db.session.add(asgard)

        models.db.session.commit()
        # refresh and detach the objets from the db before returning them
        models.db.session.refresh(kraken)
        models.db.session.refresh(asgard)
        models.db.session.expunge(kraken)
        models.db.session.expunge(asgard)

        yield kraken, asgard

        models.db.session.delete(kraken)
        models.db.session.delete(asgard)
        models.db.session.commit()


@pytest.fixture(scope='function', autouse=True)
def clean_db():
    with app.app_context():
        models.db.session.execute('truncate streetnetwork_backend cascade;')
        models.db.session.commit()


def test_streetnetwork_backend_get(default_streetnetwork_backend):
    """
    Test that the list of backends with their info is correctly returned when queried
    """
    kraken, asgard = default_streetnetwork_backend
    resp = api_get('/v0/streetnetwork_backends')
    assert 'streetnetwork_backends' in resp
    assert len(resp['streetnetwork_backends']) == 2

    resp = api_get('/v0/streetnetwork_backends/kraken')
    assert 'streetnetwork_backends' in resp
    assert len(resp['streetnetwork_backends']) == 1

    assert resp['streetnetwork_backends'][0]['args'] == kraken.args
    assert not resp['streetnetwork_backends'][0]['discarded']

    resp = api_get('/v0/streetnetwork_backends/asgard')
    assert 'streetnetwork_backends' in resp
    assert len(resp['streetnetwork_backends']) == 1

    assert resp['streetnetwork_backends'][0]['args'] == asgard.args
    assert not resp['streetnetwork_backends'][0]['discarded']


def test_streetnetwork_backend_put(default_streetnetwork_backend):
    """
    Test that a backend is correctly created/updated in db and the info returned when queried
    """

    # Create new backend
    new_backend = {'klass': 'valhalla.klass'}
    resp, status = api_put(
        'v0/streetnetwork_backends/valhalla',
        data=ujson.dumps(new_backend),
        content_type='application/json',
        check=False,
    )
    assert status == 201
    assert 'message' in resp
    assert resp['message'] == 'StreetNetwork Backend valhalla is created'

    resp = api_get('/v0/streetnetwork_backends')
    assert 'streetnetwork_backends' in resp
    assert len(resp['streetnetwork_backends']) == 3

    # Update existing backend
    new_backend['args'] = {}
    new_backend['args']['url'] = 'valhalla.url.update'
    resp = api_put(
        'v0/streetnetwork_backends/valhalla', data=ujson.dumps(new_backend), content_type='application/json'
    )
    assert 'message' in resp
    assert resp['message'] == 'StreetNetwork Backend valhalla from db is updated'

    resp = api_get('/v0/streetnetwork_backends/valhalla')
    assert 'streetnetwork_backends' in resp
    assert len(resp['streetnetwork_backends']) == 1
    assert resp['streetnetwork_backends'][0]['args']['url'] == 'valhalla.url.update'


def test_streetnetwork_backend_delete(default_streetnetwork_backend):
    """
    Test that a 'deleted' backend isn't returned when querying all backends, and that its 'discarded' parameter is set to True
    """
    resp = api_get('/v0/streetnetwork_backends')
    assert 'streetnetwork_backends' in resp
    assert len(resp['streetnetwork_backends']) == 2

    _, status_code = api_delete('v0/streetnetwork_backends/kraken', check=False, no_json=True)
    assert status_code == 204

    resp = api_get('/v0/streetnetwork_backends')
    assert 'streetnetwork_backends' in resp
    assert len(resp['streetnetwork_backends']) == 1

    resp = api_get('/v0/streetnetwork_backends/kraken')
    assert 'streetnetwork_backends' in resp
    assert len(resp['streetnetwork_backends']) == 1
    assert resp['streetnetwork_backends'][0]['discarded']


def test_streetnetwork_backend_schema():
    """
    Test that a backend isn't created in db when missing required parameters
    """

    def send_and_check(backend_id, json_data, missing_param):
        resp, status = api_put(
            url='v0/streetnetwork_backends/{}'.format(backend_id),
            data=ujson.dumps(json_data),
            content_type='application/json',
            check=False,
        )
        assert status == 400
        assert 'message' in resp
        assert resp['message'] == "'{}' is a required property".format(missing_param)
        assert 'status' in resp
        assert resp['status'] == "invalid data"

    # 'klass' is missing
    corrupted_backend = {'args': {'url': 'kraken.url', 'fail_max': 5, 'timeout': 1}}
    send_and_check('kraken', corrupted_backend, 'klass')