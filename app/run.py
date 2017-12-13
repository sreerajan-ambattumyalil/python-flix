import click

@click.command()
@click.option("--module", default="", help ="The component to be executed. (etl / app)" )
def cli(module):
    if "etl" == module:
        click.echo("Running %s" % module)
    if "app" == module:
        click.echo("Running %s" % module)
    else:
        click.echo("Execute run --help for details ")