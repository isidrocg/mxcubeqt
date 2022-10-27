#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import logging

from mxcubeqt.utils import colors
from mxcubeqt.bricks.resolution_brick import ResolutionBrick

from mxcubecore import HardwareRepository as HWR


__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "General"


class AlbaResolutionBrick(ResolutionBrick):

    #Sardana Motor State map
    #state_map = {
        #"ON": MotorStates.READY,
        #"OFF": MotorStates.OFF,
        #"CLOSE": MotorStates.DISABLED,
        #"OPEN": MotorStates.DISABLED,
        #"INSERT": MotorStates.DISABLED,
        #"EXTRACT": MotorStates.DISABLED,
        #"MOVING": MotorStates.MOVING,
        #"STANDBY": MotorStates.READY,
        #"FAULT": MotorStates.FAULT,
        #"INIT": MotorStates.INITIALIZING,
        #"RUNNING": MotorStates.MOVING,
        #"ALARM": MotorStates.ALARM,
        #"DISABLE": MotorStates.DISABLED,
        #"UNKNOWN": MotorStates.UNKNOWN,
    #}


    STATE_COLORS = (
        colors.LIGHT_RED,                   #ON
        colors.LIGHT_RED,                   #OFF
        colors.LIGHT_GREEN,                 #CLOSE
        colors.LIGHT_YELLOW,                #OPEN
        colors.LIGHT_YELLOW,                #INSERT
        colors.LIGHT_YELLOW,                #EXTRACT
        qt_import.QColor(255, 165, 0),      #MOVING
        colors.LIGHT_GREEN,                 #STANDBY
        colors.LIGHT_RED,                   #FAULT
        colors.LIGHT_YELLOW,                #INIT
        colors.LIGHT_YELLOW,                #RUNNING
        colors.LIGHT_RED,                   #ALARM
        colors.LIGHT_RED,                   #DISABLE
        colors.LIGHT_RED,                   #UNKNOWN
    )


    def __init__(self, *args):

        ResolutionBrick.__init__(self, *args)

    def update_gui(self, resolution_ready=None, detector_distance_ready=None):
        """
        Door interlock is optional, because not all sites might have it
        """
        #logging.getLogger("HWR").debug("resolution_ready %s, detector_distance_ready %s" % ( resolution_ready, detector_distance_ready) )
        groupbox_title = ""
        detector_distance = HWR.beamline.detector.distance
        if detector_distance is None:
            detector_distance_ready = False
        elif detector_distance_ready is None:
            detector_distance_ready = detector_distance.is_ready()
        #logging.getLogger("HWR").debug("detector_distance_ready = %s" % detector_distance_ready)
        #logging.getLogger("HWR").debug("detector_distanceget_state() = %s" % detector_distance.get_state())
        if detector_distance_ready:
            self.get_detector_distance_limits()
            curr_detector_distance = detector_distance.get_value()
            self.detector_distance_changed(curr_detector_distance)
            self.detector_distance_state_changed(detector_distance.get_state())
            if self.units_combobox.currentText() == "mm":
                groupbox_title = "Detector distance"
                self.new_value_validator.setRange(
                    self.detector_distance_limits[0],
                    self.detector_distance_limits[1],
                    2,
                )
        else:
            self.detector_distance_state_changed(None)

         

        if HWR.beamline.resolution is None:
            resolution_ready = False
        elif resolution_ready is None:
            resolution_ready = HWR.beamline.resolution.is_ready()
        #logging.getLogger("HWR").debug("resolution_ready = %s" % resolution_ready)
        #logging.getLogger("HWR").debug("HWR.beamline.resolution.get_state() = %s" % HWR.beamline.resolution.get_state())
        if resolution_ready:
            self.get_resolution_limits()
            curr_resolution = HWR.beamline.resolution.get_value()
            self.resolution_value_changed(curr_resolution)
            self.resolution_state_changed(HWR.beamline.resolution.get_state())
            if self.units_combobox.currentText() != "mm":
                groupbox_title = "Resolution"
                self.new_value_validator.setRange(
                    self.resolution_limits[0], self.resolution_limits[1], 3
                )
        else:
            self.resolution_state_changed(None)

        self.setEnabled(self.door_interlocked)
        self.new_value_ledit.setEnabled(resolution_ready and detector_distance_ready and self.door_interlocked)
        if not self.door_interlocked:
            groupbox_title += " (door is unlocked)"
        self.group_box.setTitle(groupbox_title)
        self.create_tool_tip()

    def detector_distance_state_changed(self, state):
        if state is None:
            return

        detector_distance = HWR.beamline.detector.distance
        color = ResolutionBrick.STATE_COLORS[state.value[1]]
        unit = self.units_combobox.currentText()

        if state == detector_distance.STATES.FAULT:
            self.setEnabled(False)
            return

        if unit == "mm":
            if state == detector_distance.STATES.READY:
                self.new_value_ledit.blockSignals(True)
                self.new_value_ledit.setText("")
                self.new_value_ledit.blockSignals(False)
                self.new_value_ledit.setEnabled(True)
            else:
                self.new_value_ledit.setEnabled(False)
            if state == detector_distance.STATES.BUSY:
                # or \
                # state == detector_distance.motor_states.MOVESTARTED:
                self.stop_button.setEnabled(True)
            else:
                self.stop_button.setEnabled(False)

            colors.set_widget_color(self.new_value_ledit, color)

