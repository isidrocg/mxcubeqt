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

from mxcubeqt.utils import qt_import, colors
from mxcubeqt.base_components import BaseWidget

from mxcubecore import HardwareRepository as HWR

__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "General"
__author__ = "Roeland Boer"


class AlbaCryostreamBrick(BaseWidget):

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)
        
        # Properties        
        self.add_property("mnemonic", "string", "")

        # Hardware objects ----------------------------------------------------
        self.cryostream_hwo = None
        self.state = None

        # Graphic elements ----------------------------------------------------
        self.qtlabel_gas_temp_label = qt_import.QLabel('Cryostream temp')
        self.qtlabel_gas_temp_value = qt_import.QLineEdit('None') # Has to be line edit for set_widget_color to work
        self.qtlabel_gas_temp_value.setAlignment(qt_import.Qt.AlignCenter)
        self.qtlabel_gas_temp_value.setReadOnly(True)

        self.gastemp_box = qt_import.QGroupBox()
        self.gastemp_layout = qt_import.QHBoxLayout( self.gastemp_box )
        self.gastemp_box.setTitle("Cryostream parameters")
        self.gastemp_layout.addWidget(self.qtlabel_gas_temp_label)
        self.gastemp_layout.addWidget(self.qtlabel_gas_temp_value)
    

        qt_import.QHBoxLayout(self)

        self.layout().addWidget(self.gastemp_box)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.MinimumExpanding
        )

    def property_changed(self, property_name, old_value, new_value):
        logging.getLogger("HWR").debug("Cryostream property changed property name %s new_value %s" % ( property_name, new_value) )
        if property_name == "mnemonic":
            if self.cryostream_hwo is not None:
                self.disconnect(
                    self.cryostream_hwo,
                    qt_import.SIGNAL("stateChanged"),
                    self.cryostream_state_changed,
                )
                self.disconnect(
                    self.cryostream_hwo,
                    qt_import.SIGNAL("gasTempChanged"),
                    self.cryostream_gas_temp_changed,
                )
            self.cryostream_hwo = self.get_hardware_object(new_value)
            if self.cryostream_hwo is not None:
                self.setEnabled(True)
                self.connect(
                    self.cryostream_hwo,
                    qt_import.SIGNAL("stateChanged"),
                    self.cryostream_state_changed,
                )
                self.connect(
                    self.cryostream_hwo,
                    qt_import.SIGNAL("gasTempChanged"),
                    self.cryostream_gas_temp_changed,
                )
                self.cryostream_hwo.force_emit_signals()
                logging.getLogger("HWR").info(
                    "User Name is: %s" % self.cryostream_hwo.userName()
                )
                self.gastemp_box.setTitle(self.cryostream_hwo.userName()) # method name will change, see TODO in Device in BaseHardwareObjects
            else:
                logging.getLogger("HWR").debug("Cryostream cant connect because the hardware object is None")
                self.setEnabled(False)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)


    def cryostream_state_changed(self, state):
        if state != None: self.state = state

    def cryostream_gas_temp_changed(self, value):
        #logging.getLogger("HWR").debug("Cryostream gas temperature update")
        if value != None:
            self.qtlabel_gas_temp_value.setText( str(value) )
            if value < 110: # in Kelvin
                colors.set_widget_color(self.qtlabel_gas_temp_value, colors.LIGHT_GREEN, qt_import.QPalette.Base)
                #self.qtlabel_gas_temp_value.setStyleSheet("background-color: lightgreen")
            if value >= 110: # in Kelvin
                colors.set_widget_color(self.qtlabel_gas_temp_value, colors.LIGHT_YELLOW, qt_import.QPalette.Base)
                #self.qtlabel_gas_temp_value.setStyleSheet("background-color: yellow")
            if value >= 150: # in Kelvin
                colors.set_widget_color(self.qtlabel_gas_temp_value, colors.LIGHT_RED, qt_import.QPalette.Base)
                #self.qtlabel_gas_temp_value.setStyleSheet("background-color: red")
