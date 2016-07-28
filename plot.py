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

def on_click(event):
    point = location_plot.getViewBox().mapSceneToView(event.scenePos()).toPoint()

    # Plot the point the user clicked
    location_plot.plot([point.x(), point.x()+0.01], [point.y(), point.y()+0.01], pen=pg.mkPen(width=9, color='g'))
    target_x = point.x()
    target_y = -1*point.y()

    my_x, my_y, my_theta = platform.get_state()
    to_turn = 0
    if not (target_x == my_x):
        to_turn += arctan(1.0*(target_y - my_y)/(target_x - my_x)) * (360/(2*3.1415))
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
#    def _update_graph():
#        robot_state = platform.get_state() 
#        y_data.append(robot_state[0])
#        x_data.append(-1*robot_state[1])
#        location_plot.plot(x_data, y_data, pen=pg.mkPen(width=4.5, color='r'))
#j        pg.QtGui.QApplication.processEvents()
#    def sense():
#        _update_graph()
#        beacon_sensor.scan(0.01)
#        localizer.update((platform.get_state()[:2], beacon_sensor.getDistance()))

#    _update_graph()

    #sense()

    #my_x, my_y, my_theta = platform.get_state()
    #target_x, target_y = localizer.target_location()
    #location_plot.plot([target_x, target_x+0.01], [target_y, target_y+0.01], pen=pg.mkPen(width=9, color='g'))
    #pg.QtGui.QApplication.processEvents()
    #target_x *= -1
    #target_y *= -1
    #to_turn = -1*arctan((target_y - my_y) / (target_x - my_x)) * (360/(2*3.1415))
    #to_turn -= my_theta*360/(2.0*3.1415)

    #while to_turn > 180.0:
    #    to_turn -= 360.0
    #while to_turn < -180.0:
    #    to_turn += 360.0

    #to_drive = sqrt((target_y-my_y)**2+(target_x-my_x)**2)
    #to_drive = 2

    #print "target=(%f, %f), turn=%f, drive:=%f" % (target_x, target_y, to_turn, to_drive)

    #platform.turn(-1*to_turn)
    #platform.drive_straight(to_drive) 

    #location_plot.plot([target_x, target_x+0.01], [target_y, target_y+0.01], pen=pg.mkPen(width=9, color='g'))
    #pg.QtGui.QApplication.processEvents()
 

    #platform.shutdown()


if __name__ == '__main__':
    import sys
    atexit.register(platform.shutdown)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
