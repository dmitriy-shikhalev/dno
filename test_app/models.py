from enum import Enum
from typing import List

from pydantic import BaseModel


class VC(BaseModel):
    cpu_available: int
    memory_available: int
    hdd_available: int
    cpu: int
    memory: int
    hdd: int


class VCList(BaseModel):
    result: List[VC]


class CreateVMArgs(BaseModel):
    name: str
    cpu: int
    memory: int
    hdd: int


class CreateVMResult(BaseModel):
    id: str


class OSEnum(Enum):
    WINDOWS = 'WINDOWS'
    LINUX = 'LINUX'


class InstallOSArgs(BaseModel):
    id: str


class InstallOSResult(BaseModel):
    id: str
    os: OSEnum
    username: str
    password: str


class CreateServerResult(BaseModel):
    id: str
    os: OSEnum
    username: str
    password: str
    ip: str
