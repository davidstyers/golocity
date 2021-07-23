from pathlib import Path

import typer

from golocity import CONF, PROJECT_ART, VERSION
from golocity.helpers import init_config, init_logging, log


def main(
    path: Path = typer.Option(
        default=Path("."),
        help="The path to the project.",
    ),
    level: str = typer.Option(
        default="DEBUG",
        help="The level to set the logger.",
    ),
    art: bool = typer.Option(
        default=True,
        help="Whether to display terminal art or not.",
        is_flag=True,
    ),
) -> None:
    """
    Main entrypoint for Golocity
    :param path: The path to the project.
    :param level: The level to set the logger.
    :param art: Whether to display terminal art or not.
    :return: None
    """
    if art:
        PROJECT_ART

    golocity_path: Path = path.joinpath(".golocity")
    golocity_path.mkdir(exist_ok=True)
    init_logging(level=level)
    log("INFO", "Started Golocity, version {}".format(VERSION))
    CONF["path"] = path
    CONF["config"] = init_config(project_path=golocity_path)


def create_golocity() -> typer.Typer:
    from golocity.commands import build, deploy

    app: typer.Typer = typer.Typer()

    app.command(
        help="Prepares and builds image, saves pertinent information"
        "in the project configuration file."
    )(build.build)

    app.command(help="Deploys project to the Golem Network.")(deploy.deploy)

    app.callback(
        help="Golocity version "
        + typer.style("{}".format(VERSION), fg=typer.colors.MAGENTA)
    )(main)

    return app


golocity: typer.Typer = create_golocity()
