import pygame
import serial
import sys
from pygame.locals import *
from serial.tools.list_ports import comports
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class GUI(QWidget):
	"""This is the GUI Class. It creates a GUI that can be interacted with an xbox 360 controller"""


    def __init__(self, *args, **kwargs):
    	"""This constructor creates the GUI class and setups the view"""
        super(GUI, self).__init__(*args, **kwargs)

        self.comm = Communications()

        pygame.init()

        # Set up the joystick
        pygame.joystick.init()

        self.my_joystick = None
        self.joystick_names = []
        self.g_keys = None
        self.axes1 = None
        self.axes2 = None

        # Enumerate joysticks
        for i in range(0, pygame.joystick.get_count()):
            self.joystick_names.append(pygame.joystick.Joystick(i).get_name())
        print(self.joystick_names)

        # By default, load the first available joystick.
        if len(self.joystick_names) > 0:
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()

        # Start timer for controller polling
        self.__timer_init = QTimer()
        self.__timer_init.timeout.connect(self.pollController)
        self.__timer_init.setSingleShot(False)
        self.__timer_init.start(50)

        self.button_array = []
        self.axes_array = []
        self.hat_array = []
        self.plot_array = []
        self.axes1 = None
        self.initUI()


    def initUI(self):
    	"""This function creates the UI via QtGUI"""
        # Layout for axes display
        vbox_axes = QVBoxLayout()
        vbox_axes.addStretch(1)
        label_axes = QLabel(self)
        label_axes.setText('Axes')
        vbox_axes.addWidget(label_axes)
        self.axes1 = AxesWidget()
        self.axes2 = AxesWidget()
        # Assume 4 axes are on controller
        # for i in range(0, self.my_joystick.get_numaxes()):
        for name in ['Movement', 'Camera']:
            slider = QSlider(Qt.Horizontal, self)
            slider.setRange(-100.0, 100.0)
            self.axes_array.append(slider)
            label = QLabel(self)
            label.setText(name + '-X')
            vbox_axes.addWidget(label)
            vbox_axes.addWidget(slider)

            slider = QSlider(Qt.Horizontal, self)
            slider.setRange(-100.0, 100.0)
            self.axes_array.append(slider)
            label = QLabel(self)
            label.setText(name + '-Y')
            vbox_axes.addWidget(label)
            vbox_axes.addWidget(slider)

        hbox_axesplot = QHBoxLayout()

        vbox = QVBoxLayout()
        axesTitle = QLabel(self)
        axesTitle.setText("Movement Axes")
        vbox.addWidget(axesTitle)
        self.axes_array[0].valueChanged[int].connect(self.axes1.set_x_value)
        self.axes_array[1].valueChanged[int].connect(self.axes1.set_y_value)
        vbox.addWidget(self.axes1)
        hbox_axesplot.addLayout(vbox)

        vbox = QVBoxLayout()
        axesTitle = QLabel(self)
        axesTitle.setText("Camera Axes")
        vbox.addWidget(axesTitle)
        self.axes_array[2].valueChanged[int].connect(self.axes2.set_x_value)
        self.axes_array[3].valueChanged[int].connect(self.axes2.set_y_value)
        vbox.addWidget(self.axes2)
        hbox_axesplot.addLayout(vbox)

        vbox_axes.addLayout(hbox_axesplot)

        # Layout for button checkboxes
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addStretch(1)
        label_buttons = QLabel(self)
        label_buttons.setText('Buttons')
        for i in range(0, self.my_joystick.get_numbuttons()):
            cb = QCheckBox(str(i), self)
            self.button_array.append(cb)
            cb.setEnabled(False)
            cb.setChecked(False)
            hbox_buttons.addWidget(cb)

        # Layout for D-pad
        hbox_dpad = QHBoxLayout()
        label_dpad = QLabel(self)
        label_dpad.setText('D-Pad')
        for i in range(0, self.my_joystick.get_numhats()):
            lbl_2 = QLabel(self)
            self.hat_array.append(lbl_2)
            lbl_2.setText(str(self.my_joystick.get_hat(i)))
            hbox_dpad.addWidget(lbl_2)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(vbox_axes)
        vbox.addWidget(label_buttons)
        vbox.addLayout(hbox_buttons)
        vbox.addWidget(label_dpad)
        vbox.addLayout(hbox_dpad)

        button = QPushButton("Reset Motors")
        button.clicked.connect(self.send_reset)
        vbox.addWidget(button)

        # self.setGeometry(300, 300, 300, 150)
        self.setLayout(vbox)

        # Qt show window
        self.show()

    def pollController(self):
    	"""This function pulls data from the xbox controller"""

        # Values ranges to collect and send to Arduino
        # 0: Left Stick Y, 0-100
        # 1: Left Stick X, 0-100
        # 2: Right Stick Y, 0-100
        # 3: Right Stick X, 0-100
        # 4: Triggers, 0-100
        # 5-8: A, B, X, Y
        # 9-10: Bumpers
        # 11-12: Back, Start
        # 13: Left Stick Button
        # 14: Right Stick Button
        # 15: Hat Switch, 0-8
        # For Hat, 0 is resting, 1:NW, 2:N, continues clockwise
        g_keys = pygame.event.get()
        for event in g_keys:
            if event.type == JOYAXISMOTION or JOYBALLMOTION or JOYBUTTONDOWN or JOYBUTTONUP or JOYHATMOTION:
                # for i in range(0, self.my_joystick.get_numaxes()):
                #     ax_value = self.my_joystick.get_axis(i)
                #     self.axes_array[i].setValue(ax_value * 100)

                # For display only
                if self.my_joystick.get_numaxes() == 5:
                    self.axes_array[0].setValue(self.my_joystick.get_axis(0) * 100)  # left stick
                    self.axes_array[1].setValue(self.my_joystick.get_axis(1) * 100)  # left stick
                    self.axes_array[2].setValue(self.my_joystick.get_axis(4) * 100)  # right stick
                    self.axes_array[3].setValue(self.my_joystick.get_axis(3) * 100)  # right stick

                self.axes1.repaint()
                self.axes2.repaint()

                for i in range(0, self.my_joystick.get_numbuttons()):
                    state = self.my_joystick.get_button(i) == 1
                    self.button_array[i].setChecked(state)

                for i in range(0, self.my_joystick.get_numhats()):
                    state = self.my_joystick.get_hat(i)
                    self.hat_array[i].setText(str(state))

                # this is to collect the byte values to send to Arduino
                to_send = bytearray(16)

                # read value and flip sign so that -1 is stick-down and +1 is stick-up
                yStick = -self.my_joystick.get_axis(1)
                # map value 0 to stick center, and value 100 to stick-up. Anything below stick-center is 0.
                if yStick <= 0:  # from 0 to -1.0
                    yStick = 0
                else:  # from 0 to 1.0
                    yStick *= 100

                # Collect bytes to send from joystick
                to_send[0] = int(yStick)  # Left stick Y
                to_send[1] = int(getAxisValueInPercentage(self.my_joystick.get_axis(0)))  # Right Stick X
                to_send[2] = int(getAxisValueInPercentage(-self.my_joystick.get_axis(4)))  # Right Stick Y
                to_send[3] = int(getAxisValueInPercentage(self.my_joystick.get_axis(3)))  # Right Stick X
                to_send[4] = int(getAxisValueInPercentage(self.my_joystick.get_axis(2)))  # Trigger buttons
                to_send[5] = (self.my_joystick.get_button(0))  # A or Cross
                to_send[6] = (self.my_joystick.get_button(1))  # B or Circle
                to_send[7] = (self.my_joystick.get_button(2))  # X or Square
                to_send[8] = (self.my_joystick.get_button(3))  # Y or Triangle
                to_send[9] = (self.my_joystick.get_button(4))  # Left Bumper
                to_send[10] = (self.my_joystick.get_button(5))  # Right Bumper
                to_send[11] = (self.my_joystick.get_button(6))  # Back or Select
                to_send[12] = (self.my_joystick.get_button(7))  # Start
                to_send[13] = (self.my_joystick.get_button(8))  # Left Stick Button
                to_send[14] = (self.my_joystick.get_button(9))  # Right Stick Buttpn
                to_send[15] = 0  # D-Pad

                # This is the flag in the array
                to_send.insert(0, 250)
                self.comm.sendData(to_send)

                # For debug from Python, uncomment
                dumb = []
                for b in to_send:
                    dumb.append(b)
                print(dumb)

                # For debug from Arduino, uncomment
                # self.comm.getBytesAvailableToRead()

    def quit(self):
    	"""This function will quit the program and stop the GUI"""
        if self.my_joystick and self.my_joystick.get_init():
            self.my_joystick.quit()
        self.run_timer.stop()
        pygame.quit()

    # Overrides
    def closeEvent(self, event):
    	"""This function will close the event being run"""
        # do stuff
        self.quit()
        event.accept()  # let the window close

    def send_reset(self):
    	"""This function will reset the motors"""
        to_send = bytearray(0)
        to_send.insert(0, 251)
        self.comm.sendData(to_send)
        print ('Motors Are Reset!')


