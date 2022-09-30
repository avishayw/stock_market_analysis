import yfinance as yf
from measurements.noise_measurements import efficiency_ratio
from indicators.momentum_indicators import simple_moving_average
from trade_managers._ma_roc_er_trading import ma_roc_er_signals
from trade_managers._signal_trading_manager import signal_trading_manager_long


def ma_roc_er_optimization(ticker, combination):

    sma1_period = combination[0]
    sma2_period = combination[1]
    sma1_uptrend_roc_period = combination[2]
    sma2_uptrend_roc_period = combination[3]
    sma1_uptrend_roc_th = combination[4]
    sma2_uptrend_roc_th = combination[5]
    sma1_uptrend_er_th = combination[6]
    sma2_uptrend_er_th = combination[7]
    sma1_downtrend_roc_period = combination[8]
    sma1_downtrend_roc_th = combination[9]
    sma1_downtrend_er_th = combination[10]

    df = yf.Ticker(ticker).history(period='max', interval='1d').reset_index()
    df = ma_roc_er_signals(df,
                           sma1_period=sma1_period,
                           sma2_period=sma2_period,
                           sma1_uptrend_roc_period=sma1_uptrend_roc_period,
                           sma2_uptrend_roc_period=sma2_uptrend_roc_period,
                           sma1_uptrend_roc_th=sma1_uptrend_roc_th,
                           sma2_uptrend_roc_th=sma2_uptrend_roc_th,
                           sma1_uptrend_er_th=sma1_uptrend_er_th,
                           sma2_uptrend_er_th=sma2_uptrend_er_th,
                           sma1_downtrend_roc_period=sma1_downtrend_roc_period,
                           sma1_downtrend_roc_th=sma1_downtrend_roc_th,
                           sma1_downtrend_er_th=sma1_downtrend_er_th
                           )

    trades, final_cap = signal_trading_manager_long(ticker, df, print_trades=False)
    return trades


