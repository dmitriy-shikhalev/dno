import asyncio
import inspect
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel

# from . import client_action


__all__ = ['UseCase', 'Status']


REGISTERED = {}

RUNNING_TASKS = {}


class Status(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    FINISHED = 'DONE'
    FAILED = 'ERROR'


class UseCase(metaclass=ABCMeta):
    id: str
    status: Status = Status.PENDING
    error: Optional[Dict[str, Any]]
    result: Optional[BaseModel]

    def __init_subclass__(cls, **kwargs):
        if not inspect.isabstract(cls):
            if not cls.__annotations__.get('result') or \
                    not issubclass(cls.__annotations__.get('result'), BaseModel):
                raise Exception('No result type', cls.__name__, cls.__annotations__)

            REGISTERED[cls.__name__] = cls

    def __init__(self, **kwargs):
        # Check args of __init__
        annotations = set(self.__annotations__.keys())
        for k, v in kwargs.items():
            type_ = self.__annotations__[k]
            if not isinstance(v, type_):
                raise RuntimeError(f'Value "{v}" is not instance of class {type_}')
            setattr(self, k, v)
            annotations.remove(k)

        annotations -= {'id', 'status', 'result', 'error'}
        if annotations:
            raise RuntimeError(
                f'Not all arguments are got in instance.__init__ of class {self.__class__}: {annotations}'
            )

        self.id = uuid4().hex

    @abstractmethod
    async def run(self):
        pass

    async def start(self):
        if self.status != Status.PENDING:
            raise Exception('Can\'t start use case twice')

        loop = asyncio.get_event_loop()
        loop.create_task(self.run())
        RUNNING_TASKS[self.id] = self

        self.status = Status.RUNNING  # TODO ???? Возможно это все не нужно, чтобы запускать из базы данных объекты