def getAxisValueInPercentage(axisValue:float)->int:
	"""This function takes in an axisValue and outputs a percentage as an int"""
    return int(((2.0 - (1.0 - axisValue)) * 100.0) / 2.0)

# Assumes range on axes is -100 to 100
class AxesWidget(QWidget):
	"""This class creates a widget that can convert a joystick to a view"""
    def __init__(self):
    	"""This constructor creates the widget"""
        super().__init__()
        self.initUI()
        self.value = (0, 0)

    def initUI(self):
    	"""This function initalizes the UI"""
        self.setMinimumSize(120, 120)
        self.setMaximumSize(120, 120)

    def set_x_value(self, x):
    	"""This function sets the x value"""
        self.value = (x, self.value[1])

    def set_y_value(self, y):
    	"""This function sets the y value"""
        self.value = (self.value[0], y)

    def paintEvent(self, e):
    	"""This function will create the view"""
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
    	"""This function will draw the widget on the view"""
        size = self.size()
        h = size.height()
        # step = int(round(h / 200))
        qp.setPen(QColor(255, 0, 0))
        qp.setBrush(QColor(0, 0, 0))
        x = self.value[0] / 2 + 60
        y = self.value[1] / 2 + 60
        qp.drawEllipse(x, y, 7, 7)
        qp.setPen(QColor(0, 0, 0))
        qp.setBrush(QColor(0, 0, 0, 0))
        qp.drawRect(9, 9, h - 11, h - 11)


class Communications:
	"""This class is the communications class and takes care of all of the Arduino interactions"""
    def __init__(self):
    	"""This constructor creates the communication class"""
        self.SerialPort = serial.Serial()
        self.SerialPort.baudrate = 38400
        self.SerialPort.write_timeout = 0.1
        self.getListofPorts()
        self.openPort()

    def __del__(self):
    	"""This function closes the serial port"""
        if self.SerialPort.is_open:
            self.SerialPort.close()

    def getListofPorts(self):
    	"""This function returns all of the ports"""
        ports = comports()
        for port in ports:
            print(port)
        return ports

    def openPort(self, port_name="COM7"):
    	"""This function opens the specified port"""
        self.SerialPort.port = port_name
        self.SerialPort.open()

    def sendData(self, vals: bytearray):
    	"""This function writes the data to the serial port"""
        self.SerialPort.write(vals)

    def getBytesAvailableToRead(self):
    	"""This function reads the bytes"""
        while self.SerialPort.in_waiting:
            print(self.SerialPort.readline())


if __name__ == "__main__":
	"""This function is the main function"""
    gui = QApplication(sys.argv)
    gui.setApplicationName("ControllerGUI")
    window = GUI()
    gui.exec_()
