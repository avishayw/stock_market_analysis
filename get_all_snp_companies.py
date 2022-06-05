import pandas as pd


def get_all_snp_companies():
    payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    return payload[0]


if __name__=="__main__":
    print(get_all_snp_companies()['Symbol'].tolist())
