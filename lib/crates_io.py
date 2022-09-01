__all__ = ['CratesIO']


import datetime
import math
import time
import typing as t

import httpx
import tqdm


def get(route: str, params: t.Optional[t.Dict] = None) -> httpx.Response:
    return httpx.get(f'https://crates.io{route}', params=params)


class CratesIO:
    '''
    Reference:
        - https://crates.io
    '''

    def __init__(self) -> None:
        pass

    def __len__(self) -> int:
        return self.number()

    def number(self) -> int:
        first_page = self._crates(1, 50, 'alpha')
        return first_page['meta']['total']

    def crates(self, delay: float = 1.0, number: int = 50, sort: str = 'alpha') -> t.Iterator[t.Dict]:
        pages = range(math.ceil(self.number()/number))
        for page in tqdm.tqdm(pages):
            yield from self.crates_by_page(page+1, number, sort)
            time.sleep(delay)

    def crates_by_page(self, page: int, number: int = 50, sort: str = 'alpha') -> t.Iterator[t.Dict]:
        try:
            data = self._crates(page, number, sort)
        except Exception as e:
            print(page, e)
        else:
            yield from map(Crate, data['crates'])

    def _crates(self, page: int, number: int, sort: str) -> t.Dict:
        params = {'page': page, 'per_page': number, 'sort': sort}
        return get('/api/v1/crates', params=params).json()


class Crate:

    def __init__(self, data: t.Dict) -> None:
        self._data = {
            'badges': data.get('badges', None),
            'date': {
                'create': self._timestamp(data.get('created_at', '')),
                'update': self._timestamp(data.get('updated_at', '')),
            },
            'description': data.get('description', None),
            'documentation': data.get('documentation', None),
            'download': {
                'all': data.get('downloads', None),
                'recent': data.get('recent_downloads', None),
            },
            'homepage': data.get('homepage', None),
            'name': data.get('name', None),
            'repository': data.get('repository', None),
            'version': {
                'max_stable': data.get('max_stable_version', None),
                'max': data.get('max_version', None),
                'newest': data.get('newest_version', None),
            },
        }

    def __repr__(self) -> str:
        return self._data.__repr__()

    @property
    def data(self) -> t.Dict:
        return self._data

    def fullize(self) -> 'Crate':
        extra = get(f'/api/v1/crates/{self._data["name"]}', params=None).json()
        self._data.update({
            'categories': extra.get('categories', None),
            'keywords': extra.get('keywords', None),
        })
        return self

    def _timestamp(self, string: str) -> t.Optional[float]:
        try:
            return datetime.datetime.fromisoformat(string).timestamp()
        except ValueError:
            return None
