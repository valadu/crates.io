import pathlib as p
import time

from lib import CratesIO


def main(directory: str, delay: float) -> None:
    root = p.Path(directory)
    root.mkdir(parents=True, exist_ok=True)

    # CratesIO
    site = CratesIO()
    tic = time.time()
    with open(root/'crates.txt', 'w') as f:
        for crate in site.crates(delay=1.0, per_page=100):
            time.sleep(delay)
            crate.fullize()
            f.write(crate.to_json() + '\n')
    toc = time.time()
    (root/'categories.txt').write_text(site.categories_to_str())
    (root/'keywords.txt').write_text(site.keywords_to_str())
    (root/'time.json').write_text(f'{{"start": {tic}, "end": {toc}}}')
    # TODO: Git
    pass


if __name__ == '__main__':
    main(
        directory='data',
        delay=0.7,
    )
