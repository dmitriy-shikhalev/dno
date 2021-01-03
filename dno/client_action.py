import asyncio
from enum import Enum
from typing import Any, Dict, Optional, Type, Union
from uuid import uuid4

from pydantic import BaseModel


class BadClientActionDeclaration(Exception):
    pass


class BadArgument(Exception):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'Bad argument: {self.name}'


# class NoArgument(BadArgument):
#     def __repr__(self):
#         return f'No argument: {self.name}'
#
#
# class BadArgumentValueType(BadArgument):
#     def __init__(self, name: str, value: Any, type_: Type):
#         self.name = name
#         self.value = value
#         self.type = type_
#
#     def __repr__(self):
#         return f'Bad argument {self.name} value type: {self.value}, must be {self.type}'


class UnexpectedStatus(Exception):
    pass


class Status(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    DONE = 'DONE'
    ERROR = 'ERROR'


class ClientActionField:
    args: BaseModel
    result: BaseModel

    def __init__(self, name: str, args, result):
        if not issubclass(args, BaseModel):
            raise BadClientActionDeclaration(f'{self.__class__.__name__}.args')
        if not issubclass(result, BaseModel):
            raise BadClientActionDeclaration(f'{self.__class__.__name__}.result')
        self.name = name
        self.__annotations__['args'] = args
        self.__annotations__['result'] = result

    async def __call__(self, **kwargs):
        # Check arguments
        self.args = self.__annotations__['args'](**kwargs)

        id = uuid4().hex
        # TODO Подумать: надо ли присваивать id здесь или внутри класса Storage

        client_action = ClientAction(self.name, id, kwargs, Status.PENDING)

        await Storage.add(client_action)

        return client_action


class ClientAction:
    __slots__ = ('id', 'name', 'args', 'status', 'result', 'error')

    id: str
    name: str
    status: Status
    args: Dict[str, Any]
    result: Optional[Dict]
    error: Optional[Dict]

    def __init__(self, name: str, id: str, args: Dict[str, Any], status: Status):
        self.id = id
        self.name = name
        self.args = args
        self.status = status
        self.result = None
        self.error = None

    def __repr__(self):
        return f'ClientAction({self.id}, {self.name}, {self.status}, {self.result}, {self.error})'

    def set_running(self):
        if self.status != Status.PENDING:
            raise UnexpectedStatus(self.status)
        self.status = Status.RUNNING

    def set_result(self, result: Optional[Dict] = None):
        if self.status != Status.RUNNING:
            raise UnexpectedStatus(self.status)
        self.status = Status.DONE
        self.result = result # or {}

    def set_error(self, error: Optional[Dict] = None):
        if self.status != Status.RUNNING:
            raise UnexpectedStatus(self.status)
        self.status = Status.ERROR
        self.error = error # or {}

    def is_finished(self):
        return self.status in (
            Status.DONE,
            Status.ERROR,
        )

    async def wait(self):
        while not self.is_finished():
            await asyncio.sleep(0)  # TODO sleep(0) or sleep(N)?


class Storage:
    _STORAGE: Dict[str, ClientAction] = {}

    def __init__(self):
        # Only class methods are allowed
        # (singleton pattern)
        raise NotImplementedError

    @classmethod
    async def get(cls, id: str):
        return cls._STORAGE[id]

    @classmethod
    async def add(cls, client_action: ClientAction):
        cls._STORAGE[client_action.id] = client_action

    @classmethod
    async def delete(cls, id: str):
        del cls._STORAGE[id]
