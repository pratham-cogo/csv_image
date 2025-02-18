import logging
import os
import socket
import sys

import click
import IPython
import uvicorn
from IPython.core.profiledir import ProfileDir
from IPython.core.ultratb import VerboseTB
from IPython.terminal.ipapp import load_default_config
from database.db import create_tables, drop_tables

log = logging.getLogger(__name__)

@click.group()
def image_cli():
    os.environ["PYTHONBREAKPOINT"] = "IPython.terminal.debugger.set_trace"

@image_cli.group("server")
def image_server():
    pass

@image_server.command("develop")
def run_development_server(port: int = 8000):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", port))
            sock.close()
            break
        except OSError:
            port += 1
    if port != 8000:
        print(f"Starting server on http://127.0.0.1:{port}/")
        user_input = input("Press 'y' to continue or any other key to quit: ")
        if user_input.lower() != "y":
            return
    uvicorn.run("main:app", reload=True, port=port)

@image_server.command("shell")
@click.argument("ipython_args", nargs=-1, type=click.UNPROCESSED)
def shell(ipython_args):
    profile_name = "image"
    ProfileDir.create_profile_dir_by_name(name=profile_name, path="./")
    config = load_default_config()
    config.TerminalInteractiveShell.banner1 = f"""Python {sys.version} on {sys.platform} IPython: {IPython.__version__}"""
    config.TerminalInteractiveShell.autoindent = True
    config.InteractiveShellApp.exec_lines = [
        "%load_ext autoreload",
        "%autoreload 2",
    ]
    VerboseTB._tb_highlight = "bg:#4C5656"
    config.InteractiveShell.ast_node_interactivity = "all"
    config.InteractiveShell.debug = True
    config.TerminalInteractiveShell.highlighting_style = "paraiso-dark"
    config.TerminalIPythonApp.profile = profile_name
    config.InteractiveShell.colors = 'linux'
    IPython.start_ipython(argv=ipython_args, config=config)

@image_cli.group("database")
def database_commands():
    pass

@database_commands.command("create_tables")
def create_db_table(model):
    """Creates database tables."""
    create_tables([model])
    print("Database tables created successfully.")


@database_commands.command("drop_tables")
def drop_db_table(model):
    """Drops all database tables."""
    drop_tables([model])
    print("Database tables dropped successfully.")

def entrypoint():
    try:
        image_cli()
    except Exception as e:
        click.secho(f"ERROR: {e}", bold=True, fg="red")

if __name__ == "__main__":
    entrypoint()
