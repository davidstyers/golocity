import pkg_resources
import typer

TMP_DOCKERFILE: str = "Dockerfile.golocity"
VERSION: str = pkg_resources.get_distribution("golocity").version
CONFIGURATION_FILE: str = "golocity.ini"
# Holds config file and path information from main callback.
CONF: dict = {}

PROJECT_ART: str = typer.echo(
    """
      ____       _            _ _
     / ___| ___ | | ___   ___(_) |_ _   _
    | |  _ / _ \| |/ _ \ / __| | __| | | |
    | |_| | (_) | | (_) | (__| | |_| |_| |
     \____|\___/|_|\___/ \___|_|\__|\__, |
                                    |___/
            """
)
