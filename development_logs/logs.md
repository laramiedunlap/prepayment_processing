## Development Notes
---
## 12/14/2022
### 7:10 am
One of the issues in the original database pull is the duplicates. There may be a way to do that in C when the strings are being first parsed that would reduce the run time. Right now the duplicates are dropped post-parsing when the dataframes are being built. The pandas drop_duplicates()
function is a safe library call that ensures we don't drop unique records. 

NOTE: The current throughput:

### Step 1
LOANS DICT (GP pointer to Loan Object)
### Step 2
BUILD COHORT LIST (list of LOAN OBJECTS for each vintage)
### Step 3
PARSE PAYMENT STRINGS:
* At parse payment strings, we filter by code. So if we find new codes or transaction codes that can be used, they can be included or discluded here. The function is called "do_prepayments"
* The output is a 3 dimensional array in the following structure of this example:

    - COHORT year=2000 [
        - GP # [
            - [datetime.date(2020, 7, 31), 298, '1010', -1085.66, 0.0],
            - [datetime.date(2020, 7, 31), 298, '1010', -1085.66, 0.0], 
            - [datetime.date(2020, 8, 31), 310, '1510', 100000, 10000],
            - [ ... ]
        - ]
    - ]

* This will have duplicates that will be dropped in the next step

### Step 4
Once we have all of those strings parsed for a cohort, we then Build dataframes and clean the data further. Then we add amortization schedules to each loan and merge that onto the actual principal payments of each loan. 

### Current step:
The issue is how to deal with increasing balances. There are large numbers of loans that have increasing balances. Overnight I reran step 1 and added a "Lender Status Code" attribute for the Loan class, and also pulled the Transaction code for each. 

Today, first thing I will get the number of increasing balances in each cohort (2000 onward). We have to figure out the logic behind the balance records so that we can accurately amortize the loans and estimate the difference in scheduled principal

---

### 12:40 pm

So we've got the counts of prepayments in each vintage and the transaction codes associated with increasing and decreasing principle. My hope was that there would be codes exclusive to increasing / decreasing balances, however that isn't the case. 
So now I need to think programmatically.

We need to smoothe these principal payment histories. For the ones we keep (key distinction), I need to apply row removal until the loan's principal meets a linear or quasi linear condition. 

This would look something like:
``` 
while not linear:
    try:
        df = apply_smoothe(df)
        if is_linear(df[TransactionBalanceAmount]) == True:
            linear==True
    except IndexError:

```
This wouldn't be difficult, but would be HUGELY prone to over-cleansing; i.e. we could be removing transactions we shouldn't be. So I need to know what transaction codes specifcally constitute principal build up, and which ones are extraneous. 

### 4:00 pm

We now have something that smoothes out some (not all) but some of the obvious problems. Now the trick is going to be estimating or backfilling the payments it would have taken to get there. Or should I do that? Historically, SOMETHING happened to cause the abrupt increases or decreases in the loan's principal... Either way, the steps for tomorrow are pretty clear:

1) Take the codes highlighted in blue in the excel file for transaction codes. When those occur, we would not make anymore money and we can call the loan paid off (assuming that's when the code is occuring) --> probably want to look at some examples. Basically do the same as before but incorporate the transaction codes that correlate to the end of our interest in the loan.

2) So I need to write some function that measures the linearity or sensibility of a payoff string. In a way, that's what the smoothing does, however we don't want to write to harsh of a smoothing function and start thrashing the data. It could be something like a generator that runs the smoothing while some condition, then when that condition flips, another function comes in and starts 

### 5:30 pm

Tomorrow I need to start by reviewing the prep notebook and seeing where I'm at -- making sure I can get back there. We need to then incorporate the smoothing function and see what the totals would now look like for the 2000 cohort. I can do two different versions: one that tracks paid off when it's actually paid off, and another that tracks continuous prepayment relative to the amortization schedule. We have to get a graph tomorrow so we can see how close or far we are from a solution. This code base needs to be refactored and libraried as well; but I keep finding new avenues to explore. What I know is this; there are too many codes and too many corner cases to resolve fully why a loan's balance spikes. The key is understanding when it matters. 

1) payoff column
2) label codes where our interest ends (195, 218, 305,410)
3) smooth the balances (and the resulting columns)
4) groupby obs, yr, month and go to csv


## 12/15/2022
### 9:01 am
Today I need to solidify the notebooks so that when I arrive there's a clear set of cells that run to get the data structures in order. We don't want to code by brownian motion. We should probably incorporate it into one unified python file and run that file, then work on the code for the day's objectives while that's starting up. So I'm going to get these running, then while that's going on I'll make the startup python file, then get to the objectives set yesterday.

### 11:00 pm
I have the data incoming still; really crazy how long it takes to load. Today I need to psot these tables to sql for each cohort and see if that's faster -- either way they need to be there. Today I want to get two breakdowns: One that has a more traditional format taking the data for what it is, only using the payoff(maybe trimming out some of the increasing balances). Then another that is smoothed and calculates prepayments relative to the predicted amortization schedule.

