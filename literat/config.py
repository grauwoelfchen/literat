import yaml


def load_data(data: dict, into: dict):
    for key in data:
        if key in into.keys():
            value = data[key]
            if isinstance(value, dict):
                load_data(value, into[key])
            else:
                into[key] = value


class Config:
    def __init__(self):
        self._file = 'config.yml'
        self._data = {
            'title': '',
            'description': '',
            'abstract': '',
            'language': 'en',
            'authors': [{
                'name': '',
                'link': '',
            }],
            'copyright': '',
            'license': '',
            'composition': {
                'readme': 'README.adoc',
                'changelog': 'CHANGELOG.adoc',
                'toc': 'toc.adoc',
                'idx': 'index.adoc',
                'arc': 'archive.adoc',
            },
            'build': {
                'syntax': 'AsciiDoc',
                'auto_toc': False,
                'auto_idx': True,
                'idx_limit': 0,
                'auto_arc': False,
                'arc_unit': 'year',
                'input': 'articles',
                'output': 'public',
                'format': 'html',
            }
        }

    def load(self) -> None:
        """Loads data from config.yaml into itself."""
        with open(self._file, 'r') as f:
            try:
                data = yaml.load(f)
            except yaml.YAMLError:
                data = ()
            load_data(data, self._data)

    def get(self, key, default):
        return self._data.get(key, default)

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return str(self._data)
