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
from mxcubeqt.bricks.tree_brick import TreeBrick
from mxcubeqt.utils import qt_import
from mxcubecore import HardwareRepository as HWR
import os


__credits__ = ["ALBA"]
__license__ = "LGPLv3+"
__category__ = "General"

###
### Pick Button
###
class AlbaTreeBrick(TreeBrick):

    def __init__(self, *args):
        TreeBrick.__init__(self, *args)
        self.logger = logging.getLogger("HWR")
        self.logger.debug("AlbaTreeBrick.__init__()")
        
        self.pick_button = qt_import.QPushButton('Mount & Pick')
        self.ln2shower_hwobj = self.get_hardware_object("/ln2shower")

        #Add the button to the layout created in tree_brick.TreeBrick,
        #below ISPyB button
        #self.sample_changer_widget.gridLayout_2.addWidget(self.pick_button, 3, 3)
        self.logger.debug( self.pick_button.text() )
        
        # Slots -----------------------------------------------------------------
        self.connect(HWR.beamline.lims, "ispyb_sync_successful", self.enable_pick)
        self.sample_changer_widget.centring_cbox.setCurrentIndex(2)
        self.dc_tree_widget.set_centring_method(2)
        
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
        self.connect(
            HWR.beamline.sample_view, "centringInProgress", self.centring_status_changed
        )
        self.connect(
            HWR.beamline.sample_view, "centringSuccessful", self.centring_successful
        )

        if self.ln2shower_hwobj is not None:
            self.connect(
                self.ln2shower_hwobj, "ln2showerIsPumpingChanged", self.ln2shower_is_pumping_changed
            )


    def pick(self):
        if HWR.beamline.sample_changer is not None:
            pass
            if not items[0].get_model().free_pin_mode:
                sample_on_load_tool = HWR.sample_changer._chnLidSampleOnTool.get_value()
                if sample_on_load_tool is not None: # sample on tool, next to be loaded comes after tool
                    next_load_sample = HWR.lims.next_sample( sample_on_load_tool )
                else: # no sample on tool: sample needs to be loaded, followed by a pick.
                    next_load_sample = HWR.lims.next_sample( loaded_sample )
                next_pick_sample = HWR.lims.next_sample( next_load_sample ) # should return None is no available next sample
                HWR.beamline.sample_changer.set_next_pick_sample(next_pick_sample)
                self.dc_tree_widget.mount_sample( next_load_sample )

    def enable_pick(self):
        self.pick_button.setEnabled(True)

    def disable_pick(self):
        self.pick_button.setEnabled(False)

    @qt_import.pyqtSlot(bool)
    def logged_in(self, logged_in):
        if not logged_in:
            self.disable_pick()
        TreeBrick.logged_in(self, logged_in)


    # def updateBeam(self,force=False):
    #     if self["displayBeam"]:
    #           if not self.minidiff.isReady(): time.sleep(0.2)
    #           beam_x = self.minidiff.getBeamPosX()
    #           beam_y = self.minidiff.getBeamPosY()
    #           try:
    #              self.__rectangularBeam.set_xMid_yMid(beam_x,beam_y)
    #           except AttributeError:
    #              pass
    #           try:
    #             self.__beam.move(beam_x, beam_y)
    #             try:
    #                 # TODO FIXME ERROR: get_beam_info is a function - this cannot be right
    #               get_beam_info = self.minidiff.getBeamInfo #getCommandObject("getBeamInfo")
    #               if force or get_beam_info: #.isSpecReady():
    #                   self._updateBeam({"size_x":0.045, "size_y":0.025, "shape": "rectangular"})
    #             except:
    #               logging.getLogger().exception("Could not get beam size: cannot display beam")
    #               self.__beam.hide()
    #           except AttributeError:
    #             pass

    def collect_started(self, owner, num_oscillations):
        self.dc_tree_widget.sample_tree_widget.setEnabled(False)
        self.sample_changer_widget.setEnabled(False)

    def collect_finished(self, owner, state, message, *args):
        self.dc_tree_widget.sample_tree_widget.setEnabled(True)
        self.sample_changer_widget.setEnabled(True)
        
    def collect_failed(self, owner, state, message, *args):
        self.dc_tree_widget.sample_tree_widget.setEnabled(True)
        self.sample_changer_widget.setEnabled(True)
 
    def centring_status_changed(self, centring_status_bool):
        self.setEnabled(not centring_status_bool)
        self.dc_tree_widget.setEnabled(not centring_status_bool)
        
    def centring_successful(self, method_name, centring_status_dict):
        self.centring_status_changed(False) # False means not centering

    def ln2shower_is_pumping_changed( self, is_pumping_bool ):
        self.setEnabled( not is_pumping_bool )
