import matplotlib.pyplot as plt
from matplotlib import collections as mc
from blume.table import table
import numpy as np
from src.enums import Maps
from src.coordinates import UnityCoordinate

X_SCALE = 24.2
X_BIAS = 25.0
Z_SCALE = -24.2
Z_BIAS = 1785.0

def PlotTable(data, name):
    # tab = table()
    fig_background_color = 'white'
    fig_border = 'white'

    columns = ('Average Error (m)', 'Worst Error (m)', "Signal Rate (s$^{-1}$)", "Prediction Rate (s$^{-1}$)")
    column_widths = [0.2,0.2,0.15,0.15]
    rows = (
        '2.4 GHz all trilateration', '2.4 GHz >-80 trilateration', '2.4 GHz >-70 trilateration', '2.4 GHz >-67 trilateration', 
        '5 GHz all trilateration', '5 GHz >-80 trilateration', '5 GHz >-70 trilateration', '5 GHz >-67 trilateration', 
        '2.4 GHz all multilateration', '2.4 GHz >-80 multilateration', '2.4 GHz >-70 multilateration', '2.4 GHz >-67 multilateration', 
        '5 GHz all multilateration', '5 GHz >-80 multilateration', '5 GHz >-70 multilateration', '5 GHz -67 multilateration'
    )
    cell_text = data
    # print(data)
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

    plt.savefig(f"experiments/draftthree/tables/table-{name}",
                bbox_inches='tight',
                edgecolor=fig.get_edgecolor(),
                facecolor=fig.get_facecolor(),
                dpi=150)
    plt.clf()
    print(f"Plotted table at experiments/draftthree/tables/table-{name}")

def PlotHistogram(name, errors_x, errors_z, errors_d):
    # return
    ax1: plt.Axes
    ax2: plt.Axes
    ax3: plt.Axes
    plt.rc('axes', titlesize=8)

    fig, (ax1, ax2, ax3) = plt.subplots(1,3)
    ax1.hist(errors_x, bins=40)
    ax1.set_title("Error distribution X (m)")
    
    ax2.hist(errors_z, bins=40)
    ax2.set_title("Error distribution Z (m)")
    
    ax3.hist(errors_d, bins=40)
    ax3.set_title("Error distribution (m)")

    plt.savefig(f"experiments/draftthree/histograms/hist-{name}",
                dpi=150)
    plt.clf()
    print(f"Plotted histogram at experiments/draftthree/histograms/hist-{name}")
    plt.close(fig)
    

def PlotPredictionError(name, floor, predictions:list[UnityCoordinate], realities: tuple):
    # return
    points = list(map(lambda p : (p.x * X_SCALE + X_BIAS, p.z * Z_SCALE + Z_BIAS), predictions))
    counter_points = list(map(lambda p : (p[0] * X_SCALE + X_BIAS, p[1] * Z_SCALE + Z_BIAS), realities))
    max_amount_points = 250
    if floor == 5:
        max_amount_points = 125
    step_size = len(points) / max_amount_points
    points = points[::int(step_size)]
    counter_points = counter_points[::int(step_size)]
    pts = np.array(points)
    cts = np.array(counter_points)

    steps = np.linspace(0,1,len(points))

    image = ''
    if int(floor) == 5:
        image = Maps.FLOOR5
    else:
        image = Maps.FLOOR6
    
    fig, ax = plt.subplots(1)
    image = plt.imread(image)
    ax.set_aspect('equal')
    ax.imshow(image)
        

    lines = list(zip(points, counter_points))

    errors = mc.LineCollection(lines, array = steps, cmap='hsv', linewidths=1, zorder=2)
    ax.add_collection(errors)

    plt.scatter(pts[:, 0], pts[:, 1], marker='*', c='white', s=40, edgecolors='black', zorder=4, linewidths=0.25)
    plt.scatter(cts[:, 0], cts[:, 1], marker='o', c=steps, cmap='hsv', s=10, zorder=3)
    
    plt.savefig(f"experiments/draftthree/scatterplots/scatter-{name}",
                dpi=150)
    plt.clf()
    print(f"Plotted scatterplot at experiments/draftthree/scatterplots/scatter-{name}")
    plt.close(fig)