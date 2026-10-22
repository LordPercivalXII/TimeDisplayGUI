# ======================================================================================================================
# TimeDisplay
#
# An application that displays time in a window.
#
# Author: TwelfthDoctor1 [TD1]
# License: NIL/TBD~, Likely MIT
# ======================================================================================================================
# Module Importation
import argparse
import ctypes
import os
import sys
from pathlib import Path
from TimeDisplayLib.TimeDisplayHandler import run_TimeDisplay
from UtilLib.ConfigJSON import ConfigJSON, setDebugState_Config
from UtilLib.ConfigTemplate import CONFIG_DEFAULT, CONFIG_NAME
from UtilLib.Logging import setup_logger
# ======================================================================================================================
# ARGUMENT PARSER
parser = argparse.ArgumentParser(
    description="TimeDisplay - Displays the current time.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

# PARSER FLAGS
parser.add_argument(
    "--mini-ui",
    help="Force the use of Mini-UI whilst ignoring useMiniUI config value",
    action="store_true",
    default=False,
    required=False,
    dest="mini_ui"
)
parser.add_argument(
    "--reg-ui",
    help="Force the use of Reg-UI whilst ignoring useMiniUI config value",
    action="store_true",
    default=False,
    required=False,
    dest="reg_ui"
)
parser.add_argument(
    "--debug-config", "--d-c",
    help="Enable Config debugging by redirecting config file path to exec location rather than ~/",
    action="store_true",
    default=False,
    required=False
)
# parser.add_argument(
#     "--debug-log", "--d-l",
#     help="Enable debugging by enabling log file creation",
#     action="store_true",
#     default=False,
#     required=False
# )
# parser.add_argument(
#     "--debug-mlog", "--d-m",
#     help="Enable MasterLogger for debugging in console",
#     action="store_true",
#     default=False,
#     required=False
# )

cmd_args = parser.parse_args(sys.argv[1:])
# ======================================================================================================================
# DEBUG SETTINGS
#
# Setting to configure Filepath for Config, use of Logging for Debugging.
# Files will be saved in the ~ Directory (ref. User Directory)
DEBUG_CONFIG = False or cmd_args.debug_config

setDebugState_Config(DEBUG_CONFIG, Path(os.path.expanduser("~")).resolve())
# ======================================================================================================================
# Init Settings
# Init Main Logger
setup_logger("TimeDisplay", is_root=True, mode="w")

# Initialise the Config File for checks
# Should it does not exist, a new file will be created.
config = ConfigJSON(CONFIG_NAME)
config.generate_json(CONFIG_DEFAULT)
# ======================================================================================================================
# Windows/Linux Set App ID for Icons to be rendered accordingly
if sys.platform == "win32":
    app_id = "lpxii.timedisplay.v1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
# Linux - Set to XWayland for certain features to work
if sys.platform != "win32" and sys.platform != "darwin":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
# ======================================================================================================================
# Run GUI
if cmd_args.mini_ui:
    run_TimeDisplay(config, True)
elif cmd_args.reg_ui:
    run_TimeDisplay(config, False)
else:
    run_TimeDisplay(config)
# ======================================================================================================================

