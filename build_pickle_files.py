def get_ids()-> list:
    with engine.connect() as con:
            con.execute('SET GLOBAL innodb_buffer_pool_size=2147483648;')
            # Get ObservationNmb's for all non-revolver loans
            query = """ SELECT elipsmisc7afoia.ObservationNmb, repymnttbl7afoia.MaturityDt, elipsmisc7afoia.LoanFundedDt, loantbl7afoia.LenderStatusCd FROM elipsmisc7afoia
                    JOIN repymnttbl7afoia
                    ON repymnttbl7afoia.ObservationNmb = elipsmisc7afoia.ObservationNmb
                    JOIN loantbl7afoia
                    ON loantbl7afoia.ObservationNmb = elipsmisc7afoia.ObservationNmb
                    WHERE RevolvingLineofCreditCd = 'Y' AND YEAR(LoanFundedDt) >= 2000 ;"""
                    
            print("aggregating loan ids...\n")
            rows = con.execute(query)
            return [list(ele) for ele in rows.fetchall()]


ids = get_ids()

loans = {}

print("looping...\n")
with engine.connect() as con:    
    for id in tqdm(ids):
        con.execute('SET GLOBAL innodb_buffer_pool_size=2147483648;')
        query = f"""SELECT EffectiveDt, TransacionCd, GeneralLedgerCd, TransactionAmt, TransactionBalanceAmt FROM master_fin WHERE ObservationNmb = \"{id[0]}\" """
        result = con.execute(query)
        rows = np.array([list(ele) for ele in result])
        loans[id[0]] = Loan(id[0], id[1], id[2], id[3], rows)
        
        # DataStructure of Loan.pmt_history: 
        #   [
        #   [EffectiveDt, GeneralLedgerCd, TransactionAmt, TransactionBalanceAmt ],
        #   [EffectiveDt, GeneralLedgerCd, TransactionAmt, TransactionBalanceAmt],
        #   [EffectiveDt, GeneralLedgerCd, TransactionAmt, TransactionBalanceAmt], ...
        #   ]
        

with open('loans_new.pickle', 'wb') as f:
    pickle.dump(loans, f)
    
def build_cohort(loan_dict, year):
    cohort = []
    for key in loan_dict:
        if loan_dict[key].origination_dt.year == year:
            cohort.append(loan_dict[key])

    return cohort

def do_principal_pmts(cohrt_ls: list):
    """WHENEVER YOU TEST A CHANGE --- CHANGE cohrt_ls to cohrt_ls[0:2] and see how it looks"""
    master_principal = []
    print('parsing all payment strings...')
    for x in (cohrt_ls):
        hist = x.all_pmts
        hist = np.insert(hist, 0, x.maturity_dt, axis=1)
        hist = np.insert(hist, 0, x.origination_dt, axis=1)      
        hist = np.insert(hist, 0, x.ObservationNmb, axis=1)
        hist_1510 = hist[ hist[:, 5]== '1510', :]
        hist_6031 = hist[ hist[:, 5]== '6031', :]
        principal_pmts = np.append(hist_1510, hist_6031, axis=0)
        order = principal_pmts[:, 3].argsort()
        principal_pmts = principal_pmts[order]
        master_principal.append(principal_pmts)
    print('returning master principal pmt structure')
    return master_principal


def build_df_list(prepayment_arr, cols):
    df_list = []
    for d in prepayment_arr:
        df_list.append(pd.DataFrame(data=d, columns= cols).drop_duplicates())
    return df_list


to_do_list = list(range(2000, 2011, 1))
cohort_map = {}
for yr in tqdm(to_do_list):
    print(f"collecting principal payments for vintage: {yr}")
    l = build_cohort(loans, yr)
    cohort_map[str(yr)] = do_principal_pmts(l)
    
columns = ['ObservationNmb', 'Origination_dt', 'MaturityDt', 'EffectiveDt', 'Transactioncd' ,'GeneralLedgerCd', 'TransactionAmt', 'TransactionBalanceAmt']
for key in tqdm(cohort_map.keys()):
    print(f"converting vintage {key} to dataframes...")
    cohort_map[key] = build_df_list(cohort_map[key], columns)
    

