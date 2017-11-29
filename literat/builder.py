from contextlib import contextmanager
import glob
import os
import re
import shutil
from subprocess import PIPE, Popen
import tempfile

from chameleon import PageTemplateLoader


def asciidoc_to_html(text):
    """Converts text into html using `asciidoc`.

    This function run `asciidoc` command within a process.
    """
    p = Popen(
        ['asciidoc', '--no-header-footer',
         '--backend=html5', '-'],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate(text.encode())
    if p.returncode != 0:
        raise RuntimeError('asciidoc: "%s"' % err)

    return out.decode('utf-8')


@contextmanager
def build_toc(toc_path):
    proot = os.path.join(os.path.dirname(__file__))

    with tempfile.NamedTemporaryFile() as f:
        with tempfile.NamedTemporaryFile() as tf:
            templates_dir = os.path.join(proot, 'templates')

            with open(toc_path, 'r') as tp:
                body = asciidoc_to_html(tp.read())
                tf.write((  # sidebar.pt
                    '<metal:macro use-macro="load:{0:s}">'
                    '<metal:slot fill-slot="toc">'
                    '{1:s}'
                    '</metal:slot>'
                    '</metal:macro>'
                ).format(
                    os.path.join(templates_dir, 'toc.pt'),
                    body
                ).encode())

                tf.seek(0)
                templates = PageTemplateLoader([
                    templates_dir,
                    os.path.dirname(tf.name),
                ])
                tmpl = templates[tf.name]

                f.write(tmpl().encode())

        f.seek(0)
        yield f


def build_index(src_path, base_dir, toc=None):
    try:
        os.makedirs(base_dir)
    except FileExistsError:
        pass

    proot = os.path.join(os.path.dirname(__file__))
    dst_path = os.path.join(base_dir, 'index.html')

    with tempfile.NamedTemporaryFile() as tf:
        templates_dir = os.path.join(proot, 'templates')

        with open(src_path, 'r') as sf:
            args = [os.path.join(templates_dir, 'master.pt')]
            if toc:
                toc.seek(0)
                args.append(toc.read().decode())

            args.append(asciidoc_to_html(sf.read()))
            tf.write((  # index.pt
                '<metal:macro use-macro="load:{0:s}">'
                '<metal:slot fill-slot="sidebar">'
                '{1:s}'
                '</metal:slot>'
                '<metal:slot fill-slot="content">'
                '<div class="content">{2:s}</div>'
                '</metal:slot>'
                '</metal:macro>'
            ).format(*args).encode())

        tf.seek(0)
        templates = PageTemplateLoader([
            templates_dir,
            os.path.dirname(tf.name),
        ])
        tmpl = templates[tf.name]

        with open(dst_path, 'w+') as df:
            df.write((tmpl(title='title', description='description')))


def build_readme(src_path, base_dir, toc=None):
    try:
        os.makedirs(base_dir)
    except FileExistsError:
        pass

    proot = os.path.join(os.path.dirname(__file__))
    dst_path = os.path.join(
        base_dir, os.path.splitext(os.path.basename(src_path))[0] + '.html')

    with tempfile.NamedTemporaryFile() as tf:
        templates_dir = os.path.join(proot, 'templates')

        with open(src_path, 'r') as sf:
            args = [os.path.join(templates_dir, 'master.pt')]
            if toc:
                toc.seek(0)
                args.append(toc.read().decode())

            args.append(asciidoc_to_html(sf.read()))
            tf.write((  # index.pt
                '<metal:macro use-macro="load:{0:s}">'
                '<metal:slot fill-slot="sidebar">'
                '{1:s}'
                '</metal:slot>'
                '<metal:slot fill-slot="content">'
                '<div class="content">{2:s}</div>'
                '</metal:slot>'
                '</metal:macro>'
            ).format(*args).encode())

        tf.seek(0)
        templates = PageTemplateLoader([
            templates_dir,
            os.path.dirname(tf.name),
        ])
        tmpl = templates[tf.name]

        with open(dst_path, 'w+') as df:
            df.write((tmpl(title='title', description='description')))


def build_article(src_path, base_dir, toc=None):
    """Generates output html through master template via temporary file.

    This function creates named temporary file which is deleted after run.
    """
    try:
        os.makedirs(base_dir)
    except FileExistsError:
        pass

    proot = os.path.join(os.path.dirname(__file__))
    dst_path = os.path.join(
        base_dir, os.path.splitext(os.path.basename(src_path))[0] + '.html')

    with tempfile.NamedTemporaryFile() as tf:
        templates_dir = os.path.join(proot, 'templates')

        with open(src_path, 'r') as sf:
            args = [os.path.join(templates_dir, 'master.pt')]
            if toc:
                toc.seek(0)
                args.append(toc.read().decode())

            args.append(asciidoc_to_html(sf.read()))
            tf.write((  # article.pt
                '<metal:macro use-macro="load:{0:s}">'
                '<metal:slot fill-slot="sidebar">'
                '{1:s}'
                '</metal:slot>'
                '<metal:slot fill-slot="content">'
                '<article>{2:s}</article>'
                '</metal:slot>'
                '</metal:macro>'
            ).format(*args).encode())

        tf.seek(0)
        templates = PageTemplateLoader([
            templates_dir,
            os.path.dirname(tf.name),
        ])
        tmpl = templates[tf.name]

        with open(dst_path, 'w+') as df:
            df.write((tmpl(title='title', description='description')))


def clean_directory(directory):
    try:
        shutil.rmtree(directory)
    except OSError:
        pass
    finally:
        try:
            os.makedirs(directory)
        except FileExistsError:
            pass


def gen_file_paths(sdir):
    """Generates target file paths in src."""
    for i in glob.iglob('{:s}/**/'.format(sdir), recursive=False):
        if os.path.isfile(i):
            yield i
        elif os.path.isdir(i):
            # only nest level 2
            for f in glob.iglob('{:s}/*'.format(i)):
                if os.path.isfile(f):
                    yield f


def get_base_dir(target_path, sdir, ddir):
    slash = re.compile(r'^/')
    if sdir in target_path:
        sbase = re.sub(
            slash, '', os.path.dirname(target_path).replace(sdir, '', 1))
    else:
        sbase = os.path.dirname(os.path.basename(target_path))
    return os.path.join(ddir, sbase)
