#!/usr/bin/python
# -*- coding: utf-8 -*-


# importing the required libraries
import pandas as pd
import numpy as np

# reading the mempool.csv file
data = pd.read_csv('mempool.csv')

data.head()

# replacing the NaN values in Parents column with Null so that we can do easy computations.
data['parents '].fillna(value="Null" , inplace=True)

# it shows the information of the data so as to know about the number of null values and type of data.
data.info()

# records is total no of rows or records in the dataset(mempool.csv) starting the count from 0.
records = data.index.stop


# here we are finding the ratio of the fee and weight for each row
# and appending the ratio column to the data
ratio = []
for i in range(records):
    ratio.append(data['fee'][i] / data['weight'][i]) 

# we have concatenated the ratio column to the data 
ratio = pd.DataFrame(ratio , columns=['ratio'])
data = pd.concat([data , ratio] , axis=1)

# the basic idea of creating the ratio column is that if we want to maximise the fee 
# and we have constraint on weight (i.e less than 4000000)
# so the miner will get maximum fee when, for every unit weight we include transaction id with maximum fee 
# so eventually having higher ratio of fee/weight.

# here, sorting the data in descending order wrt the ratio field
data = data.sort_values('ratio', axis=0 , ascending=False, ignore_index=True)

tx_id = data['tx_id']
fee = data['fee']
weight = data['weight']
parents = data['parents ']
ratio = data['ratio']


# average_ratio_of_data is basically sum of all the ratio divided by total records in data.
average_ratio_of_data = sum(ratio) / records

# threshold_ratio_of_data is basically a value ratio from data for which we will have weight<=4000000
# so this step is just an estimation for what values of ratios should be included for maximum fee.
w=0
for f in range(records):
    w = w + weight[f]
    if w >= 4000000:
        break
threshold_ratio_of_data = ratio[f]

# threshold_ratio is the average of average_ratio_of_data and threshold_ratio_of_data
       
threshold_ratio = (average_ratio_of_data + threshold_ratio_of_data) / 2

# from the above calculation threshold_ratio for this data comes out to be 0.6693820630414727
threshold_ratio

# block_txn_list_index is the final list containing the indexs of the transaction id that should be included
block_txn_list_index = []
# sum_weight is a variable to check that weight<= 4000000
sum_weight = 0


def adding_Transaction_To_The_Block():
    global block_txn_list_index
    global sum_weight
    # visited = []

    for position in range(records):
        sub_parents_list_index = []
        temp_sub_parents_list_index = []
        
        if position not in block_txn_list_index:
            if parents[position] == "Null" and (sum_weight + weight[position]) <= 4000000:
                block_txn_list_index.append(position)
                sum_weight = sum_weight + weight[position]
                # print(position)

            else:
                # print(position)
                parents_list_index = getting_Parents_Index(position , sub_parents_list_index , temp_sub_parents_list_index)     
        else:
            pass
                
            
def getting_Parents_Index(position , sub_parents_list_index , temp_sub_parents_list_index):
    sub_parents_list = []
    
    sub_parents = str(parents[position])
    sub_parents_list = sub_parents.split(sep=';', maxsplit=-1)
    
    
    for sp in sub_parents_list:
        if sp is not "Null":
            sp_index = data[tx_id == sp].index
            sub_parents_list_index.insert(0 , sp_index[0])
            temp_sub_parents_list_index.append(sp_index[0])


    while temp_sub_parents_list_index:
        if parents[temp_sub_parents_list_index[0]] == "Null":
            temp_sub_parents_list_index.pop(0)
            
        else:
            getting_Parents_Index(temp_sub_parents_list_index.pop(0) , sub_parents_list_index , temp_sub_parents_list_index)
            
    adding_Parents_Transaction_To_Block(sub_parents_list_index,position)
    
def adding_Parents_Transaction_To_Block(sub_parents_list_index , position):
    sum_ratio = 0
    average_ratio = 0
    parents_weight = 0
    global sum_weight
    
    for r in sub_parents_list_index:
        sum_ratio = sum_ratio + ratio[r]
    sum_ratio = sum_ratio + ratio[position]
    
    average_ratio = sum_ratio / (len(sub_parents_list_index) + 1)
    
    for pw in sub_parents_list_index:
        if pw not in block_txn_list_index:
            parents_weight = parents_weight + weight[pw]
    parents_weight = parents_weight + weight[position]
    
    if (average_ratio >= threshold_ratio) and (parents_weight + sum_weight <= 4000000):
        block_txn_list_index.append(position)
        
        for i in sub_parents_list_index:
            if i in block_txn_list_index:
                del block_txn_list_index[block_txn_list_index.index(i)]
                
            
        for j in reversed(sub_parents_list_index):
            block_txn_list_index.insert(0 , j)
            
        sum_weight = sum_weight + parents_weight


adding_Transaction_To_The_Block()

w = 0
for i in block_txn_list_index:
    w = w + weight[i]
print("weight:  " + str(w))
    

f = 0
for i in block_txn_list_index:
    f = f + fee[i]
print("fee:  " + str(f))


file = open("block.txt", "a")
for item in block_txn_list_index:
    file.writelines(str(tx_id[item])+"\n" )
    
file.close()

