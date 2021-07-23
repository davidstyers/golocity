from typing import Optional


def hello_world(who: Optional[str]) -> None:
    if not who:
        print("Hello World!")
    else:
        print("{} says hello_world!".format(who))


if __name__ == "__main__":
    hello_world(who=None)
