import pandas as pd
from pathlib import Path
import os
import numpy as np
from tqdm import tqdm
import datetime
import pickle


class Loan:
    ObservationNmb: int
    maturity_dt: datetime.date
    origination_dt: datetime.date
    all_pmts: np.ndarray
    
    def __init__(self, nmb, m_dt, o_dt, pmts):
        self.ObservationNmb = nmb
        self.maturity_dt = m_dt
        self.origination_dt = o_dt
        self.all_pmts = pmts
    # This could be updated later to find the payoff dates using
    # numpy. However, pandas uses np under the hood and I'm not sure it 
    # would be any more performant.
    # But this class method was there when the file was pickled and removing it could 
    # cause issues even if it doesn't do anything. 
    def find_payoff_date(self):
        pass

# This function returns the loans that match the given origination year    
def build_cohort(loan_dict, year):
    cohort = []
    for key in loan_dict:
        if loan_dict[key].origination_dt.year == year:
            cohort.append(loan_dict[key])

    return cohort

# This function organizes all the payment strings 
# bit of a misnomer --> the return is a master_list of payments
# that affect the outstanding balance
def do_prepayments(cohrt_ls: list):
    master_principal = []
    for x in tqdm(cohrt_ls):
        hist = x.all_pmts
        hist = np.insert(hist, 0, x.maturity_dt, axis=1)
        hist = np.insert(hist, 0, x.origination_dt, axis=1)      
        hist = np.insert(hist, 0, x.ObservationNmb, axis=1)
        hist_1510 = hist[ hist[:, 3]== '1510', :]
        hist_6031 = hist[ hist[:, 3]== '6031', :]
        principal_pmts = np.append(hist_1510, hist_6031, axis=0)
        order = principal_pmts[:, 2].argsort()
        principal_pmts = principal_pmts[order]
        master_principal.append(principal_pmts)
    return master_principal

#This Functions builds a list of dataframes; each one is an individual loan's 
# principal payment history
def build_df_list(prepayment_arr, cols):
    df_list = []
    for d in prepayment_arr:
        df_list.append(pd.DataFrame(data=d, columns= cols))
    return df_list


def main():
    # Read in loan structures --> This will take 15-20 minutes
    with open('payments.pickle', 'rb') as f:
        loans = pickle.load(f)
    # Get Cohort
    ls = build_cohort(loans, 2000)
    # Create master pmt array
    master_pmts = do_prepayments(ls)
    # get list of loan dataframes
    columns = ['ObservationNmb', 'Origination_dt', 'MaturityDt', 'EffectiveDt', 'GeneralLedgerCd', 'TransactionAmt', 'TransactionBalanceAmt']
    df_list = build_df_list(master_pmts, columns)
    # Combine list into one large table
    df = pd.concat(df_list)
    # Do a bunch of dataframe formatting
    df['EffectiveDt'] = pd.to_datetime(df['EffectiveDt'])
    df['Origination_dt'] = pd.to_datetime(df['Origination_dt'])
    df['MaturityDt'] = pd.to_datetime(df['MaturityDt'])
    # Get rid of effective dates in the 1960's that exist for some reason 
    df = df[df['EffectiveDt'].dt.year != 1960]
    # Drop Duplicates
    df = df.drop_duplicates()
    # Create a binary column to indicate if a loan has been paid off
    df['PaidOff'] = 0
    df.loc[ (df['TransactionAmt']<0) & (df['TransactionBalanceAmt']<1000), 'PaidOff' ] = 1
    # Create a column to calculate the number of months between origination and payoff
    df['MnthsFrom_Origination'] = 0
    df.loc[df['PaidOff']==1, 'MnthsFrom_Origination'] = ((df.Origination_dt - df.EffectiveDt)/np.timedelta64(1, 'M'))
    df['MnthsFrom_Origination'] = df['MnthsFrom_Origination'].astype(int)
    # Do another to calculate how early the loan was paid off relative to its maturity
    df['MnthsFrom_Maturity'] = 0
    df.loc[df['PaidOff']==1, 'MnthsFrom_Maturity'] = ((df.MaturityDt - df.EffectiveDt)/np.timedelta64(1, 'M'))
    df['MnthsFrom_Maturity'] = df['MnthsFrom_Maturity'].astype(int)
    # Look at all rows with a payoff, then enforce uniqueness on each ObservationNmb (take the earliest payoff date)
    
