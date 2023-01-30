"""
Command-line interface for SNNgine3D.

Copyright 2023 hsc-projects

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing
permissions and limitations under the License.

"""

import logging
import sys
import typer

from snngine3d import __title__, __version__, __copyright__


logger = logging.getLogger(__package__)
cli = typer.Typer()


@cli.command()
def run(config: str = '', verbose: bool = False) -> None:
    """
    Get info about SNNgine3D.

    Args:
        config: Name or path to network config
        verbose: Output more info

    Example:
        To call this, run: ::

            snngine3d --config
    """
    typer.echo(f"{__title__} version {__version__}, {__copyright__}")
    total = 0
    eng = Engine()
    eng.load(config)
    if sys.flags.interactive != 1:
        eng.run()


if __name__ == "__main__":
    cli()
