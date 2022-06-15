from typing import Union
from collections.abc import Iterable
import sys
import math
import statistics
import copy

import numpy as np
import matplotlib.axes as axes
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

import regplot

FIGURE_WIDTH = 9
FIGURE_HEIGHT = 5

## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
class RegressionPlotter:
    def do_poly_regression(array_y, array_x,
                            splines:(Union[int,Iterable])=1, order:(int)=1):
        
        if isinstance(splines,Iterable):
            slopes = []
            for spl in splines:
                spline_slopes = RegressionPlotter.do_splines("rank",array_y, array_x, splines=spl, order=order)
                slopes.extend(spline_slopes)                                
        else:
            slopes = RegressionPlotter.do_splines("rank",array_y, array_x, splines=splines, order=order)
        return slopes

    # #############################################
    def plot_histogram(array_x, bins, title:(str),
                        figure_id:(str)=None,
                        xlabel:(str)=None, 
                        ylabel:(str)=None):

        if figure_id == None:
            figure_id = title

        figure = plt.figure(figure_id, figsize=(FIGURE_WIDTH,FIGURE_HEIGHT))
        ax = figure.gca()

        plt.hist(array_x, 
                bins=bins, 
                range=None, 
                density=False, 
                weights=None, 
                cumulative=False, 
                bottom=None, 
                histtype='bar', 
                align='mid', 
                orientation='vertical', 
                rwidth=None, 
                log=False, 
                color=None, 
                label=None)

        avg=statistics.mean(array_x)
        std=statistics.stdev(array_x)

        if xlabel == None:
            xlabel = "decision values, avg={avg} std={std}"
        if ylabel == None:
            ylabel = "frequency"
        ax.set(xlabel=xlabel, ylabel=ylabel)

        plt.draw()

        return 

    # #############################################
    def plot_regression(array_y, array_x, title:(str), 
                        splines:(Union[int,Iterable])=1, 
                        order:(int)=1, 
                        ax:(axes.Axes)=None, figure_id:(str)=None,
                        xlabel:(str)=None, ylabel:(str)=None,
                        scatter:(bool)=True,
                        average_array:(Iterable)=None,
                        benchmark_arrays:(Iterable)=None):
        
        if figure_id == None:
            figure_id = title

        # cid = figure.canvas.mpl_connect('button_press_event', onclick)
        
        figure = plt.figure(figure_id, figsize=(FIGURE_WIDTH,FIGURE_HEIGHT))
        ax = figure.gca()

        # scatter
        regplot.regplot(
            x=np.array([array_x])[0],
            y=np.array([array_y])[0],
            color="#36688D",
            #x_jitter=.1,
            scatter_kws={"color": "#36688D"},
            label='Data',
            order=order,
            fit_reg=False,
            scatter=scatter,
            line_kws={"color": "#F49F05"},
            ax=ax
        )

        if isinstance(splines,Iterable):
            linecolors = ["orange","blue","green","violet","yellow"]
            color_ndx=0
            slopes = []
            for spl in splines:
                linecolor = linecolors[color_ndx]
                spline_slopes = RegressionPlotter.do_splines('plot', 
                                    array_y, array_x, splines=spl, 
                                    order=order, ax=ax,
                                    linecolor=linecolor)
                slopes.extend(spline_slopes)                                
                color_ndx = (color_ndx + 1)%len(linecolors)
        else:
            slopes = RegressionPlotter.do_splines('plot', 
                                    array_y, array_x, splines=splines, 
                                    order=order, ax=ax)

        # Plot the average line
        if average_array == None:
            y_mean = [np.mean(array_y)]*len(array_x)
        else:
            while len(average_array) < len(array_x):
                average_array.append(average_array[-1])
            while len(average_array) > len(array_x):
                average_array.pop()
            # y_mean = np.array([average_array])[0]
            y_mean = average_array
        ax.plot(array_x,y_mean, label='Mean', linestyle='--', color="#0F0F00")
        ## ax.legend(loc='lower right')

        if not benchmark_arrays == None:
            ax.plot(benchmark_arrays[1],benchmark_arrays[0], 
                                 label='Benchmark', linestyle='dotted', color="#002F08")

        if xlabel == None:
            xlabel = "{} (last spline slope={:1.7f})".format(title,slopes[-1])
        if ylabel == None:
            ylabel = "score"
        ax.set(xlabel=xlabel, ylabel=ylabel)

        plt.draw()

        return slopes

    ## #############################################
    def calc_slope(fit_results, array_x):
        #print(f"{title}: pvalues {fit_results.pvalues}")
        #print(f"{title}: tvalues {fit_results.tvalues}")
        vals = fit_results.fittedvalues
        deltay = vals[-1] - vals[0]
        max_x, min_x = RegressionPlotter.minmax(array_x)
        deltax = max_x-min_x
        if deltax > 0:
            slope = deltay/deltax
        else:
            slope = math.nan
        # print(f"{title}: slope of fittedvalues {slope:1.6f}")
        return slope

    ## #############################################
    def do_splines(which, array_y, array_x, 
                    splines:(int)=1, order:(int)=1, 
                    ax:(axes.Axes)=None, linecolor="#F49F05"):

        my_array_x = copy.copy(array_x)
        my_array_x.sort()
        spline_length = int(len(my_array_x)/splines)
        results = []
        slopes = []

        for spline in range(splines):
            spline_start = spline*spline_length
            if spline == splines-1:
                spline_end = len(my_array_x)
            else:
                spline_end = spline_start+spline_length
            spline_array_x = my_array_x[spline_start:spline_end]
            spline_array_y = array_y[spline_start:spline_end]
            if which == 'rank':
                fit_results = (
                    regplot.polyfit(
                        x=np.array([spline_array_x])[0],
                        y=np.array([spline_array_y])[0],
                        dropna=True,
                        order=order
                    ))
            else:                
                fit_results = (
                    regplot.regplot(
                        x=np.array([spline_array_x])[0],
                        y=np.array([spline_array_y])[0],
                        color="#36688D",
                        scatter=False,
                        # label='Data',
                        order=order,
                        fit_reg=True,
                        line_kws={"color": linecolor},
                        ax=ax
                    ))
            results.append(fit_results)
            slopes.append(RegressionPlotter.calc_slope(fit_results, spline_array_x))

        return slopes

    def minmax(coll):
        max_x = sys.float_info.min
        min_x = sys.float_info.max
        for x in coll:
            max_x = max(x,max_x)
            min_x = min(x, min_x)   
        return max_x, min_x          

