from typing import Any, TypeVar, Dict, List, Optional, Callable
from functools import partial

T = TypeVar('T')


class TimeoutException(Exception):
    pass


class TaskParams:
    def __init__(
        self,
        friend: str,
        task_name: str,
        callback: Optional[Callable] = None,
        args: Optional[List[str]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ):
        from pydantic import BaseModel

        class _TaskModel(BaseModel):
            friend: str
            task_name: str
            callback: Optional[Callable]
            args: Optional[List[str]]
            kwargs: Optional[Dict[str, Any]]
            timeout: int

        # Validate using Pydantic, but don't subclass to keep it lazy
        validated = _TaskModel(
            friend=friend,
            task_name=task_name,
            callback=callback,
            args=args,
            kwargs=kwargs,
            timeout=timeout
        )

        self.friend = validated.friend
        self.task_name = validated.task_name
        self.callback = validated.callback
        self.args = validated.args or []
        self.kwargs = validated.kwargs or {}
        self.timeout = validated.timeout


class TaskManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        from dotenv import load_dotenv
        from kimera.Bootstrap import Bootstrap

        load_dotenv()
        boot = Bootstrap()

        if boot.celery_on:
            from celery import Celery

            self._celery_app = Celery(
                broker=boot.celery_broker,
                backend=boot.celery_backend,
                backend_retry=True,
                broker_retry=True
            )
            self._friends = boot.celery_friends
        else:
            self._celery_app = None

        self._initialized = True

    @property
    def celery_app(self):
        return self._celery_app

    @property
    def friends(self):
        return self._friends

    async def send_async(self, task_name, friend, args=None, kwargs=None, callback=None, func=None, poll_start=0.1, max_poll=1):
        import asyncio
        import celery.result
        from kimera.helpers.Helpers import Helpers

        if self.celery_app is None:
            raise Exception("Microservice has no celery instance")
        if friend not in self.friends:
            raise Exception(f"{friend} is not registered as friend")

        friend = self.friends[friend]
        result = self.celery_app.send_task(
            f"{friend['route']}.{task_name}",
            args=args,
            kwargs=kwargs,
            result_cls=celery.result.AsyncResult,
            queue=friend['queue']
        )

        async def do_result(_result, start, limit):
            Helpers.sysPrint(f"Polling {friend['route']}", f"{task_name}")
            while not _result.successful():
                await asyncio.sleep(min(start, limit))
                start *= 2

            if callback:
                await callback(_result.get())
            if func:
                func(_result.get())

            _result.forget()
            _result.revoke(terminate=True, signal='SIGKILL')

        return asyncio.create_task(do_result(_result=result, start=poll_start, limit=max_poll))

    async def paraSyncTasks(self, taskList: List[TaskParams]):
        if self.celery_app is None:
            raise Exception("Microservice has no celery instance")

        tasks = [
            self.send_await(
                friend=task.friend,
                task_name=task.task_name,
                args=task.args,
                kwargs=task.kwargs,
                timeout=task.timeout
            )
            for task in taskList if task.friend in self.friends
        ]

        import asyncio
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def paraTasks(self, taskList: List[TaskParams], gather_callback: Optional[Callable] = None):
        if self.celery_app is None:
            raise Exception("Microservice has no celery instance")

        import asyncio

        to_send = [
            asyncio.create_task(
                self.send_async(
                    friend=task.friend,
                    task_name=task.task_name,
                    args=task.args,
                    kwargs=task.kwargs,
                    callback=task.callback
                )
            )
            for task in taskList if task.friend in self.friends
        ]

        if gather_callback and asyncio.iscoroutinefunction(gather_callback):
            gather = asyncio.create_task(asyncio.gather(*to_send))
            gather.add_done_callback(lambda res: asyncio.create_task(gather_callback(res.result())))
        else:
            return await asyncio.gather(*to_send)

    def _get_callback_wrapper(self):
        from functools import partial

        async def callback_wrapper(result, index, taskList):
            task = taskList[index]

            if task.kwargs is None:
                task.kwargs = {}

            bound_callback = partial(callback_wrapper, index=index + 1, taskList=taskList)

            if index + 1 == len(taskList):
                bound_callback = task.callback if task.callback else lambda result: True if result else False

            if task.friend in self.friends:
                if isinstance(result, dict):
                    task.kwargs.update(result)
                elif isinstance(result, list):
                    task.args.extend(result)
                else:
                    task.kwargs["payload"] = result

                await self.send_async(
                    friend=task.friend,
                    task_name=task.task_name,
                    args=task.args,
                    kwargs=task.kwargs,
                    callback=bound_callback
                )

        return callback_wrapper

    async def chainSyncTasks(self, taskList: List[TaskParams]):
        from kimera.helpers.Helpers import Helpers

        if self.celery_app is None:
            raise Exception("Microservice has no celery instance")
        if len(taskList) < 2:
            raise Exception("Chain must have at least two tasks")

        result = None
        for task in taskList:
            if task.friend not in self.friends:
                raise Exception(f"{task.friend} is not registered as a friend")

            args = task.args
            kwargs = task.kwargs

            if result is not None:
                if isinstance(result, dict):
                    task.kwargs.update(result)
                elif isinstance(result, list):
                    task.args.extend(result)
                else:
                    task.kwargs["payload"] = result

            result = await self.send_await(
                task_name=task.task_name,
                friend=task.friend,
                args=args,
                kwargs=kwargs,
                timeout=task.timeout
            )

            Helpers.sysPrint(f"Task {task.task_name} result:", result)

        return result

    async def chainTasks(self, taskList: List[TaskParams]):
        import asyncio

        if self.celery_app is None:
            raise Exception("Microservice has no celery instance")
        if len(taskList) < 2:
            raise Exception("Chain must have at least two tasks")

        task = taskList[0]

        if task.friend in self.friends:
            bound_callback = partial(self._get_callback_wrapper(), index=1, taskList=taskList)

            return asyncio.create_task(self.send_async(
                friend=task.friend,
                task_name=task.task_name,
                args=task.args,
                kwargs=task.kwargs,
                callback=bound_callback
            ))

    async def send_await(self, task_name, friend, args=None, kwargs=None, timeout=30, poll_start=0.1, max_poll=1):
        import asyncio
        import celery.result
        from kimera.helpers.Helpers import Helpers

        if self.celery_app is None:
            raise Exception("Microservice has no celery instance")
        if friend not in self.friends:
            raise Exception(f"{friend} is not registered as friend")

        friend = self.friends[friend]
        result = self.celery_app.send_task(
            f"{friend['route']}.{task_name}",
            args=args,
            kwargs=kwargs,
            result_cls=celery.result.AsyncResult,
            queue=friend['queue']
        )

        Helpers.sysPrint(f"Polling {friend['route']}", f"{task_name}")

        async def poll_result(_result, start=0.1, limit=1):
            while not _result.successful():
                await asyncio.sleep(min(start, limit))
                start *= 2
            return _result.get()

        try:
            result_data = await asyncio.wait_for(
                poll_result(_result=result, start=poll_start, limit=max_poll),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutException(f"Task {task_name} timed out after {timeout} seconds.")

        result.forget()
        result.revoke(terminate=True, signal='SIGKILL')

        return result_data