if __name__ == '__main__':
    import concurrent.futures
    from itertools import product, repeat
    import pandas as pd
    import numpy as np
    from strategy_statistics.strategy_statistics import all_statistics_dict
    import json

    tickers = [
        "BKRRF",
        "PRPH",
        "RAIN",
        "RCL",
        "GGAL",
        "CFIVU",
        "ABNB",
        "CFB",
        "BFI",
        "BKNG",
        "COWN",
        "DMKBA",
        "GNRC",
        "VTRU",
        "BEN",
        "FFMGF",
        "AQST",
        "TELL",
        "THTX",
        "ABMC",
        "HTH",
        "AMKR",
        "PH",
        "BDJ",
        "SPLK",
        "BILL",
        "NDAQ",
        "JFIN",
        "LNC",
        "QSAM",
        "ZURVY",
        "BKR",
        "APACU",
        "HP",
        "AIRC",
        "ZCMD",
        "LEAT",
        "MSA",
        "SHO",
        "IPG",
        "RVLV",
        "SBLRF",
        "SJR",
        "CPG",
        "CPWR",
        "ENDMF",
        "REG",
        "EXROF",
        "AMAOU",
        "HEXO",
        "VVNT",
        "CMG",
        "EXPD",
        "MODN",
        "EXCOF",
        "ITT",
        "OVTZ",
        "BNPQF",
        "HEI",
        "MCD",
        "VFF",
        "BRT",
        "VPCBU",
        "DTMXF",
        "ALLE",
        "GBNY",
        "KLIC",
        "WWE",
        "OGGFF",
        "HES",
        "MITI",
        "ORIA",
        "UE",
        "PARA",
        "AUD",
        "BITF",
        "ATI",
        "LKQ",
        "BKT",
        "LEE",
        "NGG",
        "OMEX",
        "NVACF",
        "WMB",
        "SBAC",
        "DOOO",
        "GTPAU",
        "OOMA",
        "FLXS",
        "TIG",
        "BGPPF",
        "CTR",
        "DAKT",
        "EBS",
        "REI",
        "ACBM",
        "LFTR",
        "HNST",
        "TFC",
        "JUN",
        "AVXL",
        "NUO",
        "ASPS",
        "JHI",
        "LEJU",
        "LECRF",
        "TMBR",
        "HRT",
        "HCTI",
        "SFST",
        "DMAQ",
        "FEO",
        "WWACU",
        "ESEA",
        "WGO",
        "ICPT",
        "PTC",
        "OBSV",
        "BIMI",
        "GPN",
        "AEM",
        "KE",
        "CXDO",
        "NXPI",
        "GBLEF",
        "ICHR",
        "CRIS",
        "SNMP",
        "NVVE",
        "CBBI",
        "HERAU",
        "ADN",
        "EYES",
        "KRKNF",
        "SNP",
        "EPAM",
        "NVGLF",
        "CS",
        "ELECF",
        "IDXG",
        "NBRFF",
        "INAB",
        "SLAB",
        "SGSVF",
        "TPR",
        "UNIB",
        "DTOC",
        "LAZR",
        "AGTI",
        "CUBA",
        "BEWFF",
        "STAG",
        "XPAXU",
        "PTMN",
        "TMASF",
        "ERIC",
        "NSR",
        "IVZ",
        "CL",
        "TKC",
        "UCLE",
        "DTOCU",
        "NEM",
        "AHPI",
        "MTLS",
        "GD",
        "TPRFF",
        "ECGFF",
        "RIVN",
        "QCOM",
        "KR",
        "PFIN",
        "ESP",
        "ABBV",
        "STLD",
        "TRVG",
        "SITC",
        "TIVC",
        "RELT",
        "EQMEF",
        "ETR",
        "RH",
        "BNTX",
        "ICD",
        "CTO",
        "ZS",
        "AJG",
        "CGNT",
        "SCMA",
        "OSPN",
        "JAGGF",
        "GWW",
        "EJTTF",
        "FHI",
        "ATIXF",
        "IPVI",
        "TATT",
        "FFOXF",
        "MAS",
        "CRDL",
        "NUV",
        "FPOCF",
        "PCB",
        "ROYL",
        "GBOOY",
        "RXT",
        "ADBRF",
        "PLMR",
        "MPW",
        "CUBI",
        "NDAC",
        "PFIE",
        "VNTR",
        "KF",
        "WINT",
        "AQN",
        "DOCU",
        "GNTY",
        "FVCB",
        "MPACU",
        "SO",
        "CEVA",
        "AXS",
        "MNDO",
        "LYFT",
        "HMCO",
        "AVTX",
        "DGHI",
        "HPK",
        "CURUF",
        "ONVO",
        "PLX",
        "NRRSF",
        "ASG",
        "CCNE",
        "AUMBF",
        "COST",
        "AFL",
        "MCAGU",
        "VTRS",
        "ACDI",
        "EYE",
        "MLACU",
        "COF",
        "GFAI",
        "PSNL",
        "APTM",
        "DOOR",
        "AZN",
        "IXAQU",
        "ULTA",
        "LIAN",
        "CRF",
        "DLR",
        "TCBI",
        "CRAI",
        "SPHRY",
        "BWACU",
        "FFIV",
        "OVATF",
        "ACIW",
        "ADXS",
        "ROOT",
        "GPOTF",
        "MCFE",
        "WTRG",
        "SJM",
        "AG",
        "PYPD",
        "ANPMF",
        "LMB",
        "CMA",
        "EDTX",
        "HAS",
        "CMP",
        "SBSW",
        "WDAY",
        "CEV",
        "KTEL",
        "ANY",
        "TRUIF",
        "GWSFF",
        "PVCT",
        "PSA",
        "MED",
        "IMIMF",
        "MPXOF",
        "EQIX",
        "DBLVF",
        "EGAN",
        "HUMA",
        "VMGAU",
        "CRSXF",
        "HBNC",
        "MIND",
        "ARCE",
        "TZOO",
        "NEE",
        "CTVEF",
        "KOPN",
        "BSFO",
        "AAPL",
        "VRSCF",
        "RGP",
        "FOSL",
        "HITI",
        "APLS",
        "TMAC",
        "GSTC",
        "MUFG",
        "GLQ",
        "SMIH",
        "ATHM",
        "AACG",
        "GERN",
        "DAC",
        "EMMA",
        "BLLYF",
        "TT",
        "AVAN",
        "PXD",
        "MXL",
        "GIII",
        "ITW",
        "ILMN",
        "BY",
        "AROC",
        "FITB",
        "SGIIU",
        "BXMT",
        "HAACU",
        "MBWM",
        "ICMB",
        "HCBC",
        "WDC",
        "LFACU",
        "VXTRF",
        "HOG",
        "BAP",
        "BCDA",
        "NBTX",
        "MTD",
        "NAVB",
        "MGM",
        "BMY",
        "HQH",
        "EVR",
        "GASXF",
        "OONEF",
        "ESVNF",
        "LEAI",
        "SENEA",
        "DBL",
        "URI",
        "LHCG",
        "CMAX",
        "Z",
        "HCAR",
        "PRBM",
        "PINE",
        "PZN",
        "LCID",
        "FTCO",
        "LHC",
        "PTOTF",
        "XFOR",
        "LYB",
        "CRL",
        "EA",
        "SEER",
        "SPOFF",
        "ICE",
        "MFM",
        "BIDU",
        "SELB",
        "IGTAU",
        "RF",
        "FLOOF",
        "CLAQU",
        "TROW",
        "AOS",
        "NTLA",
        "CBSH",
        "WM",
        "CAT",
        "CPSS",
        "AMAO",
        "XPER",
        "LAUR",
        "AVNT",
        "IPWR",
        "DISH",
        "FTV",
        "TSLA",
        "CLBT",
        "KNBIF",
        "NTST",
        "ATC",
        "SIEB",
        "GOTRF",
        "DD",
        "BMIX",
        "MPB",
        "BCSF",
        "SPFI",
        "EVI",
        "BAX",
        "GOOGL",
        "WU",
        "NVEC",
        "DFS",
        "AFYA",
        "CAF",
        "GBOX",
        "VITL",
        "NAVI",
        "GATO",
        "EDSA",
        "CCRN",
        "NCPL",
        "KGFHY",
        "EVOJ",
        "IMBI",
        "CINT",
        "SOTK",
        "FLIC",
        "XRAPF",
        "STTK",
        "SXOOF",
        "CCHWF",
        "EVRG",
        "IQV",
        "EHC",
        "NBO",
        "AWP",
        "AMED",
        "SEBFF",
        "MNDT",
        "MSGE",
        "MAR",
        "EYEN",
        "BIP",
        "SSNT",
        "EFSI",
        "TSRI",
        "MYD",
        "HUM",
        "SIM",
        "WWAC",
        "SSVRF",
        "CIAFF",
        "HHGCU",
        "IPOOF",
        "PD",
        "HGBL",
        "FHLT",
        "BOTJ",
        "SPOT",
        "NARI",
        "IR",
        "MDWT",
        "DXC",
        "SNA",
        "HBT",
        "UBAB",
        "RXMD",
        "COLB",
        "GROY",
        "INTWF",
        "FRSX",
        "CNMD",
        "MYNDF",
        "SURF",
        "ISTR",
        "ORCL",
        "TYL",
        "CNI",
        "RGLD",
        "PDD",
        "LNT",
        "NDLS",
        "SMDRF",
        "SRNE",
        "MGTX",
        "RLX",
        "WRE",
        "HALL",
        "SGLY",
        "HPS",
        "RBLX",
        "BIOT",
        "HRL",
        "RIOFF",
        "ENVA",
        "SPXX",
        "PI",
        "PHYT",
        "HLGN",
        "GLRE",
        "SEMR",
        "ZWRK",
        "KBNT",
        "MDT",
        "PSYCF",
        "HST",
        "ASPCU",
        "FRONU",
        "CRXT",
        "WISH",
        "HCP",
        "TEVA",
        "AEE",
        "ISCO",
        "OPY",
        "RMBI",
        "GOBI",
        "DHI",
        "ECL",
        "HPQ",
        "DYLLF",
        "FORG",
        "PBHC",
        "ASTR",
        "TBSA",
        "FMBH",
        "TOUR",
        "ALPP",
        "TRQ",
        "CB",
        "REGI",
        "FCUV",
        "CF",
        "GRPH",
        "ZY",
        "OB",
        "AMHPF",
        "UTG",
        "SCND",
        "ESE",
        "YMM",
        "CYD",
        "MAQC",
        "VLO",
        "BTCS",
        "SICNF",
        "FRBK",
        "BK",
        "IEX",
        "TRMB"
    ]

    sma1_period_list = [5, 10, 20]
    sma2_period_list = [10, 20, 50]
    sma1_uptrend_roc_period_list = [3, 5, 10, 15]
    sma2_uptrend_roc_period_list = [3, 5, 10, 15]
    sma1_uptrend_roc_th_list = [2.0, 3.0, 5.0, 10.0]
    sma2_uptrend_roc_th_list = [2.0, 3.0, 5.0, 10.0]
    sma1_uptrend_er_th_list = [0.2, 0.5, 0.8]
    sma2_uptrend_er_th_list = [0.2, 0.5, 0.8]
    sma1_downtrend_roc_period_list = [3, 5, 10, 15]
    sma1_downtrend_roc_th_list = [-2.0, -3.0, -5.0, -10.0]
    sma1_downtrend_er_th_list = [0.2, 0.5, 0.8]

    params_list = [sma1_period_list,
                   sma2_period_list,
                   sma1_uptrend_roc_period_list,
                   sma2_uptrend_roc_period_list,
                   sma1_uptrend_roc_th_list,
                   sma2_uptrend_roc_th_list,
                   sma1_uptrend_er_th_list,
                   sma2_uptrend_er_th_list,
                   sma1_downtrend_roc_period_list,
                   sma1_downtrend_roc_th_list,
                   sma1_downtrend_er_th_list]

    combinations = product(*params_list)

    for combination in combinations:

        combination_str = '_'.join([str(x) for x in combination])
        all_trades = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = executor.map(ma_roc_er_optimization, tickers, repeat(combination))

            for result in results:
                all_trades = all_trades + result

        combination_df = pd.DataFrame(all_trades).dropna()
        print(f'sma1_period: {combination[0]}\n',
              f'sma2_period: {combination[1]}\n',
              f'sma1_uptrend_roc_period: {combination[2]}\n',
              f'sma2_uptrend_roc_period: {combination[3]}\n',
              f'sma1_uptrend_roc_th: {combination[4]}\n',
              f'sma2_uptrend_roc_th: {combination[5]}\n',
              f'sma1_uptrend_er_th: {combination[6]}\n',
              f'sma2_uptrend_er_th: {combination[7]}\n',
              f'sma1_downtrend_roc_period: {combination[8]}\n',
              f'sma1_downtrend_roc_th: {combination[9]}\n',
              f'sma1_downtrend_er_th: {combination[10]}\n')
        print(f'Win Rate: {len(combination_df.loc[combination_df["win"]])/len(combination_df)}')
        print(f'Mean Change %: {np.mean(combination_df["change%"].tolist())}')
        print(f'Total trades: {len(all_trades)}')
        if len(all_trades) > 0:
            print(f'Sample error: {(1/np.sqrt(len(all_trades)))*100}\n')

        with open(f'{combination_str}_statistics.json', 'w') as f:
            json.dump(all_statistics_dict(pd.DataFrame(all_trades)), f, indent=4)
