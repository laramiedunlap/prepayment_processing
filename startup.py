import pickle

def get_loans():
    with open('pickle_files/loans_new.pickle', 'rb') as infile:
        return pickle.load(infile)

def get_cohort_map():
    with open('pickle_files/cohort_map.pickle', 'rb') as infile:
        return pickle.load(infile)

def get_cohort_map_with_df():
    with open('pickle_files/cohort_map_df.pickle', 'rb') as infile:
        return pickle.load(infile)

def main():
    startup = input('type (1) for loans dict\n(2) for cohort map\n(3) for cohort map with dataframes')
    if '1' in str(startup):
        print('Loading serialized data. This can take up to 45 minutes...')
        return get_loans()
    elif '2' in str(startup):
        print('Loading serialized data. This can take up to 90 minutes...')
        return get_cohort_map()
    elif '3' in str(startup):
        print('Loading serialized data. This can take up to 45 minutes...')
        return get_cohort_map_with_df()