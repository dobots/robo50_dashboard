
from python_qt_binding.QtCore import QSize, Qt
from QtGui import *
from rqt_robot_dashboard.widgets import IconToolButton
import thread

class MotorButton(IconToolButton):
    def __init__(self, context, index, on_motor_control):
        self._on_icon = ['bg-green.svg', 'ic-motors.svg']
        self._off_icon = ['bg-red.svg', 'ic-motors.svg']
        icons = [self._off_icon, self._on_icon]

        super(MotorButton, self).__init__("motor_%s" %index, icons=icons)

        self.setFixedSize(self._icons[0].actualSize(QSize(50,30)))
        self.clicked.connect(self.on_click)
        self.update_state(False)
        self.setToolTip('Motor %s' %(index+1))

        self.context = context

        self.motor_widget = MotorWidget('motor_widget_%s' %index, index, on_motor_control)
        self.motor_on = False

    def on_click(self):
        if not self.motor_on:
            self.context.add_widget(self.motor_widget)
        else:
            self.context.remove_widget(self.motor_widget)
        self.motor_on = not self.motor_on
        self.update_state(self.motor_on)


class MotorWidget(QWidget):
    def __init__(self, name, index, on_motor_control):
        super(MotorWidget, self).__init__()

        self.on_motor_control = on_motor_control
        self.index = index
        self.motor_on = False

        obj_name = "Motor %s" %(index+1)
        self.setObjectName(obj_name)
        self.setWindowTitle(obj_name)

        motor_layout = QVBoxLayout()

        # Slider
        self.motor_slider_value = QLabel()
        self.motor_slider_value.setText(str(0))

        self.motor_slider = QSlider(Qt.Horizontal)
        self.motor_slider.setRange(-100, 100)
        self.motor_slider.setValue(0)
        self.motor_slider.setTracking(False)
        self.motor_slider.sliderMoved.connect(lambda x: self.update_value(x))
        self.motor_slider.valueChanged.connect(lambda x: self.update_motor(x))

        motor_slider_lay = QHBoxLayout()
        motor_slider_lay.addWidget(self.motor_slider)
        motor_slider_lay.addWidget(self.motor_slider_value)
        motor_layout.addLayout(motor_slider_lay)

        # Buttons
        min_button = QPushButton("MIN")
        min_button.clicked.connect(lambda: self.motor_slider.setValue(self.motor_slider.minimum()))

        zero_button = QPushButton("0")
        zero_button.clicked.connect(lambda: self.motor_slider.setValue(0))

        max_button = QPushButton("MAX")
        max_button.clicked.connect(lambda: self.motor_slider.setValue(self.motor_slider.maximum()))

        motor_buttons_lay = QHBoxLayout()
        motor_buttons_lay.addWidget(min_button)
        motor_buttons_lay.addWidget(zero_button)
        motor_buttons_lay.addWidget(max_button)
        motor_layout.addLayout(motor_buttons_lay)

        self.setLayout(motor_layout)

    def update_motor(self, value):
        self.update_value('--')
        thread.start_new_thread(self.send_motor, (self.index, value))

    def update_value(self, value):
        self.motor_slider_value.setText(str(value))

    def send_motor(self, index, value):
        self.on_motor_control(self.index, value)
        self.update_value(value)
