import ast
import os
import subprocess
import sys
from pathlib import Path
from typing import BinaryIO, Iterator, Optional, TextIO

import docker

from golocity import TMP_DOCKERFILE
from golocity.helpers import log


class ImageClient:
    """
    Handles all image manipulations made by Golocity.
    """

    def __init__(self, project_path: Path, dockerfile_path: Path, image_id: Optional[str]) -> None:
        self.docker_client: docker.DockerClient = self.setup_docker()
        self.path = project_path
        self.golocity_path: Path = self.path.joinpath(".golocity")
        self.tmp_file: Path = self.path.joinpath(TMP_DOCKERFILE)
        self.command: list = self.clean_dockerfile(dockerfile=dockerfile_path)
        self.id = image_id

    @staticmethod
    def setup_docker() -> Optional[docker.DockerClient]:
        """
        Initiates docker client and checks to make sure docker engine is running.
        :return: functional docker client
        """
        try:
            client = docker.from_env()
            return client
        except docker.errors.DockerException:
            log(
                "CRITICAL",
                "Cannot connect to the Docker daemon. Is the docker daemon running?\n",
            )
            sys.exit(1)

    def clean_dockerfile(self, dockerfile: Path) -> list:
        """
        Parses Dockerfile for CMD and ENTRYPOINT commands and removes them
        in preparation for GVMKit build.
        :param dockerfile: A path leading to a Dockerfile.
        :return: The stripped commands from the Dockerfile.
        """
        open_dockerfile: TextIO = open(dockerfile)
        tmp_dockerfile: BinaryIO = open(self.tmp_file, "w+b")
        command: Optional[list] = []

        for line in open_dockerfile:
            if line[:3] == "CMD":
                command: list = ast.literal_eval(line[3:].strip(" "))  # type: ignore[no-redef]
                continue
            elif line[:10] == "ENTRYPOINT":
                command: list = ast.literal_eval(line[10:].strip(" "))  # type: ignore[no-redef]
                continue
            tmp_dockerfile.write(line.encode())
        tmp_dockerfile.close()

        if not command:
            log("WARNING", "Cannot find ENTRYPOINT or CMD specified in Dockerfile.\n")
            sys.exit(1)

        return command

    def _build(self) -> tuple[docker.DockerClient.images, Iterator[str]]:
        image, logs = self.docker_client.images.build(
            path=str(self.path), dockerfile=self.tmp_file.name, rm=True
        )
        return image, logs

    def build_image(
            self, keep_tmp: Optional[bool] = False
    ) -> tuple[docker.DockerClient.images, Iterator[str]]:
        """
        Builds image from Dockerfile
        :param keep_tmp: Whether to keep the temporary Dockerfile or not.
        :return: A tuple containing the new Image object and a generator of
                 the build logs as JSON-decoded objects.
        """
        log("INFO", "Building image from Dockerfile at {}".format(self.path))
        image, logs = self._build()
        for chunk in logs:
            if "stream" in chunk:
                for line in chunk["stream"].splitlines():
                    log("DEBUG", "Docker: {}".format(line))

        if not keep_tmp:
            os.remove(self.tmp_file)
        self.id = image.id

        return image, logs

    def _get(self) -> docker.DockerClient.images:
        return self.docker_client.images.get(self.id)

    def get_image(self) -> docker.DockerClient.images:
        log("INFO", "Retrieving pre-built image {}".format(self.id))
        try:
            image = self._get()
        except docker.errors.ImageNotFound:
            log("CRITICAL", "The image was not found, please rebuild the project again.")
            sys.exit(1)
        except Exception as e:
            log("CRITICAL", "Docker: {}".format(e))
            sys.exit(1)
        return image

    def _run_process(self, arguments: list) -> Optional[str]:
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, cwd=self.golocity_path)
        for stdout_line in process.stdout:
            dl: str = stdout_line.decode('utf-8')
            if "success." in dl.split(" "):
                return dl.split(" ")[3]
            log("DEBUG", "gvmkit-build: {}".format(" ".join(dl.split())))

    def build_gvmkit(
            self,
            info: Optional[bool] = False,
            push: Optional[bool] = True,
    ) -> Optional[str]:
        """
        Builds image in Golem format and pushes new image to Golem repo.
        :param image: An Image object.
        :param info: Whether to preform a dry run or not.
        :param push: Whether to push the image or not.
        :return: The hash of the pushed image.
        """
        # Currently, gvmkit_build is optimised for command line use only.
        # While this is suboptimal, it is the best way possible for now.
        log("INFO", "Building Golem virtual machine from image {}".format(self.id))
        gvmkit_hash: str = ""
        args = ["python", "-m", "gvmkit_build", self.id]
        if info:
            args.append("--info")

        try:
            self._run_process(args)
            # gvmkit_build has a bug where it won't push an image unless already built.
            if push:
                args.append("--push")
                self._run_process(args)
                return gvmkit_hash
        except Exception as e:
            log("CRITICAL", str(e))
            sys.exit(1)
