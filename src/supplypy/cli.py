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
def deploy():
    click.echo("Deploying TabPy Services...")
    deploy_services()