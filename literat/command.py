import os

import click

from literat import __version__
from literat.config import Config
from literat.builder import (
    build_toc,
    build_index,
    build_readme,
    build_article,
    clean_directory,
    get_base_dir,
    gen_file_paths,
)


pass_config = click.make_pass_decorator(  # pylint: disable=invalid-name
    Config, ensure=True)


def print_version(ctx, _param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group()
@click.option('--config', 'config_file', type=click.Path(exists=True))
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@pass_config
def cli(config, config_file):
    """Loads config file.

    This function is entry point.
    """
    if config_file:
        config.file = config_file
    config.load()


@cli.command()
@click.option('--output', type=click.Path(exists=False))
@pass_config
def new(config, output):
    """Creates new publication."""
    sdir = output or config['build']['output']
    try:
        os.makedirs(sdir)
    except FileExistsError:
        pass

    idx_file = 'README.adoc'  # default
    idx_path = os.path.join(sdir, idx_file)
    if os.path.isfile(idx_path):
        print('README exists: \'{:s}\''.format(idx_path))
    else:
        with open(os.path.join(sdir, idx_file), 'w') as f:
            f.write('== README ==')


@cli.command()
@click.option('--input', 'input_dir', type=click.Path(exists=False))
@click.option('--output', 'output_dir', type=click.Path(exists=False))
@pass_config
def build(config, input_dir, output_dir):
    """Generates html files into output directory."""
    build_config, composition_config = config['build'], config['composition']
    sdir = input_dir or build_config['input']
    ddir = output_dir or build_config['output']
    clean_directory(ddir)

    # special partial
    with build_toc(composition_config['toc']) as toc:
        # index
        idx_path = composition_config['idx']
        base_dir = get_base_dir(idx_path, sdir, ddir)
        build_index(idx_path, base_dir, toc)
        # readme
        readme_path = composition_config['readme']
        base_dir = get_base_dir(readme_path, sdir, ddir)
        build_readme(readme_path, base_dir, toc)

        # articles
        for src_path in gen_file_paths(sdir):
            base_dir = get_base_dir(src_path, sdir, ddir)
            build_article(src_path, base_dir, toc)
