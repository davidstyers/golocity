import asyncio
import json
import sys
from configparser import ConfigParser
from pathlib import Path

import typer
from yapapi.log import enable_default_logger

from golocity import CONF
from golocity.helpers import log
from golocity.yagna import YagnaClient


def deploy(
    budget: float = typer.Argument(
        default=None,
        help="The limit to spend on deploying the project.",
    ),
    subnet: str = typer.Option(
        default="mainnet",
        help="Which subnet to deploy the project to.",
    ),
) -> None:
    """
    Deploys project to the Golem Network.
    :param budget: The limit to spend on deploying the project.
    :param subnet: Which subnet to deploy the project to.
    :return: None
    """
    path: Path = CONF["path"]
    config: ConfigParser = CONF["config"]
    golocity_path: Path = path.joinpath(".golocity")

    log("INFO", "Deploying project to Golem Network.")

    if golocity_path.is_dir():
        try:
            enable_default_logger()
            ya_client = YagnaClient(
                vm_hash=config["DEFAULT"]["gvmkit_hash"],
                command=json.loads(config["DEFAULT"]["command"]),
                budget=budget,
                subnet=subnet,
            )
            loop = asyncio.get_event_loop()
            task = loop.create_task(ya_client.main())
            loop.run_until_complete(task)
        except KeyError:
            log(
                "CRITICAL",
                "Golocity does not have all the parameters needed"
                "to deploy this project.\n"
                "Try building the project and try again.",
            )
            sys.exit(1)
        except Exception as e:
            log("CRITICAL", str(e))
            sys.exit(1)
