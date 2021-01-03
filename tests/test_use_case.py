import asyncio
from typing import Dict

from pydantic import BaseModel

from dno import client_action, use_case


class ClientActionArgsBaseModel(BaseModel):
    x: int
    y: float
    z: str


class ClientActionReturnBaseModel(BaseModel):
    a: str
    b: Dict[str, int]


class ReturnBaseModel(BaseModel):
    a: str
    b: Dict[str, int]


class DummyUseCase(use_case.UseCase):
    a: int
    b: float
    xx = client_action.ClientActionField(
        name='xx',
        args=ClientActionArgsBaseModel,
        result=ClientActionReturnBaseModel,
    )
    result: ReturnBaseModel

    async def run(self):
        a = 1
        b = 1.1
        c = 'abc'
        ca = await self.xx(x=a, y=b, z=c)
        ca.set_running()
        ca.set_result({'a': str(int(a**b) * 500), 'b': {'x': 5, 'y': a * a}})
        while not ca.is_finished():
            await asyncio.sleep(0)

        assert ca.status.value == 'DONE'
        assert ca.name == 'xx'

        return ca.result


async def test():
    uc = DummyUseCase(a=4, b=3.14)
    await uc.start()
    result = await uc.run()

    assert result == {'a': '500', 'b': {'x': 5, 'y': 1}}
