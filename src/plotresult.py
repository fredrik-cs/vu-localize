import matplotlib.pyplot as plt
from blume.table import table
import numpy as np

X_SCALE = 24.2
X_BIAS = 25.0
Z_SCALE = -24.2
Z_BIAS = 1785.0

def PlotTable(data, name):
    # tab = table()
    fig_background_color = 'white'
    fig_border = 'white'

    columns = ('Average Error', 'Worst Error')
    column_widths = [0.2,0.2]
    rows = (
        '2.4 GHz all trilateration', '2.4 GHz >-80 trilateration', '2.4 GHz >-70 trilateration', '2.4 GHz >-67 trilateration', 
        '5 GHz all trilateration', '5 GHz >-80 trilateration', '5 GHz >-70 trilateration', '5 GHz >-67 trilateration', 
        '2.4 GHz all multilateration', '2.4 GHz >-80 multilateration', '2.4 GHz >-70 multilateration', '2.4 GHz >-67 multilateration', 
        '5 GHz all multilateration', '5 GHz >-80 multilateration', '5 GHz >-70 multilateration', '5 GHz -67 multilateration'
    )
    cell_text = data
    print(data)
    # tab = plt.table(cellText=cell_text,
    #           rowLabels=rows,
    #           colLabels=columns,
    #           loc='center')

    fig = plt.figure(linewidth=2,
           edgecolor=fig_border,
           facecolor=fig_background_color,
           tight_layout={'pad':1},
           #figsize=(5,3)
    )

    tab = table(plt.gca(), cellText=cell_text,
              rowLabels=rows,
              colLabels=columns,
              colWidths=column_widths,
              loc='center',
              cellLoc='center',
              rowLoc='right')
    tab.scale(1, 1.5)

    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.box(on=None)
    plt.subplots_adjust(left=0.2, bottom=0.2)
    
    # plt.show()
    plt.draw()

    plt.savefig(f"{name}-table",
                bbox_inches='tight',
                edgecolor=fig.get_edgecolor(),
                facecolor=fig.get_facecolor(),
                dpi=150)

def PlotHistogram():
    return
    plt.hist()

def PlotPredictionError():
    return
    plt.scatter()
    plt.plot()