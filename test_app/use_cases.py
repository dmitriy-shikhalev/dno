from typing import List, Optional

from pydantic import BaseModel

from dno.client_action import ClientActionField
from dno.use_case import UseCase

from . import models


class Server(UseCase):  # Abstract class
    get_vcs = ClientActionField(
        name='Get VC list',
        args=BaseModel,
        result=models.VCList
    )


class CreateServer(Server):
    name: str
    cpu: int
    memory: int
    hdd: int

    result: models.CreateServerResult

    create_vm = ClientActionField(
        name='Create Virtual Machine',
        args=models.CreateVMArgs,
        result=models.CreateVMResult,
    )

    install_os = ClientActionField(
        name='Install operation system on VM',
        args=models.InstallOSArgs,
        result=models.InstallOSResult,
    )

    async def get_appropriate_vc(self, vcs: List[models.VC]) -> Optional[models.VC]:
        for vc in vcs:
            if (
                vc.cpu_available >= self.cpu
                and vc.memory_available >= self.memory
                and vc.hdd_available >= self.memory
            ):
                return vc

    async def run(self):
        vcs = await self.get_vcs()
        vc = await self.get_appropriate_vc(vcs.result)
        if vc is None:
            raise Exception(f'No appropriate VC for cpu {self.cpu} memory {self.memory} hdd {self.hdd}')

        vm_id = await self.create_vm(name=self.name, cpu=self.cpu, memory=self.memory, hdd=self.hdd)
        vm_id = vm_id.id

        os_result = await self.install_os(id=vm_id)

        return {
            'id': vm_id,
            'os': os_result.os,
            'username': os_result.username,
            'password': os_result.password,
            'ip': os_result.ip,
        }
