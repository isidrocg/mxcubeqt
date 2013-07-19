"""
Containes the classes: QueueuEntryContainer, BaseQueueEntry, DummyQueueEntry,
TaskGroupQueueEntry, SampleQueueEntry, SampleCentringQueueEntry,
DataCollectionQueueEntry, CharacterisationQueueEntry, EnergyScanQueueEntry.

All queue entries inherits the baseclass BaseQueueEntry which inturn inherits
QueueEntryContainer. This makes it possible to arrange and execute queue
entries in a hierarchical maner.

The rest of the classes: DummyQueueEntry, TaskGroupQueueEntry, SampleQueueEntry,
SampleCentringQueueEntry, DataCollectionQueueEntry, CharacterisationQueueEntry,
EnergyScanQueueEntry are concrete implementations of tasks.
"""

import gevent
import logging
import time
import queue_model_objects_v1 as queue_model_objects
import copy
import pprint
import os
import ShapeHistory as shape_history

import edna_test_data
from XSDataMXCuBEv1_3 import XSDataInputMXCuBE

from queue_model_objects_v1 import COLLECTION_ORIGIN
from queue_model_objects_v1 import STRATEGY_COMPLEXITY
from queue_model_objects_v1 import EXPERIMENT_TYPE
from queue_model_objects_v1 import STRATEGY_OPTION
from queue_model_objects_v1 import COLLECTION_ORIGIN_STR

from BlissFramework.Utils import widget_colors

__author__ = "Marcus Oskarsson"
__copyright__ = "Copyright 2012, ESRF"
__credits__ = ["My great coleagues", "The MxCuBE colaboration"]

__version__ = "0.1"
__maintainer__ = "Marcus Oskarsson"
__email__ = "marcus.oscarsson@esrf.fr"
__status__ = "Beta"


class QueueEntryContainer(object):
    """
    A QueueEntryContainer has a list of queue entries, classes inheriting
    BaseQueueEntry, and a QueueController object. The QueueControllerObject
    controls/handles the execution of the queue entries.
    """
    def __init__(self):
        object.__init__(self)
        self._queue_entry_list = []
        self._queue_controller = None
        self._parent_container = None


    def enqueue(self, queue_entry, queue_controller = None):
        # A queue entry container has a QueueController object
        # which controls the execution of the tasks in the
        # container. The container is set to be its own controller
        # if none is given.
        if queue_controller:
            queue_entry.set_queue_controller(queue_controller)
        else:
            queue_entry.set_queue_controller(self)

        queue_entry.set_container(self)
        self._queue_entry_list.append(queue_entry)
        #logging.getLogger('queue_exec').info('Enqueue called with: ' + \
        #                                     str(queue_entry))
        #logging.getLogger('queue_exec').info('Queue is :' + \
        #                                     str(queue_entry.\
        #                                         get_queue_controller()))


    def dequeue(self, queue_entry):
        """
        Dequeues the QueueEntry <queue_entry> and returns the
        dequeued entry.

        Throws ValueError if the queue_entry is not in the queue.

        :param queue_entry: The queue entry to dequeue/remove.
        :type queue_entry: QueueEntry

        :returns: The dequeued entry.
        :rtype: QueueEntry
        """
        result = None
        index = None
        queue_entry.set_queue_controller(None)
        queue_entry.set_container(None)

        try:
            index = self._queue_entry_list.index(queue_entry)
        except ValueError:
            raise

        if index is not None:
            result =  self._queue_entry_list.pop(index)

        logging.getLogger('queue_exec').info('dequeue called with: ' + \
                                             str(queue_entry))
        logging.getLogger('queue_exec').info('Queue is :' + \
                                             str(self.get_queue_controller()))
            
        return result


    def swap(self, queue_entry_a, queue_entry_b):
        """
        Swaps places between the two queue entries <queue_entry_a> and
        <queue_entry_b>.

        Throws a ValueError if one of the entries does not exist in the
        queue.

        :param queue_entry: Queue entry to swap
        :type queue_entry: QueueEntry

        :param queue_entry: Queue entry to swap
        :type queue_entry: QueueEntry
        """
        index_a = None
        index_b = None
        
        try:
            index_a = self._queue_entry_list.index(queue_entry_a)
        except ValueError:
            raise

        try:
            index_b = self._queue_entry_list.index(queue_entry_b)
        except ValueError:
            raise

        if (index_a is not None) and (index_b is not None):
            temp = self._queue_entry_list[index_a]
            self._queue_entry_list[index_a] = self._queue_entry_list[index_b]
            self._queue_entry_list[index_b] = temp


        logging.getLogger('queue_exec').info('swap called with: ' + \
                                             str(queue_entry_a) + ', ' + \
                                             str(queue_entry_b))
        logging.getLogger('queue_exec').info('Queue is :' + \
                                             str(self.get_queue_controller()))


    def set_queue_controller(self, queue_controller):
        """
        Sets the queue controller, the object that controls execution
        of this QueueEntryContainer.

        :param queue_controller: The queue controller object.
        :type queue_controller: QueueController
        """
        self._queue_controller = queue_controller


    def get_queue_controller(self):
        """
        :returns: The queue controller
        :type queue_controller: QueueController
        """
        return self._queue_controller


    def set_container(self, queue_entry_container):
        """
        Sets the parent queue entry to <queue_entry_container>

        :param queue_entry_container:
        :type queue_entry_container: QueueEntryContainer
        """
        
        self._parent_container = queue_entry_container


    def get_container(self):
        """
        :returns: The parent QueueEntryContainer.
        :rtype: QueueEntryContainer
        """
        return self._parent_container


