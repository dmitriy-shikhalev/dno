import importlib
import sys
from typing import List

from aiohttp import web

from .use_case import REGISTERED


async def get_apps(request):
    return web.json_response(request.app['APPS'])


class DomainApp:
    def __init__(self, name):
        self.name = name
        self.models = importlib.import_module(f'{self.name}.models')
        self.use_cases = importlib.import_module(f'{self.name}.use_cases')

    async def get_use_case_list(self, request):  # NOQA
        return web.json_response(
            list(REGISTERED.keys())
        )

    async def post_use_case(self, request):
        use_case = request.match_info.get('use_case')
        if use_case not in REGISTERED:
            raise web.HTTPNotFound(reason=f'No use case {use_case}')
        raise NotImplementedError(use_case)

    async def get_use_case(self, request):
        use_case = request.match_info.get('use_case')
        raise NotImplementedError(use_case)

    async def get_task_list(self, request):
        raise NotImplementedError

    async def get_task(self, request):
        task_id = request.match_info.get('task_id')
        raise NotImplementedError(task_id)

    async def post_client_action(self, request):
        task_id = request.match_info.get('task_id')
        raise NotImplementedError(task_id)

    async def get_client_action(self, request):
        task_id = request.match_info.get('task_id')
        raise NotImplementedError(task_id)

    def __repr__(self):
        return f'Domain App <{self.name}>'


async def read_domain_app(domain_app_name: str) -> DomainApp:
    domain_app = DomainApp(domain_app_name)
    return domain_app


async def read_domain_apps(apps: List[str]) -> List[DomainApp]:
    domain_apps = []
    for domain_app_name in apps:
        app = await read_domain_app(domain_app_name)
        domain_apps.append(app)
    return domain_apps


async def app_factory(apps: List[str]) -> web.Application:
    domain_apps = await read_domain_apps(apps)

    app = web.Application()
    app['APPS'] = apps
    app.router.add_get('/', get_apps)
    for domain_app in domain_apps:
        url = '/%s/call' % domain_app.name
        app.router.add_get(url, domain_app.get_use_case_list)

        url = '/%s/call/{use_case}' % domain_app.name
        app.router.add_post(url, domain_app.post_use_case)

        url = '/%s/call/{use_case}' % domain_app.name
        app.router.add_get(url, domain_app.get_use_case)

        url = '/%s/task' % domain_app.name
        app.router.add_get(url, domain_app.get_task_list)

        url = '/%s/task/{task_id}' % domain_app.name
        app.router.add_get(url, domain_app.get_task)

        url = '/%s/task/{task_id}/client_action' % domain_app.name
        app.router.add_post(url, domain_app.post_client_action)

        url = '/%s/task/{task_id}/client_action' % domain_app.name
        app.router.add_get(url, domain_app.get_client_action)
    return app


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: python dno/app.py domain_app_name [*domain_app_names]')

    web.run_app(
        app_factory(
            sys.argv[1:]
        )
    )
