import os


def get_ticker_from_csv(full_path):
    return str(os.path.basename(full_path)).split('_')[0]