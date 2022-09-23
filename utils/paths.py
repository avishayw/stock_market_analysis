from os.path import dirname, abspath, exists, join
from os import mkdir
from pathlib import Path, PurePath
import glob


def project_path():
    project_path = Path(dirname(dirname(abspath(__file__))))
    while list(PurePath(project_path).parts)[-1] != 'stock_market_analysis':
        project_path = project_path.parent.absolute()
    return project_path


def save_under_project_path(path):
    return Path(project_path(), path)


def save_under_results_path(path):
    return Path(Path(project_path(), 'results'), path)


def save_under_models_path(path):
    return Path(Path(project_path(), 'models'), path)


def random_stock_data_path():
    return fr'C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\random_stock_data'


def save_under_random_stock_data_path(path):
    return Path(random_stock_data_path(), path)


def make_dir_under_path(path, dir):
    path = join(path,dir)
    if not exists(path):
        mkdir(path)
    return path


def get_in_sample_data_csvs():
    return glob.glob(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\in-sample-daily-data" + '/*.csv')


if __name__=="__main__":
    import json

    # print(save_under_results_path("APPL.csv"))
    csvs = glob.glob(r"C:\Users\Avishay Wasse\PycharmProjects\stock_market_analysis\in-sample-daily-data" + '/*.csv')
