import roslib;roslib.load_manifest('robo50_dashboard')
import rospy

import diagnostic_msgs
import robo50_node.srv
import robo50_node.msg

from rqt_robot_dashboard.dashboard import Dashboard
from rqt_robot_dashboard.widgets import MonitorDashWidget, ConsoleDashWidget, MenuDashWidget, BatteryDashWidget, IconToolButton, NavViewDashWidget
# from QtGui import QMessageBox, QAction, QSlider
from QtGui import *
from python_qt_binding.QtCore import QSize, Qt

from .battery import Robo50Battery
from motor_widget import MotorWidget, MotorButton

import rospkg
import os.path

rp = rospkg.RosPack()

image_path = image_path = os.path.join(rp.get_path('robo50_dashboard'), 'images')

class BreakerButton(IconToolButton):
    def __init__(self, name, onclick):
        self._on_icon = ['bg-green.svg', 'ic-breaker.svg']
        self._off_icon = ['bg-red.svg', 'ic-breaker.svg']
    
        icons = [self._off_icon, self._on_icon]

        super(BreakerButton, self).__init__(name, icons=icons)

        self.setFixedSize(self._icons[0].actualSize(QSize(50,30)))

        self.clicked.connect(onclick)


class Robo50Dashboard(Dashboard):
    def setup(self, context):
        self.message = None

        self._dashboard_message = None
        self._last_dashboard_message_time = 0.0

        # These were moved out of get_widgets because they are sometimes not defined
        # before being used by dashboard_callback. Could be done more cleanly than this
        # though.
        self.lap_bat = BatteryDashWidget("Laptop")
        self.create_bat = Robo50Battery("Create")

        self._set_motor = rospy.ServiceProxy('robo50_node/set_motor', robo50_node.srv.SetMotor)

        self.motors = [MotorButton(self.context, 0, lambda x, y: self.motor_control(x, y)),
                      MotorButton(self.context, 1, lambda x, y: self.motor_control(x, y)),
                      MotorButton(self.context, 2, lambda x, y: self.motor_control(x, y))]

        # This is what gets dashboard_callback going eagerly
        self._dashboard_agg_sub = rospy.Subscriber('diagnostics_agg', diagnostic_msgs.msg.DiagnosticArray, self.dashboard_callback)
        
    def motor_control(self, motor_id, speed):
        try:
            motor_cmd = robo50_node.srv.SetMotorRequest(motor_id, speed)
            self._set_motor(motor_cmd)
        except rospy.ServiceException, e:
            self.message = QMessageBox()
            self.message.setText("Service call failed with error: %s"%(e))
            self.message.exec_()
            return False
          
        return True

    def get_widgets(self):
        return [[MonitorDashWidget(self.context), ConsoleDashWidget(self.context)], 
                self.motors,
                [self.lap_bat, self.create_bat],
                [NavViewDashWidget(self.context)]]

    def dashboard_callback(self, msg):
        self._dashboard_message = msg
        self._last_dashboard_message_time = rospy.get_time()
  
        battery_status = {}  # Used to store Robo50Battery status info
        laptop_battery_status = {}
        op_mode = None
        for status in msg.status:
            print("Status callback %s"%status.name)
            if status.name == "/Power System/Battery":
                for value in status.values:
                    print value
                    battery_status[value.key]=value.value
                    # Create battery actually doesn't check public or check
                    # charging state. Could maybe done by looking at +-
                    # of current value
                    # Below is kobuki battery code.
                    # Best place to fix this is in create driver to match the kobuki
                    # diagnostics 
                    #elif value.key == "Charging State":
                    #    if value.value == "Trickle Charging" or value.value == "Full Charging":
                    #        self.create_bat.set_charging(True)
                    #    else:
                    #        self.create_bat.set_charging(False)
            elif status.name == "/Power System/Laptop Battery":
                for value in status.values:
                    laptop_battery_status[value.key]=value.value

        # If battery diagnostics were found, calculate percentages and stuff  
        if (laptop_battery_status):
            percentage = float(laptop_battery_status['Charge (Ah)'])/float(laptop_battery_status['Capacity (Ah)'])
            self.lap_bat.update_perc(percentage*100)
            self.lap_bat.update_time(percentage*100)
            charging_state = True if float(laptop_battery_status['Current (A)']) > 0.0 else False
            self.lap_bat.set_charging(charging_state)

        if (battery_status):
            self.create_bat.set_power_state(battery_status)
