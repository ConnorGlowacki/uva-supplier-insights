import click
from supplypy.service.preprocessing import process_all_csvs, prepare_clustered_data
from supplypy.deploy.deploy_tabpy_services import deploy_services

@click.group()
def main():
    click.echo("Dispatching command...")

@main.command()
def build():
    process_all_csvs()
    prepare_clustered_data()

@main.command()
@click.option("--host", default="http://localhost:9004/", nargs=1, help="The URL for the TabPy server to deploy tools to")
@click.option("--username", nargs=1, help="The username for TabPy server authentication")
@click.option("--password", nargs=1, help="The password for TabPy server authentication")
def deploy(host: str, username: str, password: str):
    click.echo("Deploying TabPy Services...")
    # deploy_services(host, username, password)