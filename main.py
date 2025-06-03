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
  type=click.Choice(["stdio", "sse", "http"], case_sensitive=False),
  default="sse",
  help="Transport type",
)
def main(port: int, transport: str) -> int:
  load_symbols()
  if transport == "http":
    transport = "streamable-http"
  mcp_app.run(transport)  # type: ignore
  return 0


if __name__ == "__main__":
  main()
