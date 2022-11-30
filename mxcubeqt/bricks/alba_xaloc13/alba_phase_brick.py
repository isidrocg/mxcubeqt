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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

import logging

from mxcubeqt.bricks.phase_brick import PhaseBrick                                                                                                                                                                                                         
from mxcubecore import HardwareRepository as HWR                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
__credits__ = ["MXCuBE collaboration"]                                                                                                                                                                                                                  
__license__ = "LGPLv3+"                                                                                                                                                                                                                                 
__category__ = "General"                                                                                                                                                                                                                                
      
class AlbaPhaseBrick(PhaseBrick):                                                                                                                                                                                                                           
    def __init__(self, *args):                                                                                                                                                                                                                          
        PhaseBrick.__init__(self, *args)     
        self.logger = logging.getLogger("HWR")
        #TODO: disable the brick when in collect or sample exchange processes

        if HWR.beamline.collect is not None:
            self.connect(
                HWR.beamline.collect, "collectStarted", self.collect_started
            )
            self.connect(
                HWR.beamline.collect, "collectOscillationFinished", self.collect_finished
            )
            self.connect(
                HWR.beamline.collect, "collectOscillationFailed", self.collect_failed
            )

        self.ln2shower_hwobj = self.get_hardware_object("/ln2shower")

        if self.ln2shower_hwobj is not None:
            self.connect(
                self.ln2shower_hwobj, "ln2showerIsPumpingChanged", self.ln2shower_is_pumping_changed
            )
            
        self.disconnect(
            HWR.beamline.diffractometer, "minidiffPhaseChanged", self.phase_changed
        )


        self.connect(
            HWR.beamline.supervisor, "phaseChanged", self.phase_changed
        )

    def enable_widget(self, *args):
        self.setEnabled(True)
        
    def disable_widget(self, *args):
        self.setEnabled(False)

    def collect_started(self, owner, num_oscillations):
        self.disable_widget()

    def collect_finished(self, owner, state, message, *args):
        self.enable_widget()
        
    def collect_failed(self, owner, state, message, *args):
        self.enable_widget()

    def ln2shower_is_pumping_changed( self, value ):
        self.logger.debug("Ln2 shower pumping changed, new_value: %s" % value )
        if value:
            self.disable_widget()
        else:
            self.enable_widget()
 
    def init_phase_list(self):
        self.phase_combobox.clear()
        phase_list = HWR.beamline.supervisor.get_phase_list()
        if len(phase_list) > 0:
            for phase in phase_list:
                self.phase_combobox.addItem(phase)
            self.setEnabled(True)
        else:
            self.setEnabled(False)

    def change_phase(self):
        if HWR.beamline.supervisor is not None:
            requested_phase = self.phase_combobox.currentText()
            if self["confirmPhaseChange"] and requested_phase == "BeamLocation":
                conf_msg = "Please remove any objects that might cause collision!\n" + \
                           "Continue"
                if (
                    qt_import.QMessageBox.warning(
                        None,
                        "Warning",
                        conf_msg,
                        qt_import.QMessageBox.Ok,
                        qt_import.QMessageBox.Cancel,
                   )
                   == qt_import.QMessageBox.Ok
                ):
                   HWR.beamline.supervisor.set_phase(str(requested_phase), timeout=None)
            else:
                HWR.beamline.supervisor.set_phase(str(requested_phase), timeout=None)

    def phase_changed(self, phase):
        if phase.lower() != "unknown" and self.phase_combobox.count() > 0:
            # index = self.phase_combobox.findText(phase)
            # self.phase_combobox.setEditText(phase)
            self.phase_combobox.setCurrentIndex(self.phase_combobox.findText(phase))
        else:
            self.phase_combobox.setCurrentIndex(-1)
