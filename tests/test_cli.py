import pytest
from aiohttp import web

from dno import app


@pytest.fixture
def cli(loop, aiohttp_client):
    return loop.run_until_complete(
        aiohttp_client(
            loop.run_until_complete(
                app.app_factory(['test_app'])
            )
        )
    )


@pytest.fixture
async def task(cli):
    resp = await cli.post('/test_app/call/CreateServer')
    assert resp.status == web.HTTPOk.status_code
    j = await resp.json()
    assert 'id' in j
    yield j['id']


async def test_apps(cli):
    assert cli.server.app['APPS'] == ['test_app']
    resp = await cli.get('/')
    assert resp.status == web.HTTPOk.status_code
    assert await resp.json() == ['test_app']


async def test_get_use_cases(cli):
    resp = await cli.get('/test_app/call')
    assert resp.status == web.HTTPOk.status_code
    assert 'CreateServer' in await resp.json()


async def test_get_use_cases_404(cli):
    resp = await cli.get('/no_app/call')
    assert resp.status == web.HTTPNotFound.status_code


async def test_get_call(cli):
    resp = await cli.get('/test_app/call')
    assert resp.status == web.HTTPOk.status_code
    raise NotImplementedError


async def test_post_call_404(cli):
    resp = await cli.post('/test_app/call/no_use_case')
    assert resp.status == web.HTTPNotFound.status_code


async def test_post_call(cli):
    resp = await cli.post('/test_app/call/CreateServer')
    assert resp.status == web.HTTPOk.status_code
    assert 'id' in await resp.json()


async def test_get_task_list(cli, task):
    resp = await cli.get('/test_app/task')
    assert resp.status == web.HTTPOk.status_code
    assert task in await resp.json()


async def test_get_client_action(cli, task):
    raise NotImplementedError


async def test_post_client_action(cli, task):
    raise NotImplementedError
