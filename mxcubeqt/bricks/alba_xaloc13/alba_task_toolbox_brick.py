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
# from mxcubeqt.bricks.task_toolbox_brick import TaskToolboxBrick
from mxcubeqt.bricks.alba_task_toolbox_brick import TaskToolboxBrick
from mxcubeqt.utils import colors, qt_import

from mxcubecore import HardwareRepository as HWR

__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "Sample changer"
__author__ = "Roeland Boer"

class AlbaTaskToolboxBrick(TaskToolboxBrick):
    def __init__(self, *args):
        TaskToolboxBrick.__init__(self, *args)
        self.logger = logging.getLogger("HWR.XalocLN2Shower")
        self.logger.debug( "AlbaTaskToolboxBrick.__init__()" )
         
        self.ln2shower_hwobj = self.get_hardware_object("/ln2shower")

        if HWR.beamline.sample_changer is not None:
            self.connect(
                HWR.beamline.sample_changer, "path_safeChanged", self.path_safe_changed
            )

        if self.ln2shower_hwobj is not None:
            self.connect(
                self.ln2shower_hwobj, "ln2showerIsPumpingChanged", self.ln2shower_is_pumping_changed
            )
            self.connect(
                self.ln2shower_hwobj, "ln2showerFault", self.ln2shower_fault_changed
            )

        self.serial_pump_hwobj = self.get_hardware_object("/serialpump")


        if self.serial_pump_hwobj is not None:
            self.setEnabled(True)
            #self.connect(self.serial_pump_hwobj, SIGNAL('valuesChanged'),
                            #self.set_value)

            # TODO Check why needs an initial update of parameters to show text 
            # on labels on startup
            self.connect(self.serial_pump_hwobj, 'flowChanged',
                            self.flow_update)
            self.connect(self.serial_pump_hwobj, 'pressureChanged',
                            self.pressure_update)
            self.connect(self.serial_pump_hwobj, 'pumpingChanged',
                            self.pump_state_update)
            # self.connect(self.serial_pump_hwobj, 'togglePump',
            #                 self.start_stop_pump)
            self.task_tool_box_widget.ssx_page.pump_start_button.clicked.connect(
                self.start_stop_pump
                )

            # TODO Add here action to set flow when finish editing required_flow
            self.task_tool_box_widget.ssx_page.required_flow.returnPressed.connect(
                self.set_flow
                )
            # self.new_value_ledit.textChanged.connect(self.input_field_changed)
  
            
            self.logger.info("serial_pump_hwobj connected")
            #self.serial_pump_hwobj.update_values(self.serial_pump_hwobj.flow)
        else:
            self.setEnabled(False)




    def ln2shower_is_pumping_changed(self, is_pumping_bool):
        self.logger.debug("alba_task_toolbox_brick ln2shower is pumping_changed, value %s " % is_pumping_bool)
        self.task_tool_box_widget.collect_now_button.setEnabled(not is_pumping_bool)

    def ln2shower_fault_changed(self, value):
        """
          value True means in fault
        """
        pass

    def path_safe_changed(self, path_is_safe):
        """
          value True means the path is safe
        """
        self.logger.debug("alba_task_toolbox_brick path_safe_changed, value %s " % path_is_safe)
        self.task_tool_box_widget.collect_now_button.setEnabled( path_is_safe )
        
    def flow_update(self, value):
            """
            Descript. :
            Args.     :
            Return.   : 
            """
            flow = value
            self.logger.info("flow_update: flow %s" % str(flow))
            txt = '??? ul/min' if flow is None else u'<b>%s</b> \u00B5l/min'% str(flow)
            self.task_tool_box_widget.ssx_page.flow_value_label.setText(txt)
            
    def pressure_update(self, value):
        
        pressure = value
        
        self.logger.info("pressure_update: pressure %s" % str(pressure))

        self.task_tool_box_widget.ssx_page.pump_pressure_value_label.setText('<b>%s</b> bar'% str(pressure))
        flow_control = self.task_tool_box_widget.ssx_page.flow_control_checkbox.isChecked()

        #Allow flow control, controlled by the checkbox value
        #Flow will be recomputed at each pressure change.
        if flow_control:
            self.serial_pump_hwobj.flow_control(pressure)
        
    def pump_state_update(self, value):
        #replace set_value by this function in signal connection of 
        #the pump state, then use self,value as arguments and the pumping = self.serial_pump_hwobj.getPumping()
        #may be replaced by value
        pumping = value
        self.logger.info("set_value pumping %s" % str(pumping))

        # self.state_text_value_label.setText(str(pumping))
        if pumping:
            self.task_tool_box_widget.ssx_page.pump_start_button.setText("Pause")
            self.task_tool_box_widget.ssx_page.state_text_value_label.setText('Pumping')
        elif not pumping:
            self.task_tool_box_widget.ssx_page.pump_start_button.setText("Start")
            self.task_tool_box_widget.ssx_page.state_text_value_label.setText('Paused')
        else:
            self.task_tool_box_widget.ssx_page.pump_start_button.setText("Error")
            self.task_tool_box_widget.ssx_page.state_text_value_label.setText('Error')

    def start_stop_pump(self, value):
        self.logger.info("Button pressed, toggling pump")
        self.serial_pump_hwobj.start_stop_pump()

    def set_flow(self):
        new_flow = self.task_tool_box_widget.ssx_page.required_flow.text()
        new_flow_ml_min = float(new_flow) / 1000
        self.logger.info("This will set pump flow to %s" % str(new_flow))

        if (
            self.task_tool_box_widget.ssx_page.requiredflow_validator.validate(
                new_flow, 0
                )[0] == qt_import.QValidator.Acceptable
            ):

            self.serial_pump_hwobj.channelflow.set_value(new_flow_ml_min)
            self.task_tool_box_widget.ssx_page.required_flow.setText("")
            # colors.set_widget_color(
            #     self.new_value_ledit, colors.LINE_EDIT_ACTIVE, qt_import.QPalette.Base
            # )

            
