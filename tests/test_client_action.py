from typing import Optional

import pytest
from pydantic import BaseModel, error_wrappers

from dno import client_action


@pytest.fixture()
def return_model():
    class TestBaseModel(BaseModel):
        a: int
        b: str
        c: Optional[float]

    return TestBaseModel


@pytest.fixture()
def args_model():
    class ArgsBaseModel(BaseModel):
        a: int
        b: str
        c: Optional[float]

    return ArgsBaseModel


@pytest.fixture()
def test_client_action_field(args_model, return_model):
    ca = client_action.ClientActionField(
        name='test_client_action',
        args=args_model,
        result=return_model
    )
    return ca


@pytest.fixture()
async def test_client_action_call(loop, test_client_action_field):
    inst = await test_client_action_field(a=1, b='b', c=3.1416)
    return inst


class TestCreateInstance:
    async def test_normal(self, loop, test_client_action_field):
        inst = await test_client_action_field(a=1, b='2', c=1.3)

        assert inst.args['a'] == 1
        assert inst.args['b'] == '2'
        assert inst.args['c'] == 1.3

    async def test_without_c_arg(self, test_client_action_field):
        inst = await test_client_action_field(a=1, b='2')
        assert inst.args['a'] == 1
        assert inst.args['b'] == '2'
        try:
            inst.args['c']
        except KeyError:
            pass
        else:
            raise Exception

    async def test_without_a_arg(self, test_client_action_field):
        try:
            await test_client_action_field(c=1.2, b='2')
        except error_wrappers.ValidationError as e:
            errors = e.errors()
            assert len(errors) == 1
            assert errors[0]['loc'][0] == 'a'
            assert errors[0]['type'] == 'value_error.missing'
        else:
            raise Exception

    # async def test_with_wrong_a_type(self, test_client_action_field):
    #     try:
    #         await test_client_action_field(a=1.5, b='2', c=1.3)
    #     except error_wrappers.ValidationError as e:
    #         errors = e.errors()
    #         assert len(errors) == 1
    #         assert errors[0]['loc'][0] == 'a'
    #         assert errors[0]['type'] == 'value_error.missing'
    #     else:
    #         raise Exception

    async def test_with_wrong_c_type(self, test_client_action_field):
        try:
            await test_client_action_field(a=1, b='2', c='abc')
        except error_wrappers.ValidationError as e:
            errors = e.errors()
            assert len(errors) == 1
            assert errors[0]['loc'][0] == 'c'
            assert errors[0]['type'] == 'type_error.float'
        else:
            raise Exception


class TestFullCycleInstance:
    async def test_done(self, test_client_action_call):
        # Check id
        assert test_client_action_call.id
        assert test_client_action_call.status.value == 'PENDING'
        storage_client_action = await client_action.Storage.get(test_client_action_call.id)
        assert test_client_action_call == storage_client_action
        assert test_client_action_call is storage_client_action

        # Set running
        storage_client_action.set_running()

        # Check status
        assert storage_client_action.status.value == 'RUNNING'

        # Set result
        storage_client_action.set_result({'test': 'result'})
        storage_client_action = await client_action.Storage.get(test_client_action_call.id)
        assert storage_client_action.status.value == 'DONE'
        assert storage_client_action.result == {'test': 'result'}

        # Set result (exception)
        try:
            storage_client_action.set_result({})
        except client_action.UnexpectedStatus:
            pass
        else:
            raise Exception

        # Set error (exception)
        try:
            storage_client_action.set_error({})
        except client_action.UnexpectedStatus:
            pass
        else:
            raise Exception

    async def test_error(self, test_client_action_call):
        # Check id
        assert test_client_action_call.id
        assert test_client_action_call.status.value == 'PENDING'
        storage_client_action = await client_action.Storage.get(test_client_action_call.id)
        assert test_client_action_call == storage_client_action
        assert test_client_action_call is storage_client_action

        # Set running
        storage_client_action.set_running()

        # Check status
        assert storage_client_action.status.value == 'RUNNING'

        storage_client_action.set_error({'test': 'result'})
        storage_client_action = await client_action.Storage.get(test_client_action_call.id)
        assert storage_client_action.status.value == 'ERROR'
        assert storage_client_action.error == {'test': 'result'}

        # Set result (exception)
        try:
            storage_client_action.set_result({})
        except client_action.UnexpectedStatus:
            pass
        else:
            raise Exception

        # Set error (exception)
        try:
            await storage_client_action.set_error({})
        except client_action.UnexpectedStatus:
            pass
        else:
            raise Exception

    async def test_set_result_pending(self, test_client_action_call):
        assert test_client_action_call.status.value == 'PENDING'

        try:
            test_client_action_call.set_result()
        except client_action.UnexpectedStatus:
            pass
        else:
            raise Exception()

    async def test_set_error_pending(self, test_client_action_call):
        assert test_client_action_call.status.value == 'PENDING'

        try:
            test_client_action_call.set_error()
        except client_action.UnexpectedStatus:
            pass
        else:
            raise Exception()

    async def test_set_running_done(self, test_client_action_call):
        assert test_client_action_call.status.value == 'PENDING'

        test_client_action_call.set_running()
        test_client_action_call.set_result()

        try:
            test_client_action_call.set_running()
        except client_action.UnexpectedStatus:
            pass
        else:
            raise Exception()
