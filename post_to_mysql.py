import sqlalchemy as sa
import pandas as pd
import os
from dotenv import load_dotenv

engine = sa.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
			.format(host=os.getenv('host'), db=os.getenv('db'), user=os.getenv('uname'), pw=os.getenv('password')))

data_types ={'ObservationNmb': sa.types.VARCHAR(15),
 'LoanFundedDt': sa.types.DATE,
 'MaturityDt': sa.types.DATE,
 'EffectiveDt': sa.types.DATE,
 'TransactionCd': sa.types.SmallInteger,
 'GeneralLedgerCd': sa.types.CHAR(4),
 'TransactionAmt': sa.types.Float,
 'TransactionBalanceAmt': sa.types.Float}

# For each cohort, post the concatenated dataframe with all the transactions for each loan so that we have principal payments
# and whatever other data we need there... Could also do the amortization schedules as well. I would say to load those seperately -- maybe? 

def main():
    for yr in passed_argument:
        master = pd.concat(yr)
        master.to_sql(name=f"{yr}_principalpmts", con=engine, dtype= data_types)