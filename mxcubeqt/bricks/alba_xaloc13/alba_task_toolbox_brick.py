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

from mxcubeqt.bricks.task_toolbox_brick import TaskToolboxBrick
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
        
