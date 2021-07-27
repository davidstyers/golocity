import os
import subprocess
import sys


sys.path.append(os.path.dirname(__file__))  # noqa


if __name__ == "__main__":
    if not os.path.exists("RELEASE.rst"):
        print("Not releasing a new version because there isn't a RELEASE.md file.")
        subprocess.check_output(["circleci", "step", "halt"]).decode("ascii").strip()