class BaseQueueEntry(QueueEntryContainer):
    """
    Base class for queue entry objects. Defines the overall
    interface and behaviour for a queue entry.
    """
    
    def __init__(self, view = None, data_model = None,
                 view_set_queue_entry = True):
        QueueEntryContainer.__init__(self)
        self._data_model = None
        self._view = None
        self.set_data_model(data_model)
        self.set_view(view, view_set_queue_entry)
        self._checked_for_exec = False
        self.beamline_setup = None


    def enqueue(self, queue_entry):
        """
        Method inherited from QueueEntryContainer, a derived class
        should newer need to override this method.
        """
        QueueEntryContainer.\
            enqueue(self, queue_entry, self.get_queue_controller())


    def set_data_model(self, data_model):
        """
        Sets the model node of this queue entry to <data_model>

        :param data_model: The data model node.
        :type data_model: TaskNode        
        """
        self._data_model = data_model


    def get_data_model(self):
        """
        :returns: The data model of this queue entry.
        :rtype: TaskNode
        """
        return self._data_model


    def set_view(self, view, view_set_queue_entry = True):
        """
        Sets the view of this queue entry to <view>. Makes the
        correspodning bi-directional connection if view_set_queue_entry
        is set to True. Which is normaly case, it can be usefull with
        'uni-directional' connection in some rare cases.

        :param view: The view to associate with this entry
        :type view: ViewItem

        :param view_set_queue_entry: Bi- or uni-directional connection to view.
        :type view_set_queue_entry: bool
        """
        if view:
            self._view = view

            if view_set_queue_entry:
                view.set_queue_entry(self)


    def get_view(self):
        """
        :returns the view:
        :rtype: ViewItem
        """
        return self._view


    def is_enabled(self):
        """
        :returns: True if this item is enabled.
        :rtype: bool
        """
        return self._checked_for_exec


    def set_enabled(self, state):
        """
        Enables or disables this entry, controls wether this item
        should be executed (enabled) or not (disabled)

        :param state: Enabled if state is True otherwise disabled.
        :type state: bool
        """
        self._checked_for_exec = state


    def execute(self):
        """
        Execute method, should be overriden my subclasses, defines
        the main body of the procedure to be performed when the entry
        is executed.

        The default executer calls excute on all child entries after this
        method but before post_execute.     
        """
        logging.getLogger('queue_exec').\
            info('Calling execute on: ' + str(self))
    

    def pre_execute(self):
        """
        Procedure to be done before execute.
        """
        logging.getLogger('queue_exec').\
            info('Calling pre_execute on: ' + str(self))
        self.beamline_setup = self.get_queue_controller().\
                              getObjectByRole("beamline_setup")


    def post_execute(self):
        """
        Procedure to be done after execute, and execute of all children of
        this entry.
        """
        logging.getLogger('queue_exec').\
            info('Calling post_execute on: ' + str(self))
        self.get_view().setBackgroundColor(widget_colors.LIGHT_GREEN)
        self.get_view().setHighlighted(True)
        self.get_view().setOn(False)


    def stop(self):
        """
        Stops the execution of this entry, should free external resources,
        cancel all pending processes and so on.
        """
        self.get_view().setText(1, 'Stopped')
        logging.getLogger('queue_exec').\
            info('Calling stop on: ' + str(self))


    def handle_exception(self, ex):
        if self.get_view():
            self.get_view().setBackgroundColor(widget_colors.LIGHT_RED)


    def __str__(self):
        s = '<%s object at %s> [' % (
            self.__class__.__name__,
            hex(id(self))
            )

        for entry in self._queue_entry_list:
            s += str(entry)

        return s + ']'


class DummyQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None):
        BaseQueueEntry.__init__(self, view, data_model)


    def execute(self):
        BaseQueueEntry.execute(self)
        self.get_view().setText(1,'Sleeping 5 s')
        time.sleep(5)


    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)


    def post_execute(self):
        BaseQueueEntry.post_execute(self)


class TaskGroupQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None):
        BaseQueueEntry.__init__(self, view, data_model)
        self.lims_client_hwobj = None
        self._lims_group_id = 0
        self.session_hwobj = None

    def execute(self):
        BaseQueueEntry.execute(self)
        group_data = {'sessionId': self.session_hwobj.session_id}
        self.get_data_model().lims_group_id = self.lims_client_hwobj.\
                                              _store_data_collection_group(group_data)


    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)
        
        self.lims_client_hwobj = self.beamline_setup.lims_client_hwobj
        self.session_hwobj = self.beamline_setup.session_hwobj


    def post_execute(self):
        BaseQueueEntry.post_execute(self)
        

class SampleQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None):
        BaseQueueEntry.__init__(self, view, data_model)
        self.sample_changer_hwobj = None
        self.diffractometer_hwobj = None
        self.sample_centring_result = None


    def execute(self):
        BaseQueueEntry.execute(self)

        if not self._data_model.free_pin_mode:
            if self.sample_changer_hwobj is not None:
                loaded_sample_location = \
                    (self.sample_changer_hwobj.currentBasket,
                     self.sample_changer_hwobj.currentSample)
                location = self._data_model.location
                holder_length = self._data_model.holder_length

                logging.getLogger('queue_exec').\
                    info("Loading sample " +  self._data_model.loc_str)

                self._view.setText(1, "Loading sample")

                if loaded_sample_location != location:
                    self.shape_history.clear_all()
                    try:
                        self.sample_changer_hwobj.load_sample(holder_length,
                                                              sample_location = location,
                                                              wait = True)
                    except Exception as e:
                        self._view.setText(1, "Error loading")
                        logging.getLogger('user_level_log').\
                            error("Error loading sample, please check sample changer: " + e.message)
                        raise

                    #self._view.update_pin_icon()

                    if self.diffractometer_hwobj is not None:
                        try:
                            self.diffractometer_hwobj.connect("centringAccepted",
                                                                self.centring_done)
                            self.sample_centring_result = \
                                                        gevent.event.AsyncResult()

                            centring_method = \
                                self._view.listView().parent().centring_method

                            if centring_method == queue_model_objects.CENTRING_METHOD.MANUAL:
                                logging.getLogger("user_level_log").\
                                    warning("Manual centring used, please center sample")
                                self.diffractometer_hwobj.start3ClickCentring()
                            elif centring_method == queue_model_objects.CENTRING_METHOD.LOOP:
                                logging.getLogger("user_level_log").\
                                    info("Centring sample, please wait.")
                                self.diffractometer_hwobj.\
                                    startAutoCentring(loop_only = True)
                                logging.getLogger("user_level_log").\
                                    warning("Please save or reject the centring")
                            elif centring_method == queue_model_objects.CENTRING_METHOD.CRYSTAL:
                                logging.getLogger("user_level_log").\
                                    info("Centring sample, please wait.")
                                self.diffractometer_hwobj.startAutoCentring()
                                logging.getLogger("user_level_log").\
                                    warning("Please save or reject the centring")

                            self.sample_centring_result.get()
                        finally:
                            self.diffractometer_hwobj.disconnect("centringAccepted",
                                                                     self.centring_done)
                else:
                    logging.getLogger('queue_exec').\
                        info("Sample already mounted")
            else:
                logging.getLogger('queue_exec'). \
                    info("SampleQueuItemPolicy does not have any " +\
                         "sample changer hardware object, cannot mount sample")      


    def centring_done(self, success, centring_info):
        if success:
            self.sample_centring_result.set(centring_info)
        else:
            logging.getLogger("user_level_log").\
                warning("Loop centring failed or was cancelled, please continue manually.")


    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)

        self.sample_changer_hwobj = self.beamline_setup.sample_changer_hwobj
        self.diffractometer_hwobj = self.beamline_setup.diffractometer_hwobj
        self.shape_history = self.beamline_setup.shape_history_hwobj
        
            
    def post_execute(self):
        BaseQueueEntry.post_execute(self)


class SampleCentringQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None):
        BaseQueueEntry.__init__(self, view, data_model)
        self.sample_changer_hwobj = None
        self.diffractometer_hwobj = None
        self.shape_history = None


    def execute(self):
        BaseQueueEntry.execute(self)
        self.get_view().setText(1, 'Waiting for input')

        logging.getLogger("user_level_log").\
            warning("Please select a centred position.")
        self.get_queue_controller().pause(True)

        pos = None

        if len(self.shape_history.selected_shapes):
            pos = self.shape_history.selected_shapes.values()[0]
        elif len( self.shape_history.shapes):
            pos = self.shape_history.shapes.values()[0]
        else:
            logging.getLogger("user_level_log").\
                warning("No centred position selected, using current position.")

            pos_dict = self.diffractometer_hwobj.getPositions()
            cpos = queue_model_objects.CentredPosition(pos_dict)
            pos = shape_history.Point(None, cpos, None)

        if pos:
            self.get_data_model().get_task().acquisitions[0].\
                acquisition_parameters.centred_position = pos.get_centred_positions()[0]

            if pos.qub_point is not None:
                snapshot = self.shape_history.\
                           get_snapshot([pos.qub_point])
            else:
                snapshot = self.shape_history.\
                           get_snapshot([])

            self.get_data_model().get_task().acquisitions[0].\
                acquisition_parameters.centred_position.snapshot_image = snapshot

        self.get_view().setText(1, 'Input accepted')


    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)        
        self.sample_changer_hwobj = self.beamline_setup.sample_changer_hwobj
        self.diffractometer_hwobj = self.beamline_setup.diffractometer_hwobj
        self.shape_history = self.beamline_setup.shape_history_hwobj


    def post_execute(self):
        BaseQueueEntry.post_execute(self)

class DataCollectionQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None, 
                 view_set_queue_entry = True):

        BaseQueueEntry.__init__(self, view, data_model, view_set_queue_entry)

        self.collect_hwobj = None
        self.diffractometer_hwobj = None
        self.collect_task = None
        self.beamline_config_hwobj = None
        self.shape_history = None
        self.session = None


    def execute(self):
        BaseQueueEntry.execute(self)
        data_collection = self.get_data_model()
        
        if data_collection:
            self.collect_dc(data_collection, self.get_view())
        
        if self.shape_history:
            self.shape_history.get_drawing_event_handler().de_select_all()


    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)
        
        self.collect_hwobj = self.beamline_setup.collect_hwobj
        self.diffractometer_hwobj = self.beamline_setup.diffractometer_hwobj
        self.beamline_config_hwobj = self.beamline_setup.bl_config_hwobj
        self.shape_history = self.beamline_setup.shape_history_hwobj
        self.session = self.beamline_setup.session_hwobj
        
        qc = self.get_queue_controller()

        qc.connect(self.collect_hwobj, 'collectStarted', 
                   self.collect_started)
        qc.connect(self.collect_hwobj, 'collectNumberOfFrames', 
                   self.preparing_collect)
        qc.connect(self.collect_hwobj, 'collectOscillationStarted', 
                   self.collect_osc_started)
        qc.connect(self.collect_hwobj, 'collectOscillationFailed', 
                   self.collect_failed)
        qc.connect(self.collect_hwobj, 'collectOscillationFinished', 
                   self.collect_finished)
        qc.connect(self.collect_hwobj, 'collectImageTaken', 
                   self.image_taken)
        qc.connect(self.collect_hwobj, 'collectNumberOfFrames', 
                   self.collect_number_of_frames)


        if self.get_data_model().get_parent():
            self.get_data_model().lims_group_id = self.get_data_model().\
                                                  get_parent().lims_group_id
        

    def post_execute(self):
        BaseQueueEntry.post_execute(self)
        qc = self.get_queue_controller()

        qc.disconnect(self.collect_hwobj, 'collectStarted', 
                     self.collect_started)
        qc.disconnect(self.collect_hwobj, 'collectNumberOfFrames', 
                     self.preparing_collect)
        qc.disconnect(self.collect_hwobj, 'collectOscillationStarted', 
                     self.collect_osc_started)
        qc.disconnect(self.collect_hwobj, 'collectOscillationFailed', 
                     self.collect_failed)
        qc.disconnect(self.collect_hwobj, 'collectOscillationFinished', 
                     self.collect_finished)
        qc.disconnect(self.collect_hwobj, 'collectImageTaken', 
                     self.image_taken)
        qc.disconnect(self.collect_hwobj, 'collectNumberOfFrames', 
                     self.collect_number_of_frames)


    def collect_dc(self, data_collection, list_item):
        if self.collect_hwobj:
            acq = data_collection.acquisitions[0]
            path_template = data_collection.acquisitions[0].path_template
 
            param_list = queue_model_objects.\
                to_collect_dict(data_collection, self.session)

            try:
                if data_collection.experiment_type is queue_model_objects.EXPERIMENT_TYPE.HELICAL:
                    self.collect_hwobj.getChannelObject("helical").setValue(1)

                    start_cpos = data_collection.acquisitions[0].\
                                 acquisition_parameters.centred_position
                    end_cpos = data_collection.acquisitions[1].\
                               acquisition_parameters.centred_position

                    helical_oscil_pars = {'nb_pos': 2,
                                          'udiff': 0}

                    helical_oscil_pos = {'1': start_cpos.as_dict(), \
                                         '2': end_cpos.as_dict()}
                    
                    self.collect_hwobj.getChannelObject('helical_pos').\
                        setValue(helical_oscil_pos)

                    self.collect_hwobj.getChannelObject('helical_pars').\
                        setValue(helical_oscil_pars)     

                    logging.getLogger("user_level_log").\
                        info("Helical data collection with start position: " +\
                             str(pprint.pformat(start_cpos)) + \
                            " and end position: " + str(pprint.pformat(end_cpos)))
                    logging.getLogger("user_level_log").\
                        info("Moving to start position: " + str(pprint.pformat(start_cpos)))

                    list_item.setText(1, "Moving sample")

                    self.diffractometer_hwobj.moveToCentredPosition(start_cpos, wait = True)
                else:
                    self.collect_hwobj.getChannelObject("helical").setValue(0)                
                    cpos = data_collection.acquisitions[0].\
                           acquisition_parameters.centred_position
                    logging.getLogger('queue_exec').\
                        info("Moving to centred position: " + str(cpos))
                    logging.getLogger("user_level_log").\
                        info("Moving to centred position: " + str(cpos))

                    list_item.setText(1, "Moving sample")
                    self.diffractometer_hwobj.moveToCentredPosition(cpos, wait = True)

                logging.getLogger('queue_exec').\
                    info("Calling collect hw-object with: " + str(data_collection))
                logging.getLogger("user_level_log").\
                    info("Collecting: " + str(data_collection))

                self.collect_task = self.collect_hwobj.\
                                    collect(COLLECTION_ORIGIN_STR.MXCUBE, 
                                            param_list)
                self.collect_task.get()                
            except gevent.GreenletExit:
                logging.getLogger('queue_exec').\
                    exception("Collection stopped by user.")
                logging.getLogger("user_level_log").\
                    warning("Collection stopped by user.")
                list_item.setText(1, 'Stopped')
                raise
            except Exception as ex:
                logging.getLogger("user_level_log").\
                    error("Could not perform data collection, contact the local contact")
                logging.getLogger("user_level_log").\
                    error("Cause of error: " + ex.message)
                raise

            data_collection.set_collected(True)
            data_collection.previous_acquisition = copy.deepcopy(acq)
            data_collection.previous_acquisition.acquisition_parameters.\
                centred_position = acq.acquisition_parameters.centred_position

            # Increase the run-number for re-collect
            new_run_number = self.get_view().parent().get_model().\
                             get_next_number_for_name(path_template.get_prefix())

            data_collection.set_name(acq.path_template.get_prefix())
            data_collection.set_number(new_run_number)
            path_template.run_number = new_run_number
            list_item.setText(0, data_collection.get_name())
        else:
            logging.getLogger("user_level_log").\
                error("Could not call the data collection routine, check the beamline configuration")
            list_item.setText(1, 'Failed')


    def collect_started(self, owner, num_oscillations):
        pass


    def collect_number_of_frames(self, number_of_images = 0):
        pass
    
        
    def image_taken(self, image_number):
        num_images = str(self.get_data_model().acquisitions[0].\
                     acquisition_parameters.num_images)
        
        self.get_view().setText(1, str(image_number) + "/" + num_images)
   

    def preparing_collect(self, number_images=0):
        self.get_view().setText(1, "Collecting")


    def collect_failed(self, owner, state, message, *args):
        self.get_view().setText(1, "Failed")
        logging.getLogger("user_level_log").error(message.replace('\n', ' '))


    def collect_osc_started(self, owner, blsampleid, barcode, location,
                            collect_dict, osc_id):
        self.get_view().setText(1, "Preparing")
        

    def collect_finished(self, owner, state, message, *args):
        self.get_view().setText(1, "Collection done")
        logging.getLogger("user_level_log").info('Collection completed')


    def stop(self):
        BaseQueueEntry.stop(self)

        if self.collect_task:
            self.collect_task.kill(block = True)
        
        self.get_view().setText(1, 'Stopped')
        logging.getLogger('queue_exec').info('Calling stop on: ' + str(self))
        

class CharacterisationGroupQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None, 
                 view_set_queue_entry = True):
        BaseQueueEntry.__init__(self, view, data_model, view_set_queue_entry)


    def execute(self):
        BaseQueueEntry.execute(self)


    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)
        characterisation = self.get_data_model()
        reference_image_collection = characterisation.\
                                     reference_image_collection
        characterisation_parameters = characterisation.\
                                      characterisation_parameters

        reference_image_collection.lims_group_id = self.get_data_model().\
                                                   get_parent().lims_group_id
        
        # Enqueue the reference collection and the characterisation
        # routine.
        dc_qe = DataCollectionQueueEntry(self.get_view(),
                                         reference_image_collection,
                                         view_set_queue_entry = False)
        dc_qe.set_enabled(True)
        self.enqueue(dc_qe)

        characterisation_qe = CharacterisationQueueEntry(self.get_view(), characterisation,
                                                         view_set_queue_entry = False)
        characterisation_qe.set_enabled(True)
        self.enqueue(characterisation_qe)


    def post_execute(self):
        BaseQueueEntry.post_execute(self)


class CharacterisationQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None, 
                 view_set_queue_entry = True):

        BaseQueueEntry.__init__(self, view, data_model, view_set_queue_entry)
        self.data_analysis_hwobj = None
        self.diffractometer_hwobj = None
        self.beamline_config_hwobj = None
        self.queue_model_hwobj = None
        self.session_hwobj = None
        self.edna_result = None


    def execute(self):
        BaseQueueEntry.execute(self)
        
        self.get_view().setText(1, "Characterising")
        logging.getLogger("user_level_log").info("Characterising, please wait, can take up to three minutes.")
        characterisation = self.get_data_model()
        reference_image_collection = characterisation.reference_image_collection
        characterisation_parameters = characterisation.characterisation_parameters

        edna_xml_output = None

        if self.data_analysis_hwobj is not None:

            edna_input = self.data_analysis_hwobj.from_params(reference_image_collection,
                                                              characterisation_parameters)
            #edna_input = XSDataInputMXCuBE.parseString(edna_test_data.EDNA_TEST_DATA)
            
            self.edna_result = self.data_analysis_hwobj.characterise(edna_input)

        if self.edna_result:
            logging.getLogger("user_level_log").\
                info("Characterisation successful.")
          
            characterisation.html_report = self.data_analysis_hwobj.\
                                           get_html_report(self.edna_result)
            
            collection_plan = None

            try:
                collection_plan = self.edna_result.getCharacterisationResult().\
                                  getStrategyResult().getCollectionPlan()
            except:
                pass

            if collection_plan:
                dcg_model = characterisation.get_parent()

                char_dcg_name = dcg_model._name
                # Get only the name portion, and not the number.
                num = dcg_model._number

                sample_data_model = dcg_model.get_parent()

                new_dcg_name = 'Diffraction plan'
                new_dcg_num = dcg_model.get_parent().\
                              get_next_number_for_name(new_dcg_name)

                new_dcg_model = queue_model_objects.TaskGroup()
                new_dcg_model.set_enabled(False)
                new_dcg_model.set_name(new_dcg_name)
                new_dcg_model.set_number(new_dcg_num)
                self.queue_model_hwobj.add_child(sample_data_model, new_dcg_model)
                
                edna_collections = queue_model_objects.\
                                   dc_from_edna_output(self.edna_result,                   
                                                       reference_image_collection,
                                                       new_dcg_model,
                                                       sample_data_model,
                                                       self.session_hwobj)

                for edna_dc in edna_collections:
                    edna_dc.set_enabled(False)
                    self.queue_model_hwobj.add_child(new_dcg_model, edna_dc)

            else:  
                logging.getLogger('queue_exec').\
                    info('EDNA-Characterisation completed successfully but without collection plan.')
                logging.getLogger("user_level_log").\
                    warning("Characterisation completed successfully but without collection plan.")
                
            self.get_view().setText(1, "Done")
            
        else:
            self.get_view().setText(1, "Charact. Failed")

            if self.data_analysis_hwobj.is_running():
                logging.getLogger('queue_exec').\
                    error('EDNA-Characterisation, software is not responding.')
                logging.getLogger("user_level_log").\
                    error("Characterisation completed with error: data analysis server is not responding.")
            else:
                logging.getLogger('queue_exec').\
                    error('EDNA-Characterisation completed with a failure.')
                logging.getLogger("user_level_log").\
                    error("Characterisation completed with errors.")


        characterisation.set_executed(True)
        self.get_view().setHighlighted(True)

        
    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)
        self.get_view().setOn(True)
        self.get_view().setHighlighted(False)

        self.data_analysis_hwobj = self.beamline_setup.data_analysis_hwobj
        self.diffractometer_hwobj = self.beamline_setup.diffractometer_hwobj
        self.beamline_config_hwobj = self.beamline_setup.bl_config_hwobj
        self.queue_model_hwobj = self.get_view().listView().parent().queue_model_hwobj
        self.session_hwobj = self.beamline_setup.session_hwobj


    def post_execute(self):
        BaseQueueEntry.post_execute(self)
               

class EnergyScanQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None):
        BaseQueueEntry.__init__(self, view, data_model)
        self.energy_scan_hwobj = None
        self.energy_scan_task = None


    def execute(self):
        BaseQueueEntry.execute(self)
        
        if self.energy_scan_hwobj:
            energy_scan = self.get_data_model()
            self.get_view().setText(1, "Starting energy scan")

            self.energy_scan_task = \
                gevent.spawn(self.energy_scan_hwobj.startEnergyScan,
                             energy_scan.element_symbol,
                             energy_scan.edge,
                             energy_scan.path_template.directory,
                             energy_scan.path_template.get_prefix())

        result = self.energy_scan_task.get()
        self.energy_scan_hwobj.ready_event.wait()
        self.energy_scan_hwobj.ready_event.clear()


    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)        
        self.energy_scan_hwobj = self.beamline_setup.energy_hwobj

        qc = self.get_queue_controller()
        
        qc.connect(self.energy_scan_hwobj, 'scanStatusChanged', 
                   self.energy_scan_status_changed)
        
        qc.connect(self.energy_scan_hwobj, 'energyScanStarted', 
                   self.energy_scan_started)

        qc.connect(self.energy_scan_hwobj, 'energyScanFinished',
                   self.energy_scan_finished)

        qc.connect(self.energy_scan_hwobj, 'energyScanFailed',
                   self.energy_scan_failed)
                   

    def post_execute(self):
        BaseQueueEntry.post_execute(self)
        qc = self.get_queue_controller()

        qc.disconnect(self.energy_scan_hwobj, 'scanStatusChanged', 
                      self.energy_scan_status_changed)
        
        qc.disconnect(self.energy_scan_hwobj, 'energyScanStarted', 
                      self.energy_scan_started)
        
        qc.disconnect(self.energy_scan_hwobj, 'energyScanFinished',
                      self.energy_scan_finished)

        qc.disconnect(self.energy_scan_hwobj, 'energyScanFailed',
                      self.energy_scan_failed)
        

    def energy_scan_status_changed(self, msg):
        logging.getLogger("user_level_log").info(msg)


    def energy_scan_started(self):
        logging.getLogger("user_level_log").info("Energy scan started.")


    def energy_scan_finished(self, scan_info):
        energy_scan = self.get_data_model()
        scan_file_path = os.path.join(energy_scan.path_template.directory,
                                      energy_scan.path_template.get_prefix())

        scan_file_archive_path = os.path.join(energy_scan.path_template.\
                                              get_archive_directory(),
                                              energy_scan.path_template.get_prefix())

        (pk, fppPeak, fpPeak, ip, fppInfl, fpInfl,rm,
         chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title) = \
        self.energy_scan_hwobj.doChooch(None, energy_scan.element_symbol,
                                        energy_scan.edge,
                                        scan_file_archive_path,
                                        scan_file_path)


        scan_info = self.energy_scan_hwobj.scanInfo


        # This does not always apply, update model so
        # that its possible to access the sample directly from
        # the EnergyScan object.
        sample = self.get_view().parent().parent().get_model()
        sample.crystals[0].energy_scan_result.peak = pk
        sample.crystals[0].energy_scan_result.inflection = ip
        sample.crystals[0].energy_scan_result.first_remote = rm
        sample.crystals[0].second_remote = None

        energy_scan.result = sample.crystals[0].energy_scan_result
        
        logging.getLogger("user_level_log").\
            info("Energy scan, result: peak: %.4f, inflection: %.4f" %
                 (sample.crystals[0].energy_scan_result.peak,
                  sample.crystals[0].energy_scan_result.inflection))
        
        self.get_view().setText(1, "Done")


    def energy_scan_failed(self):
        logging.getLogger("user_level_log").info("Energy scan failed.")


