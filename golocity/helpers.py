import configparser
import logging
from pathlib import Path

import typer

from golocity import CONFIGURATION_FILE


def init_config(project_path: Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    file_path = project_path.joinpath(CONFIGURATION_FILE)
    if file_path.exists():
        config.read(file_path)
    else:
        config["DEFAULT"] = {}
        config["DEFAULT"]["image_id"] = ""
        config["DEFAULT"]["command"] = ""
        config["DEFAULT"]["gvmkit_hash"] = ""
    return config


def init_logging(level: str) -> None:
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(level))
    logging.basicConfig(
        filename=".golocity/golocity.log",
        filemode="w",
        level=numeric_level,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    )


def log(level: str, msg: str) -> None:
    logging.getLogger(__name__)
    colors: dict[str, str] = {
        "DEBUG": typer.colors.CYAN,
        "INFO": typer.colors.GREEN,
        "WARNING": typer.colors.YELLOW,
        "CRITICAL": typer.colors.RED,
    }
    numeric_level = getattr(logging, level.upper(), None)
    typer.echo(
        typer.style(
            msg,
            fg=colors[level],
        )
    )
    logging.log(level=numeric_level, msg=msg)
