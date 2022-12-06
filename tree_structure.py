import numpy as np
from pandas import *
import matplotlib.pyplot as plt
 
# reading CSV file
data = read_csv("GraphAnalysis/graphAnalysis.csv")
 
# converting column data to list
nodes = data[" % of reduced nodes"].tolist()
cf = data["% of reduced cf"].tolist()

num_simulations = 11

expr_mean_nodes = np.zeros(99)
expr_mean_cf = np.zeros(99)
expr_var_nodes = nodes
expr_var_cf = cf
expr_var_nodes = np.reshape(expr_var_nodes, (num_simulations, 99))
expr_var_nodes = np.transpose(expr_var_nodes)
expr_var_cf = np.reshape(expr_var_cf, (num_simulations, 99))
expr_var_cf = np.transpose(expr_var_cf)
for i in range(0,99):
    for j in range(0,num_simulations):
        expr_mean_nodes[i] = expr_mean_nodes[i] + nodes[i+99*j]
        expr_mean_cf[i] = expr_mean_cf[i] + cf[i+99*j]
    expr_mean_nodes[i] = expr_mean_nodes[i]/num_simulations
    expr_mean_cf[i] = expr_mean_cf[i]/num_simulations

expr_var_nodes = np.var(expr_var_nodes, axis=1) 
expr_var_cf = np.var(expr_var_cf, axis=1)
mean_nodes = np.mean(expr_mean_nodes)
var_nodes = np.var(expr_mean_nodes)
mean_cf = np.mean(expr_mean_cf)
var_cf = np.var(expr_mean_cf)

print("Among all the configurations, the total number of nodes is reduced with a mean of", mean_nodes)
print("variance", var_nodes)
print("Among all the configurations, the ratio cf is reduced with a mean of", mean_cf)
print("variance", var_cf)

bt_number =  np.linspace(0,100,100, dtype=int)
bt_number =  np.delete(bt_number, 37)

e_nodes=np.sqrt(expr_var_nodes) 

plt.errorbar(bt_number, expr_mean_nodes, e_nodes, linestyle='None', marker='.', elinewidth= 1, color= 'red', ecolor= 'blue')

plt.title('Average Percentage Reduction of Total Nodes')
plt.xlabel('Configuration')
plt.ylabel('Average % reduction')
plt.show()

e_cf=np.sqrt(expr_var_cf) 


plt.errorbar(bt_number, expr_mean_cf, e_cf, linestyle='None', marker='.', elinewidth= 1, color= 'red', ecolor= 'blue')

plt.title('Average Percentage Reduction $cf$')
plt.xlabel('Configuration')
plt.ylabel('Average % reduction')
plt.show()