class GenericWorkflowQueueEntry(BaseQueueEntry):
    def __init__(self, view = None, data_model = None):
        BaseQueueEntry.__init__(self, view, data_model)
        self.rpc_server_hwobj = None


    def execute(self):
        BaseQueueEntry.execute(self)
        self.get_queue_controller().emit('show_workflow_tab', (self.get_data_model(),))
        logging.getLogger("user_level_log").info("Executing workflow, waiting for user input.")


        #if self.rpc_server_hwobj.wokflow_in_progress:
        #    time.sleep(1)
        

    def pre_execute(self):
        BaseQueueEntry.pre_execute(self)
        self.rpc_server_hwobj = self.beamline_setup.rpc_server_hwobj

    def post_execute(self):
        BaseQueueEntry.post_execute(self)
        

MODEL_QUEUE_ENTRY_MAPPINGS = \
    {queue_model_objects.DataCollection: DataCollectionQueueEntry,
     queue_model_objects.Characterisation: CharacterisationGroupQueueEntry,
     queue_model_objects.EnergyScan: EnergyScanQueueEntry,
     queue_model_objects.SampleCentring: SampleCentringQueueEntry,
     queue_model_objects.Sample: SampleQueueEntry,
     queue_model_objects.TaskGroup: TaskGroupQueueEntry,
     queue_model_objects.Workflow: GenericWorkflowQueueEntry}