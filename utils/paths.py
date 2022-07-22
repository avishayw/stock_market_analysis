from os.path import dirname, abspath, exists, join
from os import mkdir
from pathlib import Path, PurePath


def project_path():
    project_path = Path(dirname(dirname(abspath(__file__))))
    while list(PurePath(project_path).parts)[-1] != 'stock_market_analysis':
        project_path = project_path.parent.absolute()
    return project_path


def save_under_project_path(path):
    return Path(project_path(), path)


def save_under_results_path(path):
    return Path(Path(project_path(), 'results'), path)


def make_dir_under_path(path, dir):
    path = join(path,dir)
    if not exists(path):
        mkdir(path)


if __name__=="__main__":

    print(save_under_results_path("APPL.csv"))
