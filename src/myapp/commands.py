import click

from myapp.services.categories import seed_categories


@click.command("seed-categories")
def seed_categories_command():
    """Carga las categorías iniciales (no crea duplicados)."""
    created = seed_categories()
    if created:
        click.echo(f"Categorías creadas: {', '.join(created)}")
    else:
        click.echo("Las categorías ya estaban cargadas.")


def register_commands(app):
    app.cli.add_command(seed_categories_command)
