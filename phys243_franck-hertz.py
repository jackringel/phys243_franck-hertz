import re
import matplotlib.pyplot as plt
import numpy as np
import math
import os

def parse_file(file):
    """takes in franck-hertz csv file, returns np arrays of input voltages and output voltages"""
    text = file.read()
    ls = np.array(re.split(',|\n', text))
    ls = ls[7:]
    n = 0
    xvals = np.array([])
    yvals = np.array([])
    for i in ls:
        if n == 0:
            n+=1
        elif n == 1:
            xvals = np.append(xvals,float(i))
            n+=1
        elif n == 2:
            try:
                yvals = np.append(yvals,float(i))
            except:
                xvals = xvals[:-1]
            n=0
    return xvals, yvals

def parse_exp_folder(folder):
    """takes in text path (use forward slash) to picoscope experiment folder w 64 waveforms, returns np arrays of input and output voltages"""
    x = np.array([])
    y = np.array([])
    for i in range(64):
        file_ext = "_0"+str(i+1)+".csv" if i < 9 else "_"+str(i+1)+".csv"
        temp = folder.split('/')
        temp.append(temp[-1]+file_ext)
        filename = ''
        for i in temp:
            filename += i+'/'
        filename=filename[:-1]
        file=open(filename,'r')
        xvals, yvals = parse_file(file)
        file.close()
        x=np.concatenate((x,xvals))
        y=np.concatenate((y,yvals))
    return x, y

def error_propogation(x,y):
    """takes in numpy arrays with some overlapping xvalues
    calculates error bars for given xval
    returns 3 arrays - xvals, yvals, std_devs"""
    x, y = sort_organize(x,y)
    yvals = np.array([])
    std_devs = np.array([])
    for i in y:
        mean, std_dev = analyze_data(i)
        yvals = np.append(yvals, mean)
        std_devs = np.append(std_devs, std_dev)
    sorted_indices = np.argsort(x)
    x = x[sorted_indices]
    yvals = yvals[sorted_indices]
    return x, yvals, std_devs

def analyze_data(values):
    """take in numpy array of values, return mean and std dev"""
    total = 0
    for i in values:
        total += i
    mean = total / np.size(values)
    sum_ = 0
    for i in values:
        sum_ += math.pow(i-mean,2)
    std_dev = math.sqrt(sum_/np.size(values))
    return mean, std_dev

def sort_organize(x,y):
    """take in equally sized numpy arrays with some like x values
    return array of arrays - all possible x values, array of
    associated y values for each"""
    xvals = np.array([])
    yvals = []
    for i in range(np.size(x)):
        if x[i] not in xvals:
            xvals = np.append(xvals, x[i])
            yvals.append(np.array([y[i]]))
        else:
            index = xvals.tolist().index(x[i])
            yvals[index] = np.append(yvals[index], y[i])
    return xvals, np.array(yvals)

def parse_folder(folder):
    """takes in string containing folder with sub-experiment folders,
    iterates through them, returns list of lists - each sub-list has format
    [name, xvals, yvals, std_devs]"""
    directory = os.fsencode(folder)
    data = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        x, y = parse_exp_folder(folder+'/'+filename)
        xvals, yvals, std_devs = error_propogation(x, y)
        data.append([filename, xvals, yvals, std_devs])
    return data

def main():
    folder = input("Directory name (use forward slashes, and don't end the string on a slash): ")
    data = parse_folder(folder)
    fig,(ax1) = plt.subplots(1,1)
    colors = ['k','m','y','c','r','g','b']
    for exp in data:
        ax1.errorbar(exp[1], exp[2], yerr=exp[3], fmt='o', color=colors.pop(), markersize=3, label=exp[0])
    handles, labels = ax1.get_legend_handles_labels()
    handles = [h[0] for h in handles]
    ax1.legend(handles, labels)
    plt.xlabel('Input Voltage (V)')
    plt.ylabel('Output Voltage (V)')
    plt.title('Input and Output Voltages for All Temperatures')
    plt.show()

def graph_exp(filename):
    """graph single experiment from picoscope exp folder.
    also print results and latex table"""
    temperature = filename.split('/')[-1]
    x,y = parse_exp_folder(filename)
    xvals, yvals, std_devs = error_propogation(x,y)
    data, maxima, minima = minima_maxima(xvals,yvals)
    output = print_data(data)
    print(output)
    table = create_table(output)
    print(table)
    for i in range(len(xvals)):
        plt.errorbar(xvals[i], yvals[i], yerr=std_devs[i], fmt='o', markersize=3, color='g' if i in minima else 'r' if i in maxima else 'b')
    plt.xlabel('Input Voltage (V)')
    plt.ylabel('Output Voltage (V)')
    plt.title(temperature)
    plt.show()

