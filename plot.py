from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import atexit
from numpy import arctan,sqrt
from platform import Platform
from beacon import BeaconSensor
from localization import Localizer
from numpy import sin,cos,array,arctan2
from time import sleep
from math import pi as PI

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="BeaconBot")
win.resize(800,800)
win.setWindowTitle('BeaconBot Vizualization')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Configure location plot
location_plot = win.addPlot(title="Location")
location_plot.showGrid(x=True, y=True)
location_plot.setLabel('left', 'Y Position', units='cm')
location_plot.setLabel('bottom', 'X Position', units='cm')
location_plot.setXRange(-250, 250)
location_plot.setYRange(-250, 250)

# Configure the heading plot
#heading_plot = win.addPlot(title="Heading")
#heading_plot.showGrid(x=True, y=True)
#heading_plot.setXRange(-1, 1)
#heading_plot.setYRange(-1, 1)

x_data = [0]
y_data = [0]

def getCircle(radius, offset):
    pi = 3.1415
    circle_x = array([cos(pi*(i+1)/180.0)*radius + offset[0] for i in range(0, 360)])
    circle_y = array([sin(pi*(i+1)/180.0)*radius + offset[1] for i in range(0, 360)])
    return (circle_x, circle_y)

platform = Platform()
atexit.register(platform.shutdown)
robot_state = platform.get_state()
localizer = Localizer()

def on_click(event):
    point = location_plot.getViewBox().mapSceneToView(event.scenePos()).toPoint()
    # Plot the point the user clicked
    location_plot.plot([point.x(), point.x()+0.01], [point.y(), point.y()+0.01], pen=pg.mkPen(width=9, color='g'))
    platform.go_to_point(point.x(), point.y())

win.scene().sigMouseClicked.connect(on_click)


iterations = 600
i = 0
sampling_time = 1
while True:
    if i >= iterations:
        platform.reset()
        localizer.reset()
        location_plot.clear()
        x_data = [0]
        y_data = [0]
        i = 0
    i += 1

    # Sense
    x = platform.x()
    y = platform.y()
    dist = platform.get_beacon_distance(1)
    print "Read distance as %f" % dist
    platform.reset_beacon_sensor()

    # Calculate the position of the object to avoid
    forward_distance = platform.get_forward_distance()
    object_x = x + forward_distance*cos(platform.theta())
    object_y = y + forward_distance*sin(platform.theta())

    sampling_time = dist/5.0

    if dist <= 35:
        print "VICTORY!"
        break

    # Give the localizer the sample
    sample = ((x, y), dist)
    localizer.update(sample)

    # Get the target location
    go_to = localizer.target_location()

    # Graphics
    circle_x, circle_y = getCircle(dist, (platform.x(), platform.y()))
    location_plot.plot(circle_x, circle_y, pen=pg.mkPen(width=1, color='w'))
    x_data.append(platform.x())
    y_data.append(platform.y())
    location_plot.plot(x_data, y_data, pen=pg.mkPen(width=4.5, color='r'))
    #heading_plot.clear()
    #heading = platform.theta()
    #heading_plot.plot([0, cos(heading)], [0, sin(heading)], pen='b')
    location_plot.plot([go_to[0], go_to[0]+0.01], [go_to[1], go_to[1]+0.01], pen=pg.mkPen(width=9, color='g'))
    location_plot.plot([object_x, object_x+0.01], [object_y, object_y+0.01], pen=pg.mkPen(width=20, color='b'))

    pg.QtGui.QApplication.processEvents()

    platform.go_to_point(go_to[0], go_to[1])

    pg.QtGui.QApplication.processEvents()

if __name__ == '__main__':
    import sys
    atexit.register(platform.shutdown)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
