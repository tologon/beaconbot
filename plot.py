from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import atexit
from platform import Platform
from localization import Localizer
from numpy import sin,cos,array
from time import sleep
from math import pi as PI

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="BeaconBot")
win.resize(800,800)
win.setWindowTitle('BeaconBot Vizualization')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Produces a list of x and y coords
# that plot a circle ([x1, x2,...], [y1, y2,...])
def getCircle(radius, offset):
    circle_x = array([cos(PI*(i+1)/180.0)*radius + offset[0] for i in range(0, 360)])
    circle_y = array([sin(PI*(i+1)/180.0)*radius + offset[1] for i in range(0, 360)])
    return (circle_x, circle_y)

def on_click(event):
    # This gets the (x,y) position of the users mouse
    point = location_plot.getViewBox().mapSceneToView(event.scenePos()).toPoint()
    # Plot the point the and a *very* close point so make it show up on the graph
    location_plot.plot([point.x(), point.x()+0.01], [point.y(), point.y()+0.01], pen=pg.mkPen(width=9, color='g'))

    # Drive the platform there.
    platform.go_to_point(point.x(), point.y())

win.scene().sigMouseClicked.connect(on_click)

# Configure location plot
location_plot = win.addPlot(title="Location")
location_plot.showGrid(x=True, y=True)
location_plot.setLabel('left', 'Y Position', units='cm')
location_plot.setLabel('bottom', 'X Position', units='cm')
location_plot.setXRange(-250, 250)
location_plot.setYRange(-250, 250)

x_data = [0]
y_data = [0]

platform = Platform()
atexit.register(platform.shutdown)
localizer = Localizer()
iterations = 8
scan_time = 1.5
i = 0

while True:
    if i >= iterations:
        # Experimenting with resetting the program and plot
        # when the encoder error becomes too great
        platform.reset()
        localizer.reset()
        location_plot.clear()
        x_data = [0]
        y_data = [0]
        i = 0
    i += 1

    # Get the state of the robot
    x = platform.x()
    y = platform.y()
    beacon_dist = platform.get_beacon_distance(scan_time)
    # The Kalman filter gets a little stuck,
    # so reinitializing it increases the accuracy
    # after moving.
    platform.reset_beacon_sensor()
    print "Read distance as %f" % beacon_dist

    # Use the ultrasonic sensor to get the point in front of us
    # that we'll run into if we keep going.
    forward_distance = platform.get_forward_distance()
    object_x = x + forward_distance*cos(platform.theta())
    object_y = y + forward_distance*sin(platform.theta())

    if beacon_dist <= 35:
        # TODO: find a way to not make this
        # happen erroneously
        print "VICTORY!"
        break

    # Give the localizer the sample
    sample = ((x, y), beacon_dist)
    localizer.update(sample)

    # Get an estimate of the beacon location
    position = localizer.target_location()
    print position
    beacon_x, beacon_y = position
    #beacon_x *= -1

    print beacon_x
    print beacon_y

    # Graphics
    # --------
    circle_x, circle_y = getCircle(beacon_dist, (platform.x(), platform.y()))
    location_plot.plot(circle_x, circle_y, pen=pg.mkPen(width=1, color='w'))
    x_data.append(platform.x())
    y_data.append(platform.y())
    location_plot.plot(x_data, y_data, pen=pg.mkPen(width=4.5, color='r')) # robot path
    location_plot.plot([beacon_x, beacon_x+0.01], [beacon_y, beacon_y+0.01], pen=pg.mkPen(width=9, color='g')) # beacon guess
    location_plot.plot([object_x, object_x+0.01], [object_y, object_y+0.01], pen=pg.mkPen(width=20, color='b')) # object
    pg.QtGui.QApplication.processEvents()
    # --------

    platform.go_to_point(beacon_x, beacon_y)

    pg.QtGui.QApplication.processEvents()

if __name__ == '__main__':
    import sys
    atexit.register(platform.shutdown)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
