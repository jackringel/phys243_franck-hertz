# phys243_franck-hertz
Code for parsing csv files from picoscope experiments.

parse_file: Takes in a single filename and returns parameterized numpy arrays - xvals for input voltage, yvals for output voltage. Fairly useless on its own, used for parsing an entire experiment folder

parse_exp_folder: Takes in filename for full picoscope experiment with 64 waveforms. Calls parse_file and iterates through folder, returns 2 arrays aggregating all x and y values

error_propogation: Takes in raw data returned by parse_exp_folder, calls analyze_data and sort_organize to return array of unique x values, an array of arrays showing all the y values each x value is mapped to, and the standard deviation for each of these points

parse_folder: Takes in folder containing multiple experiment folders, calls parse_exp_folder and error_propogation on each to return data for each experiment

main: Calls parse_folder to graph all experiments together. Note that as is the code will not cycle through colors, so modification is required to graph more than 7 experiments at once

graph_exp: Takes in single experiment folder and calls parse_exp_folder, error_propogation, and minima_maxima to graph a single experiment and find local minima and maxima to be shown in different colors. Also calls print_data and create_table to print a list of relevant data (maxima, minima, drop size for each max to min, and distance between maxima) and produce a formatted LaTeX table with this information

minima_maxima: Takes in arrays resulting from error_propogation and returns local maxima of the dataset, local minima, and other information

quick_graph: Shorthand of graph_exp used for my testing

Important/useful functions are main and graph_exp for graphing a single experiment and getting extra data or graphing a group of experiments, or parse_exp_folder, error_propogation, print_data, and create_table for more atomic functions.
