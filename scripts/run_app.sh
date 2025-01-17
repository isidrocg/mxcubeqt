#!/usr/bin/env bash

#  DESCRIPTION
#  --------------
#  Generic startup script for any mxcube application using Qt4
#

#  ENVIRONMENT
#  -----------
#  The following environment variables are needed
#
#    INSTITUTE - ALBA, SOLEIL,...
#    MXCUBE_ROOT - directory where mxcube is installed (git clone destination)
#    MXCUBE_XML_PATH - directory for the HwObj xml files
#    MXCUBE_GUI_PATH - directory for the gui file(s)
#    MXCUBE_LOG_PATH - directory for storing the logs
#
#  You can create a .mxcube.rc file under $HOME's user folder using the
#  mxcube.rc template.
#

#  EXAMPLE of .mxcube.rc file
#  --------------------------
#  |#!/usr/bin/env bash
#  |
#  | export INSTITUTE=ALBA
#  | export MXCUBE_ROOT=/MXCuBE/mxcube
#  | export MXCUBE_XML_PATH=$MXCUBE_ROOT/../HardwareObjects.xml
#  | export MXCUBE_GUI_PATH=$MXCUBE_ROOT/../guis
#  | export MXCUBE_LOG_PATH=$MXCUBE_ROOT/../log/
#  |
#  | # include other local exports here.
#  |
#

#  RUNNING MXCUBE
#  -----------------
#  Setup the environment variables properly.
#
#  To run mxcube2 (or any other application <app_name>)
#     1) Copy the GUI file to $MXCUBE_GUI_PATH as <app_name>.gui
#     2) Execute <app_name>
#
#  If no file matching the <app_name>.gui is found, the example mxcube gui is started.
#
##########################################################################

# Define MXCuBE defaults
MXCUBE_BRICKS_PATH=$MXCUBE_ROOT/gui/bricks # (This could be exported from python script)
MXCUBE_HWOBJS_PATH=$MXCUBE_ROOT/HardwareRepository/HardwareObjects # (This could be exported from python script)
MXCUBE_DEFAULT_GUI_FILE=$MXCUBE_ROOT/configuration/example_mxcube_gui.yml
MXCUBE_DEFAULT_XML_PATH=$MXCUBE_ROOT/HardwareRepository/configuration/mockup,$MXCUBE_ROOT/HardwareRepository/configuration/mockup/qt

export PYTHONPATH=$PYTHONPATH:$MXCUBE_ROOT
export PYTHONPATH=$PYTHONPATH:$MXCUBE_BRICKS_PATH
export PYTHONPATH=$PYTHONPATH:$MXCUBE_HWOBJS_PATH

if [ ! -z "$INSTITUTE" ]; then
    export PYTHONPATH=$PYTHONPATH:$MXCUBE_BRICKS_PATH/$INSTITUTE
    export PYTHONPATH=$PYTHONPATH:$MXCUBE_HWOBJS_PATH/$INSTITUTE
fi

if [ -z "$USER" ]; then
    USER=UNKWOWN
fi

GUI_FILE=$MXCUBE_ROOT/$APP_NAME.gui
# Load defaults if GUI file does not exists
if [ ! -f $GUI_FILE ]; then
    GUI_FILE=$MXCUBE_DEFAULT_GUI_FILE
    XML_PATH=$MXCUBE_DEFAULT_XML_PATH
else
    XML_PATH=$MXCUBE_XML_PATH
    GUI_FILE=$MXCUBE_GUI_PATH/$APP_NAME.gui
fi

echo "######################################################################"
echo " USER:        $USER"
echo " INSTITUTE:   $INSTITUTE"
echo " MXCUBE_ROOT: $MXCUBE_ROOT"
echo " GUI_FILE:    $GUI_FILE"
echo "######################################################################"

# Running the application
$MXCUBE_ROOT/scripts/mxcube_app.py --hardwareRepository=$XML_PATH \
			--bricksDir=$MXCUBE_BRICKS_PATH \
			--logFile=$MXCUBE_LOG_PATH/$APP_NAME-$USER.log \
			$GUI_FILE $* > $MXCUBE_LOG_PATH/$APP_NAME-$USER.out 2> $MXCUBE_LOGS_PATH/$APP_NAME-$USER.err
