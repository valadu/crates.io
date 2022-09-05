import functools as f
import time
import typing as t

from lib.crates_io import Crate
from data import categories, crates, keywords


class Category:
    def __init__(self, name: str, data: t.Dict[str, t.Any]) -> None:
        self._data = data
        self._data['id'] = name

    @property
    def data(self) -> t.Dict[str, t.Any]:
        return self._data

    def __repr__(self) -> str:
        date = lambda t: time.strftime('%Y/%m/%d', time.localtime(t))
        return f'<{self._data["name"]} ({self._data["count"]:,d} crates) @ {date(self._data["timestamp"])}>'


class Keyword:
    def __init__(self, name: str, data: t.Dict[str, t.Any]) -> None:
        self._data = data
        self._data['id'] = name

    @property
    def data(self) -> t.Dict[str, t.Any]:
        return self._data

    def __repr__(self) -> str:
        date = lambda t: time.strftime('%Y/%m/%d', time.localtime(t))
        return f'<{self._data["name"]} ({self._data["count"]:,d} crates) @ {date(self._data["timestamp"])}>'


class Analysis:
    def __init__(self, number: int = 10) -> None:
        self._number = number

    @f.lru_cache()
    def new_crates(self) -> t.List[Crate]:
        key = lambda name: crates[name]['timestamp']['create']
        return [self._crate(crates[name]) for name in self._max(crates, self._number, key)]

    @f.lru_cache()
    def most_downloaded(self) -> t.List[Crate]:
        key = lambda name: crates[name]['download']['all']
        return [self._crate(crates[name]) for name in self._max(crates, self._number, key)]

    @f.lru_cache()
    def just_updated(self) -> t.List[Crate]:
        key = lambda name: crates[name]['timestamp']['update']
        return [self._crate(crates[name]) for name in self._max(crates, self._number, key)]

    @f.lru_cache()
    def most_recent_downloads(self) -> t.List[Crate]:
        key = lambda name: crates[name]['download']['recent']
        return [self._crate(crates[name]) for name in self._max(crates, self._number, key)]

    @f.lru_cache()
    def popular_keywords(self) -> t.List[Keyword]:
        key = lambda name: keywords[name]['count']
        return [Keyword(name, keywords[name]) for name in self._max(keywords, self._number, key)]

    @f.lru_cache()
    def popular_categories(self) -> t.List[Category]:
        key = lambda name: categories[name]['count']
        return [Category(name, categories[name]) for name in self._max(categories, self._number, key)]

    def _crate(self, data: t.Dict[str, t.Any]) -> Crate:
        crate = Crate({})
        crate._data = data
        return crate

    def _max(self, data: t.Iterable, number: int = 1, key: t.Optional[t.Callable] = None) -> t.List[t.Any]:
        # TODO: optimize
        return sorted(data, key=key, reverse=True)[:number]


if __name__ == '__main__':
    import pandas as pd

    domain = 'https://crates.io'
    analysis = Analysis(number=10)

    data = {
        'New Crates': [
            f'[`{crate.verbose(1)}`]({domain}/crates/{crate.data["name"]})'
            for crate in analysis.new_crates()
        ],
        'Most Downloaded': [
            f'[`{crate.verbose(1)}`]({domain}/crates/{crate.data["name"]})'
            for crate in analysis.most_downloaded()
        ],
        'Just Updated': [
            f'[`{crate.verbose(1)}`]({domain}/crates/{crate.data["name"]})'
            for crate in analysis.just_updated()
        ],
        'Most Recent Downloads': [
            f'[`{crate.verbose(1)}`]({domain}/crates/{crate.data["name"]})'
            for crate in analysis.most_recent_downloads()
        ],
        'Popular Keywords': [
            f'[`{repr(keyword)}`]({domain}/keywords/{keyword.data["id"]})'
            for keyword in analysis.popular_keywords()
        ],
        'Popular Categories': [
            f'[`{repr(category)}`]({domain}/categories/{category.data["id"]})'
            for category in analysis.popular_categories()
        ],
    }
    pd.DataFrame(data).to_markdown('README.md', index=False)
