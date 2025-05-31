from pathlib import Path

from mcp.server import Server
from mcp.types import Tool

def serve(db_sqlite_path: Path, metadata_yml_path: Path) -> None:
    server = Server(db_sqlite_path.basename)

    @server.list_tools()
    def list_tools() -> list[Tool]:
        """List available local data tools"""
        return [
            Tool(
                name="get_dataset_description",
                description="Get the description of the dataset. HIGHLY RECOMMENDED to run this first to understand what this data is.",
            ),
            Tool(
                name="list_tables",
                description="List tables in the dataset."
            ),
            Tool(
                name="run_query",
                description="Run a query against the data."
            )
        ]