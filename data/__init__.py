__all__ = ['categories', 'crates', 'keywords', 'time']


import json as _j
import pathlib as _p
import typing as _t



def _load_txt_1(path: _p.Path) -> _t.Dict[str, _t.Any]:
    data = {}
    with open(path, 'r') as f:
        for line in f:
            key, value = line.split('\t', maxsplit=1)
            data[key] = _j.loads(value)
    return data

def _load_txt_2(path: _p.Path) -> _t.Dict[str, _t.Any]:
    data = {}
    with open(path, 'r') as f:
        for line in f:
            value = _j.loads(line)
            data[value['name']] = value
    return data


_root = _p.Path(__file__).absolute().parent
categories = _load_txt_1(_root/'categories.txt')
crates = _load_txt_2(_root/'crates.txt')
keywords = _load_txt_1(_root/'keywords.txt')
time = _j.loads((_root/'time.json').read_text())
