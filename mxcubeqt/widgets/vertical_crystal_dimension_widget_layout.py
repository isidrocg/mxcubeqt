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


from mxcubeqt.utils import qt_import


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class VerticalCrystalDimensionWidgetLayout(qt_import.QWidget):
    def __init__(self, parent=None, name=None, fl=0):
        qt_import.QWidget.__init__(self, parent, qt_import.Qt.WindowFlags(fl))

        if not name:
            self.setObjectName("VerticalCrystalDimensionWidgetLayout")

        return

        VerticalCrystalDimensionWidgetLayoutLayout = qt_import.QVBoxLayout(
            self, 0, 6, "VerticalCrystalDimensionWidgetLayoutLayout"
        )

        self.gbox = qt_import.QGroupBox(self, "gbox")
        self.gbox.setSizePolicy(
            qt_import.QSizePolicy.MinimumExpanding, qt_import.QSizePolicy.MinimumExpanding
        )
        self.gbox.setChecked(0)
        self.gbox.setColumnLayout(0, qt_import.Qt.Vertical)
        self.gbox.layout().setSpacing(6)
        self.gbox.layout().setMargin(11)
        gboxLayout = qt_import.QHBoxLayout(self.gbox.layout())
        gboxLayout.setAlignment(qt_import.Qt.AlignTop)

        main_layout = qt_import.QVBoxLayout(None, 0, 15, "main_layout")

        space_group_layout = qt_import.QHBoxLayout(None, 0, 6, "space_group_layout")

        space_group_ledit_layout = qt_import.QHBoxLayout(None, 0, 6, "space_group_ledit_layout")

        self.space_group_label = qt_import.QLabel(self.gbox, "space_group_label")
        space_group_ledit_layout.addWidget(self.space_group_label)

        self.space_group_ledit = qt_import.QComboBox(0, self.gbox, "space_group_ledit")
        self.space_group_ledit.setMinimumSize(qt_import.QSize(100, 0))
        self.space_group_ledit.setMaximumSize(qt_import.QSize(100, 32767))
        space_group_ledit_layout.addWidget(self.space_group_ledit)
        space_group_layout.addLayout(space_group_ledit_layout)
        space_group_hspacer = qt_import.QSpacerItem(
            1, 20, qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Minimum
        )
        space_group_layout.addItem(space_group_hspacer)
        main_layout.addLayout(space_group_layout)

        vdim_layout = qt_import.QVBoxLayout(None, 0, 2, "vdim_layout")

        vdim_heading_layout = qt_import.QHBoxLayout(None, 0, 6, "vdim_heading_layout")

        self.dimension_label = qt_import.QLabel(self.gbox, "dimension_label")
        vdim_heading_layout.addWidget(self.dimension_label)
        vdim_heading_spacer = qt_import.QSpacerItem(
            1, 20, qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Minimum
        )
        vdim_heading_layout.addItem(vdim_heading_spacer)
        vdim_layout.addLayout(vdim_heading_layout)

        vdim_control_layout = qt_import.QHBoxLayout(None, 0, 0, "vdim_control_layout")

        vdim_ledit_hlayout = qt_import.QHBoxLayout(None, 0, 20, "vdim_ledit_hlayout")

        col_one_vdim_ledit_hlayout = qt_import.QHBoxLayout(
            None, 0, 6, "col_one_vdim_ledit_hlayout"
        )

        vlayout_min_vdim_label = qt_import.QVBoxLayout(None, 0, 6, "vlayout_min_vdim_label")

        self.min_vdim_label = qt_import.QLabel(self.gbox, "min_vdim_label")
        vlayout_min_vdim_label.addWidget(self.min_vdim_label)

        self.vdim_min_phi_label = qt_import.QLabel(self.gbox, "vdim_min_phi_label")
        vlayout_min_vdim_label.addWidget(self.vdim_min_phi_label)
        col_one_vdim_ledit_hlayout.addLayout(vlayout_min_vdim_label)

        vlayout_min_vdim_ledit = qt_import.QVBoxLayout(None, 0, 6, "vlayout_min_vdim_ledit")

        self.min_vdim_ledit = qt_import.QLineEdit(self.gbox, "min_vdim_ledit")
        self.min_vdim_ledit.setMinimumSize(qt_import.QSize(50, 0))
        self.min_vdim_ledit.setMaximumSize(qt_import.QSize(50, 32767))
        vlayout_min_vdim_ledit.addWidget(self.min_vdim_ledit)

        self.min_vphi_ledit = qt_import.QLineEdit(self.gbox, "min_vphi_ledit")
        self.min_vphi_ledit.setMinimumSize(qt_import.QSize(50, 0))
        self.min_vphi_ledit.setMaximumSize(qt_import.QSize(50, 32767))
        vlayout_min_vdim_ledit.addWidget(self.min_vphi_ledit)
        col_one_vdim_ledit_hlayout.addLayout(vlayout_min_vdim_ledit)
        vdim_ledit_hlayout.addLayout(col_one_vdim_ledit_hlayout)

        col_two_vdim_ledit_hlayout = qt_import.QHBoxLayout(
            None, 0, 6, "col_two_vdim_ledit_hlayout"
        )

        vlayout_two_vdim_hlayout = qt_import.QVBoxLayout(None, 0, 6, "vlayout_two_vdim_hlayout")

        self.max_vdim_label = qt_import.QLabel(self.gbox, "max_vdim_label")
        vlayout_two_vdim_hlayout.addWidget(self.max_vdim_label)

        self.max_vphi_label = qt_import.QLabel(self.gbox, "max_vphi_label")
        vlayout_two_vdim_hlayout.addWidget(self.max_vphi_label)
        col_two_vdim_ledit_hlayout.addLayout(vlayout_two_vdim_hlayout)

        vlayout_max_vdim_ledit = qt_import.QVBoxLayout(None, 0, 6, "vlayout_max_vdim_ledit")

        self.max_vdim_ledit = qt_import.QLineEdit(self.gbox, "max_vdim_ledit")
        self.max_vdim_ledit.setMinimumSize(qt_import.QSize(50, 0))
        self.max_vdim_ledit.setMaximumSize(qt_import.QSize(50, 32767))
        vlayout_max_vdim_ledit.addWidget(self.max_vdim_ledit)

        self.max_vphi_ledit = qt_import.QLineEdit(self.gbox, "max_vphi_ledit")
        self.max_vphi_ledit.setMinimumSize(qt_import.QSize(50, 0))
        self.max_vphi_ledit.setMaximumSize(qt_import.QSize(50, 32767))
        vlayout_max_vdim_ledit.addWidget(self.max_vphi_ledit)
        col_two_vdim_ledit_hlayout.addLayout(vlayout_max_vdim_ledit)
        vdim_ledit_hlayout.addLayout(col_two_vdim_ledit_hlayout)
        vdim_control_layout.addLayout(vdim_ledit_hlayout)
        vspacer = qt_import.QSpacerItem(1, 20, qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.Minimum)
        vdim_control_layout.addItem(vspacer)
        vdim_layout.addLayout(vdim_control_layout)
        main_layout.addLayout(vdim_layout)
        gboxLayout.addLayout(main_layout)
        VerticalCrystalDimensionWidgetLayoutLayout.addWidget(self.gbox)

        self.languageChange()

        self.resize(qt_import.QSize(307, 163).expandedTo(self.minimumSizeHint()))

    def languageChange(self):
        self.setCaption(self.__tr("VerticalCrystalDimensionWidget"))
        self.gbox.setTitle(self.__tr("Crystal"))
        self.space_group_label.setText(self.__tr("Space group:"))
        self.dimension_label.setText(self.__tr("Vertical crystal dimension (mm):"))
        self.min_vdim_label.setText(self.__tr("Min:"))
        self.vdim_min_phi_label.setText(
            self.__trUtf8("\xcf\x89\x20\x61\x74\x20\x6d\x69\x6e\x3a")
        )
        self.max_vdim_label.setText(self.__tr("Max:"))
        self.max_vphi_label.setText(
            self.__trUtf8("\xcf\x89\x20\x61\x74\x20\x6d\x61\x78\x3a")
        )

    def __tr(self, s, c=None):
        return qt_import.QApplication.translate("VerticalCrystalDimensionWidgetLayout", s, c)

    def __trUtf8(self, s, c=None):
        return qt_import.QApplication.translate(
            "VerticalCrystalDimensionWidgetLayout", s, c, qt_import.QApplication.UnicodeUTF8
        )
