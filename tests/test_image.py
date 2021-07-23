from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

import pytest

import typer

from golocity.image import ImageClient
from golocity.main import create_golocity


app: typer.Typer = create_golocity()

ENTRYPOINT_DOCKERFILE = """
FROM python:3

WORKDIR /usr/src/app

COPY . .

ENTRYPOINT [ "python", "./hello-world.py" ]
"""

CMD_DOCKERFILE = """
FROM python:3

WORKDIR /usr/src/app

COPY . .

ENTRYPOINT [ "python", "./hello-world.py" ]
"""


class TestImage:
    def __init__(self, img_id: Optional[str]):
        self.id = img_id


@pytest.fixture
def project_directory(request) -> Path:
    # Make a new directory and provide the path a Path object.
    # Will remove the directory when complete.
    with TemporaryDirectory() as tempdir:
        project_path: Path = Path(tempdir)
        dockerfile_path: Path = project_path.joinpath("Dockerfile")
        with open(dockerfile_path, "w") as file:
            if request.param == "CMD":
                file.write(CMD_DOCKERFILE)
            elif request.param == "ENTRYPOINT":
                file.write(ENTRYPOINT_DOCKERFILE)
        yield project_path


@pytest.mark.parametrize("project_directory", ["CMD", "ENTRYPOINT"], indirect=True)
def test_clean_cmd_dockerfile(project_directory: Path, mocker) -> None:
    dockerfile = Path(project_directory).joinpath("Dockerfile")
    mocker.patch("golocity.image.ImageClient.setup_docker", return_value=None)
    image = ImageClient(
        project_path=project_directory, dockerfile_path=dockerfile, image_id=None
    )
    assert image.command == ["python", "./hello-world.py"]


@pytest.mark.parametrize("project_directory", ["ENTRYPOINT"], indirect=True)
def test_build_image(project_directory: Path, mocker) -> None:
    dockerfile = Path(project_directory).joinpath("Dockerfile")
    test_class = TestImage(img_id="test")
    mocker.patch("golocity.image.ImageClient.setup_docker", return_value=None)
    mocker.patch(
        "golocity.image.ImageClient._build", return_value=(test_class, "This is a test")
    )
    image = ImageClient(
        project_path=project_directory, dockerfile_path=dockerfile, image_id=None
    )
    assert image.build_image() == (test_class, "This is a test")


@pytest.mark.parametrize("project_directory", ["ENTRYPOINT"], indirect=True)
def test_get_image(project_directory: Path, mocker) -> None:
    dockerfile = Path(project_directory).joinpath("Dockerfile")
    mocker.patch("golocity.image.ImageClient.setup_docker", return_value=None)
    mocker.patch("golocity.image.ImageClient._get", return_value=None)
    image = ImageClient(
        project_path=project_directory, dockerfile_path=dockerfile, image_id=None
    )
    assert image.get_image() is None


@pytest.mark.parametrize("project_directory", ["ENTRYPOINT"], indirect=True)
def test_build_gvmkit(project_directory: Path, mocker) -> None:
    dockerfile = Path(project_directory).joinpath("Dockerfile")
    mocker.patch("golocity.image.ImageClient.setup_docker", return_value=None)
    mocker.patch("golocity.image.ImageClient._run_process", return_value=None)
    image = ImageClient(
        project_path=project_directory, dockerfile_path=dockerfile, image_id=None
    )
    assert image.build_gvmkit() == ""
