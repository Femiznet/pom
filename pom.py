import click
from generator import (
    generate_config, 
    generate_from_config, 
)
import json, os

@click.group()
def pom():
    """Pom — Page Object Model generator for Playwright."""
    pass


@pom.command()
@click.argument('url')
@click.option('-o', '--output', default="pom.config.json", help='Config file path')
def get(url:str, output:str):
    """Fetch a page - (html) and auto-detect interactive elements into a config file.
    
    The generated config can be reviewed and edited before running `pom generate`.
    """
    click.echo(f"Fetching {url}...")
    
    try:

        # build config structure from html
        model = generate_config(url)

        # confirm before overwriting existing config
        if os.path.exists(output):
            overwrite = click.confirm(f'{output} already exists. Overwrite?', default=False)
            if not overwrite:
                click.echo('Aborted.')
                return

        with open(output, 'w') as f:
            json.dump(model, f, indent=2)

        click.echo(f"Config saved to {output}")
        click.echo(f"Review it then run: python pom.py generate -o <generated file>")

    except Exception as e:
        first_line = str(e).split('\n')[0]
        click.echo(f"Error: {first_line}", err=True)


@pom.command()
@click.option('-o', '--output', default=None, help='Output file name')
@click.option('--config', default='pom.config.json', help='Config file path')
def generate(config:str, output:str):
    """Generate a page object model from a config file.
    
    Reads baseUrl and pages from the config and produces a BasePom subclass
    with typed Locator attributes and auto navigation.
    """

    if not config.endswith('.json'):
        click.echo(f"Warning: '{config}' doesn't look like a JSON file. Continuing anyway...")

    try:
        with open(config, 'r') as f:
            data = json.load(f)

        model = generate_from_config(data)
        
        if output:
            with open(output, 'w') as f:
                f.write(model)
            click.echo(f"Model saved to {output}")
        else:
            # print to stdout if no output file specified
            print(model)

    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON in config file: {e.msg} at line {e.lineno}", err=True)
    except FileNotFoundError:
        click.echo(f"Config file not found: {config}", err=True)
    except KeyError as e:
        click.echo(f"Missing required field in config: {e}", err=True)
    except Exception as e:
        first_line = str(e).split('\n')[0]
        click.echo(f"Error: {first_line}", err=True)
        
if __name__ == '__main__':
    pom()