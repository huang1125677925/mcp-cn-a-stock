from typing import Literal

from dotenv import load_dotenv

load_dotenv(override=True)
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

import click

from qtf_mcp import mcp_app
from qtf_mcp.symbols import load_symbols


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
  "--transport",
  type=click.Choice(["stdio", "sse"]),
  default="stdio",
  help="Transport type",
)
def main(port: int, transport: Literal["stdio", "sse", "streamable-http"]) -> int:
  load_symbols()
  mcp_app.run(transport)
  return 0


if __name__ == "__main__":
  main()
