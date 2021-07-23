from typing import AsyncGenerator, AsyncIterable

from yapapi import Golem, Task, WorkContext
from yapapi.payload import vm

from golocity.helpers import log


class YagnaClient:
    def __init__(self, vm_hash: str, command: list, budget: float, subnet: str):
        self.vm_hash: str = vm_hash
        self.command: list = command
        self.budget: float = budget
        self.subnet: str = subnet

    async def worker(self, context: WorkContext, tasks: AsyncIterable[Task]) -> AsyncGenerator:
        async for task in tasks:
            command = " ".join(self.command)
            context.run('/bin/bash', '-c', command)

            future_results = yield context.commit()
            results = await future_results
            task.accept_result(result=results[-1])

    async def main(self) -> None:
        package = await vm.repo(
            image_hash=self.vm_hash,
        )

        tasks: list = [Task(data=None)]

        async with Golem(budget=self.budget, subnet_tag=self.subnet) as golem:
            async for completed in golem.execute_tasks(  # type: ignore[attr-defined]
                self.worker, tasks, payload=package
            ):
                log("WARNING", "Yagna: {}".format(completed.result.stdout))
