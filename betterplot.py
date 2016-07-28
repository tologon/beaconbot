from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import atexit
from numpy import arctan,sqrt
from platform import Platform
from beacon import BeaconSensor
from localization import Localizer
from numpy import sin,cos,array

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

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
location_plot.setXRange(-50, 50)
location_plot.setYRange(-50, 50)

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

def on_click(event):
    point = location_plot.getViewBox().mapSceneToView(event.scenePos()).toPoint()

    # Plot the point the user clicked
    location_plot.plot([point.x(), point.x()+0.01], [point.y(), point.y()+0.01], pen=pg.mkPen(width=9, color='g'))
    target_x = point.x()
    target_y = -1*point.y()

    my_x, my_y, my_theta = platform.get_state()
    to_turn = 0

    new_forward = (target_x - my_x, target_y - my_y)

    current_forward = (cos(my_theta), sin(my_theta))

    angle_numerator = (new_forward[0] * current_forward[0]) + (new_forward[1] * current_forward[1])

    angle_denominator = sqrt((new_forward[0]**2) + (new_forward[1]**2)) * 
    if not (target_x == my_x):
        to_turn = arctan(1.0*(target_y - my_y)/(target_x - my_x)) * (360/(2*3.1415))
    else:
        print "ignored arctan."

    to_turn -= my_theta * (360/(2*3.1415))

    x_sign = target_x-my_x
    y_sign = target_y-my_y
    print "x_sign=%f y_sign=%f" % (x_sign, y_sign)

    if x_sign <= 0:
        if y_sign <= 0:
            to_turn = 90 + to_turn
            pass
            #to_turn = 90 - to_turn
        else:
            pass
            #to_turn = 180 - to_turn
    else:
        if y_sign <= 0:
            pass
    #        to_turn = 180 - to_turn
        else:
            pass
    #        to_turn = 180 - to_turn

    while to_turn > 180.0:
        to_turn -= 360.0
    while to_turn < -180.0:
        to_turn += 360.0

    to_drive = sqrt((target_y-my_y)**2+(target_x-my_x)**2)
    #to_drive = 5

    platform.turn(to_turn)
    print "Turning %f%%." % (to_turn)
    platform.drive_straight(to_drive) 
    print "Driving %fcm." % (to_drive)

    my_x, my_y, my_theta = platform.get_state()
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
