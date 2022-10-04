from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient

from .decorators import get, post
from .routable import Routable


class ExampleRoutable(Routable):
    prefix = "/api/v1/testing"
    def __init__(self, injected: int) -> None:
        super().__init__()
        self.__injected = injected

    @get(path='/add/{x}')
    def add(self, x: int) -> int:
        return x + self.__injected

    @post(path='/sub/{x}')
    def sub(self, x: int) -> int:
        return x - self.__injected

    @get(path='/async')
    async def do_async(self) -> int:
        return self.__injected + 1

    @get(path='/aecho/{val}', response_class=PlainTextResponse)
    async def aecho(self, val: str) -> str:
        return f'{val} {self.__injected}'


def test_routes_respond() -> None:
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)

    response = client.get('/api/v1/testing/add/22')
    assert response.status_code == 200
    assert response.text == '24'

    response = client.post('/api/v1/testing/sub/4')
    assert response.status_code == 200
    assert response.text == '2'


def test_routes_only_respond_to_method() -> None:
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)

    response = client.post('/api/v1/testing/add/22')
    assert response.status_code == 405
    response = client.put('/api/v1/testing/add/22')
    assert response.status_code == 405
    response = client.delete('/api/v1/testing/add/22')
    assert response.status_code == 405

    response = client.get('/api/v1/testing/sub/4')
    assert response.status_code == 405
    response = client.put('/api/v1/testing/sub/4')
    assert response.status_code == 405
    response = client.delete('/api/v1/testing/sub/4')
    assert response.status_code == 405


def test_async_methods_work() -> None:
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)

    response = client.get('/api/v1/testing/async')
    assert response.status_code == 200
    assert response.text == '3'

    # Make sure we can call it more than once.
    response = client.get('/api/v1/testing/async')
    assert response.status_code == 200
    assert response.text == '3'


def test_async_methods_with_args_work() -> None:
    app = FastAPI()
    t = ExampleRoutable(2)
    app.include_router(t.router)

    client = TestClient(app)

    response = client.get('/api/v1/testing/aecho/hello')
    assert response.status_code == 200
    assert response.text == 'hello 2'