# Either starts on local max or min
# "Iterate" until get to first max
# Start with "looking for max," once found go into "looking for min"
# Only considering drops from max, so bounded by first and last max

def minima_maxima(xvals, yvals):
    """takes in a sorted set of xvals and yvals for one experiment
    returns array of arrays
    each array: [local max x, local max y, local min x, local min y, drop size,
    next local max x, next local max y, distance between maxima]
    also returns [indices of maxima], [indices of minima]"""
    data = []
    looking_for_max = True
    maxima = []
    minima = []
    for i in range(len(xvals)-1):
        if looking_for_max:
            if yvals[i+1] < yvals[i]:
                maxima.append(i)
                looking_for_max = False
        else:
            if yvals[i+1] > yvals[i]:
                minima.append(i)
                looking_for_max = True
    for i in range(len(maxima)-1):
        data.append([xvals[maxima[i]], yvals[maxima[i]], xvals[minima[i]],
                     yvals[minima[i]], yvals[maxima[i]]-yvals[minima[i]],
                     xvals[maxima[i+1]], yvals[maxima[i+1]],
                     xvals[maxima[i+1]]-xvals[maxima[i]]])
    # Add final minimum and drop if get final local min before max
    if len(maxima) == len(minima):
        data.append([xvals[minima[-1]], yvals[minima[-1]],
                     yvals[maxima[-1]]-yvals[minima[-1]]])
    return data, maxima, minima

def print_data(data):
    """takes in return value of minima_maxima function, returns string of
    data in more readable form"""
    temp = ''
    if len(data[-1]) == 3:
        temp = data[-1]
        data=data[:-1]
    maxima_x = []
    maxima_y = []
    minima_x = []
    minima_y = []
    drops = []
    distances = []
    for i in data:
        maxima_x.append(i[0])
        maxima_y.append(i[1])
        minima_x.append(i[2])
        minima_y.append(i[3])
        drops.append(i[4])
        distances.append(i[7])
    if temp:
        minima_x.append(temp[0])
        minima_y.append(temp[1])
        drops.append(temp[2])
    maxima_x.append(data[-1][5])
    maxima_y.append(data[-1][6])
    output = ''
    output += 'Maxima:'
    for i in range(len(maxima_x)):
        output += '\n('+stringify(maxima_x[i])+', '+stringify(maxima_y[i])+')'
    output += '\n\nMinima:'
    for i in range(len(minima_x)):
        output += '\n('+stringify(minima_x[i])+', '+stringify(minima_y[i])+')'
    output += '\n\nDrop sizes:'
    for i in drops:
        output += '\n'+stringify(i)
    output += '\n\nDistances between peaks:'
    for i in distances:
        output += '\n'+stringify(i)
    return output

def stringify(flt):
    """turn float into rounded string"""
    return str(round(flt,2))

def quick_graph(name):
    """shorthand for graphing one exp"""
    graph_exp('phys243/data/'+name)

def create_table(data):
    """takes in return of print_data fct, returns string; latex table"""
    ls = data.split('\n')
    maxima = []
    minima = []
    drops = []
    distances = []
    ls.remove("Maxima:")
    ls.remove("Minima:")
    ls.remove("Drop sizes:")
    ls.remove("Distances between peaks:")
    # Get list of each column
    while(ls[0]):
        maxima.append(ls.pop(0))
    ls.remove('')
    while(ls[0]):
        minima.append(ls.pop(0))
    ls.remove('')
    while(ls[0]):
        drops.append(ls.pop(0))
    ls.remove('')
    while ls:
        distances.append(ls.pop(0))
    # Build table base
    output = '\\begin{table}[htbp]\n\\centering\n\\begin{tabular}{llll}\nMaximum (V,V) & Minimum(V, V) & Voltage Drop (V) & Gap to Next Minimum (V)\\\\\n\\hline\n'
    # Add row line by line
    while maxima:
        output += maxima.pop(0)+'&'
        if minima:
            output += minima.pop(0)
        output += '&'
        if drops:
            output += drops.pop(0)
        output += '&'
        if distances:
            output += distances.pop(0)
        output += '\\\\\n'
    output = output[:-3]+'\n\\end{tabular}\n\\caption{Relationship between maximum and minimum current points at [temp].}\n\\label{tab:Table [n]}\n\\end{table}'
    return output
