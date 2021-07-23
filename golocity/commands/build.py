import json
from configparser import ConfigParser
from pathlib import Path
from typing import Iterator

import docker
import typer

from golocity import CONF, CONFIGURATION_FILE
from golocity.helpers import log
from golocity.image import ImageClient


def build(
    dockerfile: str = typer.Option(
        default="Dockerfile",
        help="The name of the Dockerfile for the project.",
    ),
    info: bool = typer.Option(
        default=False,
        help="Preform a test build without creating image "
        "and pushing image to the Golem repository.",
        is_flag=True,
    ),
    push: bool = typer.Option(
        default=True,
        help="Push created image to Golem repository.",
        is_flag=True,
    ),
    keep_docker_image: bool = typer.Option(
        default=False,
        help="Keep the docker image if already built.",
        is_flag=True,
        metavar="keep-docker-image",
    ),
    keep_tmp: bool = typer.Option(
        default=False,
        help="Keep the temporary Dockerfile used by Golocity.",
        is_flag=True,
        metavar="keep-tmp",
    ),
) -> None:
    """
    Prepares and builds image, saves pertinent information in the
    project config file.
    :param dockerfile: The name of the Dockerfile for the project.
    :param info: Preform a test build without creating image and
                 pushing image to the Golem repository.
    :param push: Push created image to Golem repository.
    :param keep_docker_image: Keep the docker image if already built.
    :param keep_tmp: Keep the temporary Dockerfile used by Golocity.
    :return: None
    """
    path: Path = CONF["path"]
    config: ConfigParser = CONF["config"]
    golocity_path: Path = path.joinpath(".golocity")
    golocity_path.mkdir(exist_ok=True)

    dockerfile_path: Path = path.joinpath(dockerfile)
    image_client: ImageClient = ImageClient(
        project_path=path,
        dockerfile_path=dockerfile_path,
        image_id=config["DEFAULT"]["image_id"],
    )
    if keep_docker_image:
        image: docker.DockerClient.images = image_client.get_image()
    else:
        converted_image: docker.DockerClient.images
        logs: Iterator[str]
        image, logs = image_client.build_image(keep_tmp=keep_tmp)

    config["DEFAULT"]["command"] = json.dumps(image_client.command)
    vm_hash = image_client.build_gvmkit(info=info, push=push)

    config["DEFAULT"]["image_id"] = image.id
    if vm_hash is not None:
        config["DEFAULT"]["gvmkit_hash"] = vm_hash

    with open(golocity_path.joinpath(CONFIGURATION_FILE), "w") as config_file:
        config.write(config_file)

    log("INFO", "Successfully built project 🎉")
