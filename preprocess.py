import pandas as pd
import numpy as np

def to_datetime(in_df: pd.DataFrame, c_list: list)->pd.DataFrame:
    for c in c_list:
        in_df[c] = pd.to_datetime(in_df[c])
    return in_df

def to_numeric(in_df: pd.DataFrame, c_list: list)->pd.DataFrame:
    for c in c_list:
        in_df[c] = pd.to_numeric(in_df[c])
    return in_df

def to_str(in_df: pd.DataFrame, c_list: list)->pd.DataFrame:
    for c in c_list:
        in_df[c] = in_df[c].astype(str)
    return in_df

def stratify_df_types(test:pd.DataFrame)->pd.DataFrame:
    """Set dtypes and column names like they will be in the database"""
    test.rename(columns={'Origination_dt':'LoanFundedDt'}, inplace=True)
    test.rename(columns={'Transactioncd':'TransactionCd'}, inplace=True)
    dates_list = ['LoanFundedDt', 'MaturityDt', 'EffectiveDt']
    nums_list = ['TransactionAmt', 'TransactionBalanceAmt']
    str_list = ['TransactionCd', 'GeneralLedgerCd', 'ObservationNmb']
    test = to_datetime(test, dates_list)
    test = to_numeric(test, nums_list)
    test = to_str(test, str_list)
    return test
    
def set_top_bot(test: pd.DataFrame)-> pd.DataFrame:
    """Re-window a dataframe to the last occurring max TransactionBalanceAmt 
    and the first occurring min TransactionBalanceAmt"""
    ix_top = test[test.TransactionBalanceAmt.values == test.TransactionBalanceAmt.values.max()].index
    ix_bot = test[test.TransactionBalanceAmt.values == test.TransactionBalanceAmt.values.min()].index
    return test.iloc[ix_top[-1]:ix_bot[0]+1]

def find_spikes(test: pd.DataFrame):
    try:
        sample = set_top_bot(test)
        arr = sample['TransactionBalanceAmt'].values
        mins = (np.diff(np.sign(np.diff(arr))) > 0).nonzero()[0] + 1
        maxs = (np.diff(np.sign(np.diff(arr))) < 0).nonzero()[0] + 1
        return sample, mins, maxs
    except AttributeError:
        return None

# def peak_handler(test: pd.DataFrame, min_list: list, max_list: list)-> str:
#     e_codes = set(['195', '218', '305', '410', '416']) 
#     peak_codes = set(list(test.loc[test.index.isin(max_list)]['TransactionCd'].values))
#     if 

def get_yrs_till_mat(l_dict:dict, obs:str)->float:
    try:
        x = pd.Timestamp(l_dict[obs].maturity_dt)
        y =  pd.Timestamp(l_dict[obs].origination_dt)
    except:
        return 'Unknown'
    return round((x-y)/np.timedelta64(1, 'Y'),0)

def remove_end_codes(test: pd.DataFrame, e_codes: set) -> pd.DataFrame:
    pass
    
def label_revolver(test: pd.DataFrame)-> bool:
    my_arr = test['TransactionBalanceAmt'].values
    maxs = (np.diff(np.sign(np.diff(my_arr))) < 0).nonzero()[0] + 1
    