### 2:00 pm
I've tried using binary search, and recursive binary search to find these peaks and troughs in the data to no avail. I have got the first paid to zero balance marked, and I can simply hard code in the transaction codes to give a clear cut "end of our revenue" timestamp

### 4:07 pm
So I have the code that can clean the data, and it can be iterated x times. We could decide to drop loans where there are too many edits to make the information useful. We have payoff column. We have the error codes and we drop positive balances there. I think I need to wrap this up, get a deliverable and go from there. Because that will take some time. By 6:00 I should have that done. 

## 12/16/2022
### 10:15 am
Well the good news, it runs. Bad news (which was expected) the prepayment amount comes in higher than the balance. Not really a surprise-- we're not taking nearly as many of the positive balance increases. From here I'm going to look at just the difference in principals. I think there could be a large deviation now among the original transaction balance amount column and the balance. 

## 12/19/2022
### 6:27 am
The real issue at this point is that the prepayment amount (in excess of the scheduled payment) comes in higher than the total pool balance. One reason this could be happening is because the scheduled payments are too low. Another reason could be that the interpolated prepay balance estimates are too high. I hate to go down rabbit trails, but my thinking is this. If we're filling in values for the balances, we have to fill in values for the payments. If a loan's prepaid balance is higher than the total principal -- i need to know which loans that is happening on. How many and what is going on there. From there i need to fine tune the interpolation process. I think there are too many Nan's -- it's a bit too ad-hoc right now. 
### 10:15 am
Alright so the code combination for an increase to the approval balance is:
``` 
{Tcd: 151, GLcd: 6002} 
```
I do not think this needs anymore investigation. We know that balances increase, the primary question is what we do with them. There's two types of balances increases. 

1) When the SBA is recording asset charge offs or loans being sold into the secondary market. These are irregular spikes that can be handled by removing the last occuring balance increase and take the earliest payoff date with the corresponding transaction code. 
2) When approval balance increases and/or loans are funded in stages. To resolve this, I simply need to know when to start tracking the principal payments. 
    * For loans with multiple consecutive balance increases, it's obvious there are no principal payments during that time frame. 
    * However, there are loans that have mulitple months of principal payments interrupted by a balance increase. We would need to encode that specific condition, then reamortize the loan when that condition is met. Further, the original dataframe would need to be split into two or more seperate data sets, amortized, trimmed, then stacked. While it's possible, I don't know if it's necessary. If the majority of loans being observed in practice are standard, I think the database would be more useful if the payment histories carry a closer reflection to reality. 

So for the rest of today I'm going to write the code that will reduce payment strings to their most logical sequence. 

### Step 1. 
---
We'll have to justify multiple descending peaks when they occur. We need to hard code the end codes to immediately start a different module, because the termination date is known. When not present, we need to trim everything before the peak. Let's start with that and then go from there. 

Side note: for now, if post-peak trimming a loan's first principal payment is NOT in the given cohort year, I'll dumb the observation number or index into a list. 

---

## 12/20/2022
### 6:34 am
Got a bit sidetracked yesterday with analytics for Waterstation. Reviewing my notes for step one, let's start by removing everything after a zero balance and a transaction code ``` (195, 218, 305, 410, 416) ```, then lets remove everything before the highest maximum. 
### 6:49 am
Running that logic over sample loans it works okay, but the issue will be sniffing out the revolvers. If I start out by chopping off the heads and tails, then loans can slip through that are actually revolvers with only one pay down. My concern is that I will be left with a very small dataset, because the only evidence I have that these are actually revolvers is... Oh wait I have an idea. If I look for post-peak, consecutive balance increases. Keep in mind that the peak -- even if a relative maximum is found, will be the index with the highest transaction balance amount. 

* I need to get five samples of loans that are mislabelled and my algorithm will label a revolver, then see if Ergkys supports that logic. 
* Another question would be can a revolver have a code 195? I'm assuming revolvers are sold and defaulted on just like a loan. So I don't think the code history would give anymore detail. 
    - 2009208
    - 2015959
    - 1493364
    - 1501177
    - 1504372
* Well that's six, and I found them way too fast. Now I want to go find loans that would count as a revolver after trimming the head and tail. So right now I'm pulling the data directly from the dictionary. To loop through these, I want to create a copy, re-window on the copy, then simply count if the number of local maxima are two or more. 

### 2:58 pm
One function down, now there's two more I can write. 
- One that checks the yrs till maturity and refuses the loan if it has a high peak count and 10 or less years till maturtity. 
- One that looks for an equality of positive tramt and trbalance amt.


## 12/21/2022
### 7:39 am
Examples to show Tom:
 - 1490638
 * Accounting Errors?
 - *2007445*
 - *1511615* 
 - *2007445*

 ```
pseudo: 
df.at[min_row, 'TransactionBalanceAmt'] = -1*(df.at[min_row, 'TransactionAmt'])
df.at[max_row, 'TransactionAmt'] = -1*(df.at[min_row, 'TransactionBalanceAmt'] - df.at[max_row, 'TransactionBalanceAmt'])
 ```