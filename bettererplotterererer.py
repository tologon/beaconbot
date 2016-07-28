from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import atexit
from numpy import arctan,sqrt
from platform import Platform
from beacon import BeaconSensor
from localization import Localizer
from numpy import sin,cos,array,arctan2
from time import sleep

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="BeaconBot")
win.resize(800,400)
win.setWindowTitle('BeaconBot Vizualization')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Configure location plot
location_plot = win.addPlot(title="Location")
location_plot.showGrid(x=True, y=True)
location_plot.setLabel('left', 'Y Position', units='cm')
location_plot.setLabel('bottom', 'X Position', units='cm')
location_plot.setXRange(-100, 100)
location_plot.setYRange(-100, 100)

# Configure the heading plot
heading_plot = win.addPlot(title="Heading")
heading_plot.showGrid(x=True, y=True)
heading_plot.setXRange(-1, 1)
heading_plot.setYRange(-1, 1)



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
beacon_sensor = BeaconSensor('0c:f3:ee:04:22:3d')

my_x = 0
my_y = 0
my_theta = 0

def on_click(event):
    point = location_plot.getViewBox().mapSceneToView(event.scenePos()).toPoint()

    # Plot the point the user clicked
    location_plot.plot([point.x(), point.x()+0.01], [point.y(), point.y()+0.01], pen=pg.mkPen(width=9, color='g'))
    target_x = point.x()
    target_y = point.y()

    my_x, my_y, my_theta = platform.get_state()
    x_diff = target_x-my_x
    y_diff = target_y-my_y

    to_turn = -1*(arctan2(y_diff, x_diff) - my_theta) * (360/(2*3.1415))
    print "---"
    print "Step 1: angle calculation %f = -1 * (arctan2(%f, %f) - %f) * (360/2*3.1415)" % (to_turn, y_diff, x_diff, my_theta)
    print
    #print "x_sign=%f y_sign=%f to_turn=%f" % (x_diff, y_diff, to_turn)

    while to_turn > 180.0:
        to_turn -= 360.0
    while to_turn < -180.0:
        to_turn += 360.0

    to_drive = sqrt((x_diff)**2+(y_diff)**2)
    #to_drive = 5

    print "Step 2: turning %f%%." % (to_turn)
    platform.turn(to_turn)
    sleep(0.5)
    print "Step 3: driving %fcm." % (to_drive)
    platform.drive_straight(to_drive) 
    print

    my_x, my_y, my_theta = platform.get_state()
    print "Step 4: results after driving: (%f, %f, %f)" % (my_x, my_y, my_theta*360/(2.0*3.1415))
    print
    print "---"

    # Save the location
    x_data.append(my_x)
    y_data.append(my_y*-1)

    location_plot.plot(x_data, y_data, pen=pg.mkPen(width=4.5, color='r'))

    heading_plot.clear()
    heading_plot.plot([0, cos(my_theta)], [0, -1*sin(my_theta)], pen='b')

win.scene().sigMouseClicked.connect(on_click)


while True:
    pg.QtGui.QApplication.processEvents()

if __name__ == '__main__':
    import sys
    atexit.register(platform.shutdown)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
