__all__ = ['CratesIO']


import datetime
import math
import time
import typing as t

import httpx
import retrying
import tqdm


@retrying.retry(stop_max_attempt_number=7, wait_fixed=1_000)
def get(route: str, params: t.Optional[t.Dict] = None) -> httpx.Response:
    return httpx.get(f'https://crates.io{route}', params=params)


class CratesIO:
    '''
    Reference:
        - https://crates.io
    '''

    categories: t.Dict = {}
    keywords: t.Dict = {}

    def __init__(self) -> None:
        pass

    def __len__(self) -> int:
        return self.number()

    def number(self) -> int:
        first_page = self._crates(1, 50, 'alpha')
        return first_page['meta']['total']

    def crates(self, delay: float = 1.0, per_page: int = 50, sort: str = 'alpha') -> t.Iterator['Crate']:
        pages = range(math.ceil(self.number()/per_page))
        for page in tqdm.tqdm(pages):
            yield from self.crates_by_page(page+1, per_page, sort)
            time.sleep(delay)

    def crates_by_page(self, page: int, per_page: int = 50, sort: str = 'alpha') -> t.Iterator['Crate']:
        try:
            data = self._crates(page, per_page, sort)
        except Exception as e:
            print(page, e)
        else:
            yield from map(Crate, data['crates'])

    def _crates(self, page: int, per_page: int, sort: str) -> t.Dict:
        params = {'page': page, 'per_page': per_page, 'sort': sort}
        return get('/api/v1/crates', params=params).json()


class Crate:

    def __init__(self, data: t.Dict) -> None:
        self._data = {
            'badges': data.get('badges', None),
            'timestamp': {
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
        # categories
        categories = extra.get('categories', None)
        if categories is not None:
            for category in categories:
                key = category.get('id', None)
                if key not in CratesIO.categories:
                    CratesIO.categories[key] = {
                        'name': category.get('category', None),
                        'count': category.get('crates_cnt', None),
                        'timestamp': self._timestamp(category.get('created_at', '')),
                    }
            categories_ = [c.get('id', None) for c in categories]
        else:
            categories_ = None
        # keywords
        keywords = extra.get('keywords', None)
        if keywords is not None:
            for keyword in keywords:
                key = keyword.get('id', None)
                if key not in CratesIO.keywords:
                    CratesIO.keywords[key] = {
                        'name': keyword.get('keyword', None),
                        'count': keyword.get('crates_cnt', None),
                        'timestamp': self._timestamp(keyword.get('created_at', '')),
                    }
            keywords_ = [k.get('id', None) for k in keywords]
        else:
            keywords_ = None
        self._data.update({'categories': categories_, 'keywords': keywords_})
        return self

    def _timestamp(self, string: str) -> t.Optional[float]:
        try:
            return datetime.datetime.fromisoformat(string).timestamp()
        except ValueError:
            return None
