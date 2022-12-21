### needs a cohort map

data = {}
for yr in cohort_map.keys():
    print(f'doing {yr}')
    data[yr] = []
    for d in tqdm(cohort_map[yr]):
        d['balance delta'] = d['TransactionBalanceAmt'].diff()
        inc_balance_count = d['balance delta'][d['balance delta']>0].count()
        data[yr].append(inc_balance_count)

test_1 = pd.DataFrame.from_dict( data , orient='index').transpose()
for c in test_1.columns:
    yr_str = c
    sample = pd.DataFrame(test_1[[c]].dropna().value_counts().reset_index())
    sample = sample.rename(columns={c: 'IncBalanceOccurence',
                                        0: 'NumberOccurences'})
    sample.to_csv(f'increasing_balance_csvs/{yr_str}.csv')
    
data_2 = {}
for yr in cohort_map.keys():
    print(f'doing {yr}')
    data_2[yr] = []
    for d in (cohort_map[yr]):
        d = d.rename(columns={'Transactioncd':'TransactionCd'})
        test_2 = d.iloc[2:]
        # looking for positive or negative transactions based on boolean mask
        y = (test_2[test_2['balance delta']<0]['TransactionCd'].values)
        if len(y)>0:
            data_2[yr]+=( [i for i in y] )

def get_matching_transaction_codes(idx_list:list)->pd.DataFrame:
    df_transactioncd = pd.read_csv('elips_code_csvs/ELIPSLOOKUP_TRANCDTBL.csv')
    df_transactioncd = df_transactioncd[['TRANSACTIONCD','DESCRIPTION']]
    df_transactioncd.rename(columns={"TRANSACTIONCD":"TransactionCd"}, inplace=True)
    mask = idx_list
    return df_transactioncd[df_transactioncd['TransactionCd'].isin(mask)].set_index('TransactionCd')

test_2 = pd.DataFrame.from_dict(data_2, orient='index').transpose()

test_2 = test_2.transpose().reset_index().apply(lambda s: s.value_counts(), axis=1).fillna(0)
idx = list(range(2000,2011))
test_2 = test_2[[c for c in test_2.columns if int(c) not in idx]]
test_2.columns = test_2.columns.astype(int)
test_2.index = idx
test_2 = test_2.transpose()
test_2.head()
test_2.merge( get_matching_transaction_codes(list(test_2.index)), how='left', left_index=True, right_index=True ).to_csv('increasing_balance_csvs/decreasing_tcodes.csv')
df_inc_tcodes = pd.read_csv('increasing_balance_csvs/increasing_tcodes.csv')
df_inc_tcodes.rename(columns={'Unnamed: 0': 't_code'}, inplace=True)
df_dec_tcodes = pd.read_csv('increasing_balance_csvs/decreasing_tcodes.csv')
df_dec_tcodes.rename(columns={'Unnamed: 0': 't_code'}, inplace=True)
inc_codes = set(df_inc_tcodes.t_code.values)
dec_codes = set(df_dec_tcodes.t_code.values)

# print(inc_codes&dec_codes)
print(f"exclusive increasing codes: {[c for c in inc_codes if c not in dec_codes]}")
print(f"exclusive decreasing codes: {[c for c in dec_codes if c not in inc_codes]}")