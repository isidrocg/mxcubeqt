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

"""CreateStillScanWidget allows to create a ssx acquisition method"""

import copy

import api

from gui.utils import queue_item, QtImport
from gui.widgets.create_task_base import CreateTaskBase
from gui.widgets.acquisition_still_widget import AcquisitionStillWidget
from gui.widgets.data_path_widget import DataPathWidget
from gui.widgets.processing_widget import ProcessingWidget

from HardwareRepository.HardwareObjects import (
    queue_model_objects,
    queue_model_enumerables,
)


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


class CreateStillScanWidget(CreateTaskBase):
    def __init__(self, parent=None, name=None, flags=0):

        CreateTaskBase.__init__(
            self, parent, name, QtImport.Qt.WindowFlags(flags), "Still"
        )

        if not name:
            self.setObjectName("create_still_scan_widget")

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------
        self.init_models()

        # Graphic elements ----------------------------------------------------
        self._acq_widget = AcquisitionStillWidget(
            self,
            "acquisition_widget",
            layout="vertical",
            acq_params=self._acquisition_parameters,
            path_template=self._path_template,
        )

        self._data_path_widget = DataPathWidget(
            self,
            "create_dc_path_widget",
            data_model=self._path_template,
            layout="vertical",
        )

        self._processing_widget = ProcessingWidget(
            self, data_model=self._processing_parameters
        )

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self._acq_widget)
        _main_vlayout.addWidget(self._data_path_widget)
        _main_vlayout.addWidget(self._processing_widget)
        _main_vlayout.addStretch(0)
        _main_vlayout.setSpacing(6)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self._acq_widget.acqParametersChangedSignal.connect(
            self.acq_parameters_changed
        )
        self._data_path_widget.pathTemplateChangedSignal.connect(
            self.path_template_changed
        )
        self._processing_widget.enableProcessingSignal.connect(
            self._run_processing_toggled
        )

        # Other ---------------------------------------------------------------
        self._processing_widget.processing_widget.run_processing_parallel_cbox.setChecked(
            api.beamline_setup._get_run_processing_parallel()
        )

    def use_osc_start(self, status):
        """
        Enables osc start QLineEdit
        :param status: boolean
        :return:
        """
        return

    def update_exp_time_limits(self):
        """
        Updates exposure time limits
        :return:
        """
        return

    def init_models(self):
        """
        Inits data model
        :return: None
        """
        CreateTaskBase.init_models(self)
        self._processing_parameters = queue_model_objects.ProcessingParameters()

        has_shutter_less = api.beamline_setup.detector_has_shutterless()
        self._acquisition_parameters.shutterless = has_shutter_less

        self._acquisition_parameters = api.beamline_setup.get_default_acquisition_parameters(
            "default_acquisition_values"
        )
        self._acquisition_parameters.num_triggers = 1
        self._acquisition_parameters.num_images_per_trigger = 1

    def set_tunable_energy(self, state):
        """
        Sets tunable energy
        :param state: boolean
        :return: None
        """
        self._acq_widget.set_tunable_energy(state)

    def update_processing_parameters(self, crystal):
        """
        Updates processing parameters
        :param crystal: Crystal
        :return:
        """
        self._processing_parameters.space_group = crystal.space_group
        self._processing_parameters.cell_a = crystal.cell_a
        self._processing_parameters.cell_alpha = crystal.cell_alpha
        self._processing_parameters.cell_b = crystal.cell_b
        self._processing_parameters.cell_beta = crystal.cell_beta
        self._processing_parameters.cell_c = crystal.cell_c
        self._processing_parameters.cell_gamma = crystal.cell_gamma
        self._processing_widget.update_data_model(self._processing_parameters)

    def single_item_selection(self, tree_item):
        """
        Method called when a queue item in the tree is selected
        :param tree_item: queue_item
        :return: None
        """
        CreateTaskBase.single_item_selection(self, tree_item)

        if isinstance(tree_item, queue_item.SampleQueueItem):
            sample_model = tree_item.get_model()
            # self._processing_parameters = copy.deepcopy(self._processing_parameters)
            self._processing_parameters = sample_model.processing_parameters
            self._processing_widget.update_data_model(self._processing_parameters)
        elif isinstance(tree_item, queue_item.BasketQueueItem):
            self.setDisabled(False)
        elif isinstance(tree_item, queue_item.DataCollectionQueueItem):
            dc_model = tree_item.get_model()
            self._acq_widget.use_kappa(False)

            if not dc_model.is_helical():
                if dc_model.is_executed():
                    self.setDisabled(True)
                else:
                    self.setDisabled(False)

                sample_data_model = self.get_sample_item(tree_item).get_model()
                energy_scan_result = sample_data_model.crystals[0].energy_scan_result
                self._acq_widget.set_energies(energy_scan_result)

                # self._acq_widget.disable_inverse_beam(True)

                self._path_template = dc_model.get_path_template()
                self._data_path_widget.update_data_model(self._path_template)

                self._acquisition_parameters = dc_model.acquisitions[0].acquisition_parameters
                self._acq_widget.update_data_model(
                    self._acquisition_parameters, self._path_template
                )
                # self.get_acquisition_widget().use_osc_start(True)
                if len(dc_model.acquisitions) == 1:
                    self.select_shape_with_cpos(
                        self._acquisition_parameters.centred_position
                    )

                self._processing_parameters = dc_model.processing_parameters
                self._processing_widget.update_data_model(self._processing_parameters)
            else:
                self.setDisabled(True)
        else:
            self.setDisabled(True)

    def _create_task(self, sample, shape):
        """
        Creates a new Still scan task
        :param sample: sample node
        :param shape: centering point
        :return: Acquisition item
        """
        tasks = []

        cpos = queue_model_objects.CentredPosition()
        cpos.snapshot_image = api.graphics.get_scene_snapshot()

        tasks.extend(self.create_dc(sample, cpos=cpos))
        self._path_template.run_number += 1

        return tasks

    def create_dc(
        self,
        sample,
        run_number=None,
        start_image=None,
        num_images=None,
        osc_start=None,
        sc=None,
        cpos=None,
        inverse_beam=False,
    ):
        """
        Creates a new data collection item
        :param sample: Sample
        :param run_number: int
        :param start_image: int
        :param num_images: int
        :param osc_start: float
        :param sc:
        :param cpos: centered position
        :param inverse_beam: boolean
        :return:
        """
        tasks = []

        # Acquisition for start position
        acq = self._create_acq(sample)

        if run_number:
            acq.path_template.run_number = run_number

        if start_image:
            acq.acquisition_parameters.first_image = start_image
            acq.path_template.start_num = start_image

        if num_images:
            acq.acquisition_parameters.num_images = num_images
            acq.path_template.num_files = num_images

        if osc_start:
            acq.acquisition_parameters.osc_start = osc_start

        if inverse_beam:
            acq.acquisition_parameters.inverse_beam = False

        acq.acquisition_parameters.centred_position = cpos

        processing_parameters = copy.deepcopy(self._processing_parameters)
        data_collection = queue_model_objects.DataCollection(
            [acq], sample.crystals[0], processing_parameters
        )
        data_collection.set_name(acq.path_template.get_prefix())
        data_collection.set_number(acq.path_template.run_number)
        data_collection.experiment_type = queue_model_enumerables.EXPERIMENT_TYPE.OSC
        run_processing_after, run_processing_parallel = \
            self._processing_widget.get_processing_state()

        data_collection.run_processing_after = run_processing_after
        if run_processing_parallel:
            data_collection.run_processing_parallel = "Still"
        data_collection.set_requires_centring(False)

        tasks.append(data_collection)

        return tasks
