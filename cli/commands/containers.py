import os
import click

from cli.utils import constants
from cli.utils import database
from cli.utils import shared

TERMINATION_STRING = 'if [ -z `docker-compose ps -q %s` ] || ' \
                     '   [ -z `docker ps -q --no-trunc | grep $(docker-compose ps -q %s)` ]; then\n' \
                     '  exit 1\n' \
                     'else\n' \
                     '  docker-compose stop %s\n' \
                     '  exit 0\n' \
                     'fi'


def read_services_file(services_file):
    services_file_location = os.path.join(constants.SERVICES_DIR, services_file)

    return [line.rstrip('\n') for line in open(services_file_location)]


def terminate_container(container, debug=False):
    code, _, _ = shared.execute_command(
        "Terminating container %s" % container,
        TERMINATION_STRING % (container, container, container),
        debug=debug,
        cwd=constants.PROJECT_DIR,
        allowed_exit_codes=[0, 1]
    )

    if code is 1:
        click.echo("     Container %s is not running." % container)
    elif code is 0:
        click.echo("     Container %s terminated." % container)
    else:
        click.echo(
            click.style("     WARNING", fg='yellow') +
            ": Unknown exit code use --debug option to get more information."
        )


def terminate_containers(containers, debug=False):
    for container in containers:
        terminate_container(container, debug)


def terminate_all_containers(debug):
    shared.execute_command(
        "Shutting down all corresponding CRMint containers",
        "docker-compose down",
        cwd=constants.PROJECT_DIR,
        debug=debug
    )

    click.echo("     Containers terminated.")


def launch_containers(args, debug, detach, containers):
    click.echo(click.style(">>>> Launch environment", fg='magenta', bold=True))
    # click.echo(click.style("---> Shutting down previously launched containers ", fg='blue', bold=True))

    terminate_containers(containers, debug)
    # terminate_all_containers(debug)

    additional_args = []
    if detach:
        additional_args.append("--d")

    command = "docker-compose up %s %s %s" % (
        args,
        ' '.join(additional_args),
        ' '.join(containers)
    )

    shared.execute_command(
        "Launching containers: %s" % ', '.join(containers),
        command,
        debug=debug,
        force_std_out=not detach,
        disable_spinner=not detach,
        cwd=constants.PROJECT_DIR
    )

    click.echo("     Containers launched.")

    print args


@click.group()
def cli():
    """Container groups manipulations"""
    pass


####################### NO FRONTEND ########################

@cli.group()
def no_frontend():
    """All containers except Frontend"""
    pass


@click.option('--args')
@click.option('--debug/--no-debug', default=False)
@click.option(
    '--detach/--no-detach',
    default=True,
    help='Detached mode: Run containers in the background.'
)
@no_frontend.command('up')
def no_frontend_up(args, debug, detach):
    """Launch all containers except Frontend"""

    if not args:
        args = ""

    services = read_services_file('no_frontend.txt')
    launch_containers(args, debug, detach, services)

    click.echo(click.style("Done.", fg='magenta', bold=True))


@click.option('--debug/--no-debug', default=False)
@no_frontend.command('down')
def no_frontend_down(debug):
    """Stop all containers except Frontend"""

    services = read_services_file('no_frontend.txt')
    terminate_containers(services, debug)

    click.echo(click.style("Done.", fg='magenta', bold=True))


####################### NO BACKEND ########################

@cli.group()
def no_backend():
    """All containers except Backend"""
    pass


@click.option('--args')
@click.option('--debug/--no-debug', default=False)
@click.option(
    '--detach/--no-detach',
    default=True,
    help='Detached mode: Run containers in the background.'
)
@no_backend.command('up')
def no_backend_up(args, debug, detach):
    """Launch all containers except Backend"""

    if not args:
        args = ""

    services = read_services_file('no_backend.txt')
    launch_containers(args, debug, detach, services)

    click.echo(click.style("Done.", fg='magenta', bold=True))


@click.option('--debug/--no-debug', default=False)
@no_backend.command('down')
def no_backend_down(debug):
    """Stop all containers except Backend"""

    services = read_services_file('no_backend.txt')
    terminate_containers(services, debug)

    click.echo(click.style("Done.", fg='magenta', bold=True))


####################### BASE ONLY ########################

@cli.group()
def base_only():
    """Util containers manipulations (database, seeds etc.)"""
    pass


@click.option('--args')
@click.option('--debug/--no-debug', default=False)
@click.option(
    '--detach/--no-detach',
    default=True,
    help='Detached mode: Run containers in the background.'
)
@base_only.command('up')
def base_only_up(args, debug, detach):
    """Launch all containers except Backend and Frontend"""

    if not args:
        args = ""

    services = read_services_file('base_only.txt')
    launch_containers(args, debug, detach, services)

    click.echo(click.style("Done.", fg='magenta', bold=True))


@click.option('--debug/--no-debug', default=False)
@base_only.command('down')
def base_only_down(debug):
    """Stop all containers except Backend and Frontend"""

    services = read_services_file('base_only.txt')
    terminate_containers(services, debug)

    click.echo(click.style("Done.", fg='magenta', bold=True))


####################### ALL ########################

@cli.group()
def all():
    """Manipulate with all containers"""
    pass


@click.option('--args')
@click.option('--debug/--no-debug', default=False)
@click.option(
    '--detach/--no-detach',
    default=True,
    help='Detached mode: Run containers in the background.'
)
@all.command('up')
def all_up(args, debug, detach):
    """Launch all containers"""

    if not args:
        args = ""

    services = read_services_file('all.txt')
    launch_containers(args, debug, detach, services)

    click.echo(click.style("Done.", fg='magenta', bold=True))


@click.option('--debug/--no-debug', default=False)
@all.command('down')
def all_down(debug):
    """Stop all containers"""

    terminate_all_containers(debug)

    click.echo(click.style("Done.", fg='magenta', bold=True))
