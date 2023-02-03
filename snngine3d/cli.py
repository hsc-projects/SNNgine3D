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
# from typing import Optional

# from main import launch_engine
from snngine3d.engine import Engine


logger = logging.getLogger(__package__)
cli = typer.Typer()


@cli.command()
def run(config_model: str = 'config_models.DefaultEngineConfig', verbose: bool = False) -> None:
    """
    Get info about SNNgine3D.

    Args:
        config_model: Name or path to network config
        verbose: Output more info

    Example:
        To call this, run: ::

            snngine3d --config
    """

    try:
        from snngine3d import __title__, __version__, __copyright__
        typer.echo(f"{__title__} version {__version__}, {__copyright__}")

        components = config_model.split('.')
        config = __import__("snngine3d")

        for comp in components:
            config = getattr(config, comp)
    except ImportError:
        components = config_model.split('.')
        config = __import__(components[0])

        for comp in components[1:]:
            config = getattr(config, comp)

    typer.echo(f"\nInitializing Engine with {config_model}")

    eng = Engine(config=config())

    if sys.flags.interactive != 1:
        eng.run(allow_interactive=True)


if __name__ == "__main__":
    cli()
    # launch_engine()
