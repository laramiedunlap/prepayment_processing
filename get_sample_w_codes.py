import pandas as pd
from pathlib import Path
import sqlalchemy as sa
from dotenv import load_dotenv
import os
import psutil
import regex as re
import numpy as np
from tqdm import tqdm
import datetime
load_dotenv()

# set options for pandas and numpy formatting (no errors should occur if these are ommitted)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.options.mode.chained_assignment = None  # default='warn'
np.set_printoptions(formatter={'float':"{:6.5g}".format})

def main():
    id = str(input('Input Observation Number...'))
    print('Doing transactions with codes...')
    engine = sa.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                .format(host=os.getenv('host'), db=os.getenv('db'), user=os.getenv('uname'), pw=os.getenv('password')))

    query = f"SELECT distinct EffectiveDt, TransacionCd, GeneralLedgerCd, TransactionAmt, TransactionBalanceAmt  FROM master_fin where ObservationNmb = \"{id}\";"
    df_1 = pd.read_sql(query, engine)
    df_generalledgercd = pd.read_csv('elips_code_csvs/ELIPSLOOKUP_GENLDGCDTBL.csv')

    df_generalledgercd =df_generalledgercd[['GENERALLEDGERCD','DESCRIPTION']]

    df_transactioncd = pd.read_csv('elips_code_csvs/ELIPSLOOKUP_TRANCDTBL.csv')

    df_transactioncd = df_transactioncd[['TRANSACTIONCD','DESCRIPTION']]

    df_generalledgercd.rename(columns={"GENERALLEDGERCD":"GeneralLedgerCd"}, inplace=True)
    df_transactioncd.rename(columns={"TRANSACTIONCD":"TransacionCd"}, inplace=True)

    targ = df_1.merge(df_transactioncd, on='TransacionCd')
    targ = targ.merge(df_generalledgercd, on='GeneralLedgerCd')

    targ = targ.rename(columns={'DESCRIPTION_x': 'Tcd_description',
                        'DESCRIPTION_y': 'GLcd_decription'})

    targ.to_csv('spot checks/transactions_w_codes.csv')


    print('Doing tables...')
    query = f"SELECT * FROM elipsamt7afoia WHERE ObservationNmb = \"{id}\""
    df_1 = pd.read_sql(query, engine)
    df_1.to_csv('spot checks/elipsamt_tbl.csv')

    query = f"SELECT * FROM elipscoll7afoia WHERE ObservationNmb = \"{id}\""
    df_1 = pd.read_sql(query, engine)
    df_1.to_csv('spot checks/elipscoll_tbl.csv')

    query = f"SELECT * FROM elipsmisc7afoia WHERE ObservationNmb = \"{id}\""
    df_1 = pd.read_sql(query, engine)
    df_1.to_csv('spot checks/elipsmisc_tbl.csv')

    query = f"SELECT * FROM repymnttbl7afoia WHERE ObservationNmb = \"{id}\""
    df_1 = pd.read_sql(query, engine)
    df_1.to_csv('spot checks/repymnt_tbl.csv')
    
    print('done')
    
if __name__ == "__main__":
    main()

