#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging
from copy import deepcopy

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

import queue_model_objects_v1 as queue_model_objects 
import Qt4_queue_item
import Qt4_GraphicsManager as graphics_manager

from Qt4_create_task_base import CreateTaskBase
from widgets.Qt4_data_path_widget import DataPathWidget
from widgets.Qt4_acquisition_widget import AcquisitionWidget
from queue_model_enumerables_v1 import EXPERIMENT_TYPE
from queue_model_enumerables_v1 import COLLECTION_ORIGIN


class CreateAdvancedWidget(CreateTaskBase):
    """
    Descript. :
    """

    def __init__(self, parent = None,name = None, fl = 0):
        CreateTaskBase.__init__(self, parent, name, QtCore.Qt.WindowFlags(fl), 'Advanced')

        if not name:
            self.setObjectName("create_advanced_widget")

        # Hardware objects ----------------------------------------------------
 
        # Internal variables --------------------------------------------------
        self.init_models()
        self._advanced_methods = None
        self._grid_map = {}

        # Graphic elements ----------------------------------------------------
        self._advanced_methods_widget = uic.loadUi(os.path.join(\
            os.path.dirname(__file__), "ui_files/Qt4_advanced_methods_layout.ui"))

        self._acq_widget =  AcquisitionWidget(self, "acquisition_widget",
             layout='vertical', acq_params=self._acquisition_parameters,
             path_template=self._path_template)

        self._data_path_gbox = QtGui.QGroupBox('Data location', self)
        self._data_path_gbox.setObjectName('data_path_gbox')
        self._data_path_widget = DataPathWidget(self._data_path_gbox,
             'create_dc_path_widget', data_model = self._path_template,
             layout = 'vertical')

        # Layout --------------------------------------------------------------
        _data_path_gbox_vlayout = QtGui.QVBoxLayout(self._data_path_gbox)
        _data_path_gbox_vlayout.addWidget(self._data_path_widget)
        _data_path_gbox_vlayout.setSpacing(0)
        _data_path_gbox_vlayout.setContentsMargins(0,0,0,0)

        _main_vlayout = QtGui.QVBoxLayout(self) 
        _main_vlayout.addWidget(self._advanced_methods_widget)
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_gbox)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(2)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._data_path_widget.data_path_layout.prefix_ledit.textChanged.\
             connect(self._prefix_ledit_change)
        self._data_path_widget.data_path_layout.run_number_ledit.textChanged.\
             connect(self._run_number_ledit_change)
        self._data_path_widget.pathTemplateChangedSignal.connect(\
             self.handle_path_conflict)
        self._advanced_methods_widget.grid_listwidget.currentItemChanged.\
             connect(self.grid_listwidget_current_item_changed)

        # Other ---------------------------------------------------------------
        self._acq_widget.use_osc_start(False)
        self._acq_widget.use_kappa(False) 
        self._acq_widget.use_kappa_phi(False)
        self._acq_widget.acq_widget_layout.num_images_label.setEnabled(False)
        self._acq_widget.acq_widget_layout.num_images_ledit.setEnabled(False)

    def init_models(self):
        """
        Descript. :
        """
        CreateTaskBase.init_models(self)
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        if self._beamline_setup_hwobj is not None:
            has_shutter_less = self._beamline_setup_hwobj.\
                               detector_has_shutterless()
            self._acquisition_parameters.shutterless = has_shutter_less

            self._acquisition_parameters = self._beamline_setup_hwobj.\
                get_default_acquisition_parameters("default_advanced_values")
            if not self._advanced_methods:
                self._advanced_methods = self._beamline_setup_hwobj.get_advanced_methods()            
                for method in self._advanced_methods:
                    self._advanced_methods_widget.method_combo.addItem(method)
        else:
            self._acquisition_parameters = queue_model_objects.AcquisitionParameters()
            self._path_template = queue_model_objects.PathTemplate()

    def approve_creation(self):
        """
        Descript. :
        """
        result = CreateTaskBase.approve_creation(self)

        method_name = str(self._advanced_methods_widget.method_combo.\
                currentText()).title().replace(' ', '')
        if len(self._advanced_methods_widget.grid_listwidget.selectedItems()) == 0:
            logging.getLogger("user_level_log").error("No grid selected")
            result = False 

        return result
            
    def update_processing_parameters(self, crystal):
        """
        Descript. :
        """
        return

    def single_item_selection(self, tree_item):
        """
        Descript. :
        """
        CreateTaskBase.single_item_selection(self, tree_item)

        if isinstance(tree_item, Qt4_queue_item.SampleQueueItem):
            sample_model = tree_item.get_model()
            #self._processing_parameters = sample_model.processing_parameters
            #self._processing_widget.update_data_model(self._processing_parameters)
        elif isinstance(tree_item, Qt4_queue_item.AdvancedQueueItem):
            advanced = tree_item.get_model()
            if tree_item.get_model().is_executed():
                self.setDisabled(True)
            else:
                self.setDisabled(False)

            # sample_data_model = self.get_sample_item(tree_item).get_model()
            #self._acq_widget.disable_inverse_beam(True)

            print 1

            
            return
            self._path_template = advanced.get_path_template()
            self._data_path_widget.update_data_model(self._path_template)

            data_collection = advanced.reference_image_collection

            self._acquisition_parameters = data_collection.acquisitions[0].\
                                           acquisition_parameters
            self._acq_widget.update_data_model(self._acquisition_parameters,
                                               self._path_template)
            self.get_acquisition_widget().use_osc_start(True)
        else:
            self.setDisabled(True)

  
    def _create_task(self,  sample, shape):
        """
        Descript. :
        """
        data_collections = []
        shape = self.get_selected_grid()

        if isinstance(shape, graphics_manager.GraphicsItemGrid): 
            snapshot = self._graphics_manager_hwobj.get_snapshot(shape)
            grid_properties = shape.get_properties()

            acq = self._create_acq(sample)
            acq.acquisition_parameters.centred_position = shape.get_centred_position()
            acq.acquisition_parameters.mesh_range = shape.get_grid_range_mm()
            acq.acquisition_parameters.num_lines = grid_properties["num_lines"]
            acq.acquisition_parameters.num_images = grid_properties["num_lines"] * \
                                                    grid_properties["num_images_per_line"]

            processing_parameters = deepcopy(self._processing_parameters)

            dc = queue_model_objects.DataCollection([acq],
                                     sample.crystals[0],
                                     processing_parameters)

            dc.set_name(acq.path_template.get_prefix())
            dc.set_number(acq.path_template.run_number)
            dc.set_experiment_type(EXPERIMENT_TYPE.MESH)

            exp_type = self._advanced_methods_widget.method_combo.currentText()
            advanced = queue_model_objects.Advanced(exp_type, dc, 
                  shape, sample.crystals[0])

            data_collections.append(advanced)
            self._path_template.run_number += 1

        return data_collections            

    def shape_created(self, shape, shape_type):
        if shape_type == "Grid":
            self._advanced_methods_widget.grid_listwidget.addItem(shape.get_full_name())            
            new_item = self._advanced_methods_widget.grid_listwidget.item(\
                self._advanced_methods_widget.grid_listwidget.count() - 1)
            self._grid_map[shape] = new_item
            #new_item.setSelected(True)
            self._advanced_methods_widget.grid_listwidget.setCurrentItem(new_item)
            shape.setSelected(True)
            self.grid_listwidget_current_item_changed(new_item)
  
    def shape_deleted(self, shape, shape_type):
        if self._grid_map.get(shape):
            shape_index = self._advanced_methods_widget.grid_listwidget.\
                 indexFromItem(self._grid_map[shape])
            self._advanced_methods_widget.grid_listwidget.takeItem(shape_index.row())
            self._grid_map.pop(shape) 

    def grid_listwidget_current_item_changed(self, item):
        for grid, listwidget_item in self._grid_map.iteritems():
            if listwidget_item == item:
                grid_properties = grid.get_properties() 
                cell_count = grid_properties.get("num_lines") * \
                             grid_properties.get("num_images_per_line")
                self._acq_widget.acq_widget_layout.num_images_ledit.setText("%d" % cell_count)
                self._acq_widget.acq_widget_layout.first_image_ledit.\
                     setText("%d" % grid_properties.get("first_image_num"))
                centred_point = grid.get_centred_position()
                self._acq_widget.acq_widget_layout.osc_start_ledit.setText(\
                     "%.2f" % float(centred_point.phi))
                self._acq_widget.acq_widget_layout.kappa_ledit.setText(\
                     "%.2f" % float(centred_point.kappa))
                self._acq_widget.acq_widget_layout.kappa_phi_ledit.setText(\
                     "%.2f" % float(centred_point.kappa_phi))
                grid.setSelected(True) 
            else:
                grid.setSelected(False)

    def get_selected_grid(self):
        for grid, listwidget_item in self._grid_map.iteritems():
            if listwidget_item.isSelected():
                return grid 