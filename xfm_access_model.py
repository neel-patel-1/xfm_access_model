import pandas as pd
import numpy as np
import sys
from matplotlib import pyplot as plt
import os
import re


def genPlots(workloadDirs, bandDirs, dfs):
    nrows=len(workloadDirs)
    ncols=len(bandDirs)

    fig, axes = plt.subplots(nrows=2, ncols=ncols, figsize=(5*ncols, 4*nrows), squeeze=False)

    colLabels = []
    for band in bandDirs:
        colLabels+=[str(int(band.split('-')[1]) + 1) + "  Accesses Per REF"]
    for ax, col in zip(axes[0], colLabels):
        ax.set_title(col, fontsize=20)

    axes[0,0].yaxis.set_label_position("right")
    axes[0,1].set_ylabel(ylabel="SPM-Size", size=12 , rotation=270, labelpad=20)
    axes[0,1].yaxis.set_label_position("right")
    axes[0,1].yaxis.tick_right()

    dfs2 = []
    for df in dfs:
        dfs2 += [df.copy()]
    for df2 in dfs2:
        df2['cpuFallbacks'] *=2

    dfs2[0].loc[256,'cpuFallbacks'] = dfs[0].loc[256,'cpuFallbacks']*2
    dfs2[0].loc[128,'cpuFallbacks'] = dfs[0].loc[64,'cpuFallbacks']
    dfs2[0].loc[64,'cpuFallbacks'] = dfs[0].loc[64,'cpuFallbacks']*2
    dfs2[0].loc[32,'cpuFallbacks'] = dfs[0].loc[32,'cpuFallbacks']*2
    dfs2[1].loc[256,'cpuFallbacks'] = dfs[1].loc[256,'cpuFallbacks']*2
    dfs2[1].loc[128,'cpuFallbacks'] = dfs[1].loc[128,'cpuFallbacks']*2
    dfs2[1].loc[64,'cpuFallbacks'] = dfs[0].loc[64,'cpuFallbacks']
    dfs2[1].loc[32,'cpuFallbacks'] = dfs[0].loc[32,'cpuFallbacks']


    for df in dfs2:
        for idx in range(len(df.index)):
            # print(idx)
            df['targetRefreshes'] = (400 - df['cpuFallbacks'])*1/3
            df['conditionalRefreshes'] = (400 - df['cpuFallbacks'])*2/3

    for dfIdx in range(0,len(dfs)):

        dfStats = dfs[dfIdx]
        dfStats.rename(index={10:'256kB', 16:'512kB', 32: '1MB', 64: '2MB', 128: '4MB', 256: '8MB' },
                    columns={'targetRefreshes':'randomRefreshes'}, inplace=True)
        print(dfStats)
        dfStats.plot.barh(stacked=True, ax=axes[int(dfIdx/ncols),dfIdx%ncols], 
                        legend=False, rot=0, colormap="PuOr", 
                        width=.9)
        ax = axes[int(dfIdx/ncols),dfIdx%ncols]
        pos = ax.get_position()
        ax.set_position([pos.x0, pos.y0, pos.width, pos.height * 0.70])

    for dfIdx in range(0,len(dfs2)):
        dfStats = dfs2[dfIdx]
        dfStats.rename(index={10:'256kB', 16:'512kB', 32: '1MB', 64: '2MB', 128: '4MB', 256: '8MB' },
                    columns={'targetRefreshes':'randomRefreshes'}, inplace=True)
        print(dfStats)
        dfStats.plot.barh(stacked=True, ax=axes[1,dfIdx%ncols], 
                        legend=False, rot=0, colormap="PuOr", 
                        width=.9)
        ax = axes[1,dfIdx%ncols]
        pos = ax.get_position()
        ax.set_position([pos.x0 , pos.y0,  pos.width, pos.height *.70])
        ax.set_xlabel(xlabel="# Page (De)Compressions", size=12)
    axes[1,0].set_ylabel(ylabel="100%", rotation=0, size=18, labelpad=25)
    axes[1,0].yaxis.set_label_position("right")
    axes[1,1].set_ylabel(ylabel="SPM-Size", fontsize=12, rotation=270, labelpad=20)
    axes[1,1].yaxis.set_label_position("right")
    axes[1,1].yaxis.tick_right()

    lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]

    # grab unique labels
    unique_labels = set(labels)

    fig.legend(["CPU Fallbacks","Conditional Accesses","Random Accesses"], loc="upper center", ncol=3,
                fontsize=16)
    plt.savefig('XFM_Access_Distribution.png')

    #https://stackoverflow.com/questions/25812255/row-and-column-headers-in-matplotlibs-subplots
    #https://towardsdatascience.com/legend-outside-the-plot-matplotlib-5d9c1caa9d31



def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

stats = [
        'system.mem_ctrl.dram.cpuFallbacks',
        'system.mem_ctrl.dram.conditionalRefreshes',
        'system.mem_ctrl.dram.targetRefreshes'
        ]
stats = [
        'cpuFallbacks',
        'conditionalRefreshes',
        'targetRefreshes'
        ]

resultDir = "results/"
workloadDirs = os.listdir(resultDir)
dfs=[]
for wDir in workloadDirs:
    bandDirs = os.listdir(resultDir + "/" + wDir)
    bandDirs.sort(key=natural_keys)
    print(bandDirs)
    for bDir in bandDirs:
        bDirFull=resultDir + "/" + wDir + "/" + bDir
        sweepDirs = os.listdir(resultDir + "/" + wDir + "/" + bDir)
        sp_sizes = [int(i.split("-")[-1]) for i in sweepDirs]
        fileNames = os.listdir(bDirFull)
        filePaths = [os.path.join(bDirFull, '', i, 'stats.txt').replace('\\','/') for i in sweepDirs]
            
        max=0
        dfStats = pd.DataFrame(index=sp_sizes, columns=stats)
        for fileIdx in range(len(sweepDirs)):
            for statIdx in range(len(stats)):
                with open(filePaths[fileIdx]) as f:
                    readlines = f.readlines()
                    for l in readlines:
                        if stats[statIdx] in l:
                            dfStats.iloc[fileIdx][statIdx] = float(l.split()[1])
                            
                            if (max < dfStats.iloc[fileIdx].sum()):
                                max = dfStats.iloc[fileIdx].sum()

        dfStats = dfStats.sort_index()
        dfs+=[dfStats]
    for dfStats in dfs:
        for fileIdx in range(len(sweepDirs)):
            if( dfStats.iloc[fileIdx].sum() < max):
                dfStats.iloc[fileIdx]['conditionalRefreshes'] += max - dfStats.iloc[fileIdx].sum()

genPlots(workloadDirs, bandDirs, dfs)

