import datetime
import os
import sys
from pathlib import Path
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QResizeEvent, QCloseEvent, QContextMenuEvent
from PyQt6.QtWidgets import QMainWindow, QApplication, QLayout
from Qt6UI.QtStyleSheet import QT_STYLESHEET_DARK, QT_STYLESHEET_LIGHT
from Qt6UI.TimeDisplayUI import Ui_TimeDisplay
from Qt6UI.TimeDisplayMiniUI import Ui_TimeDisplayMini
from TimeDisplayLib.FontHandler import FontWeight
from TimeDisplayLib.SettingsHandler import TimeDisplaySettings
from UtilLib.ConfigJSON import ConfigJSON, CONFIG_NAME

EXIT_CODE_REOPEN = 1001
SIZE_SAVE_DELAY_MS = 500  # Wait this long after the last resize event before writing the size to disk


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class TimeDisplayGUI(QMainWindow):
    def __init__(self, parent=None):
        super(TimeDisplayGUI, self).__init__(parent)
        self.ui = Ui_TimeDisplayMini()
        self.hide()  # Initial Hiding

        # Setup UI
        self.ui.setupUi(self)
        self.setWindowTitle("TimeDisplay")
        self._connectActions()

        # Config Data
        self.json = ConfigJSON(CONFIG_NAME)
        self.json.getConfigData()

        # DateTime Data
        self.dt = None

        # Run Settings
        self.initResize()
        self.centerWindow()
        self.updateSettingState()
        self.onFloatChange()
        self.onSwitchTheme()
        self.onUpdateWinVisibility()
        self.onUpdateWindowBar()

        # Menubar - macOS Disabling (FOR TEST ONLY)
        if sys.platform == "darwin":
            # Leave disabled, always use Native Menu Bar
            # self.ui.menubar.setNativeMenuBar(False)
            # self.setWindowFlag(Qt.WindowType.Window.MacWindowToolBarButtonHint, False)
            pass

        # Hotkey - Non macOS -> use Alt+S instead of CMD key
        if sys.platform != "darwin":
            self.ui.action_Settings.setShortcut("Alt+S")

        # Misc Testing Section
        self.ui.statusbar.setVisible(False)

        # Timer to Refresh UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.processTimeDisplay)
        self.timer.setInterval(self.json.return_specific_json("intervalRate"))
        self.timer.start()

        # Frameless Window Movement Position
        self.old_pos = self.pos()

        self.ui.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)

        self._applied_font_key = None
        self.refreshFonts()

    def _connectActions(self):
        self.ui.action_Settings.triggered.connect(self.openSettings)
        self.ui.action_Float_on_Top.triggered.connect(self.settingFloat)
        self.ui.actionUse_24_Hour_Format.triggered.connect(self.setting24Hr)
        self.ui.actionShow_Seconds.triggered.connect(self.settingSecs)
        self.ui.actionShow_Date.triggered.connect(self.settingDate)
        self.ui.actionShow_AM_PM.triggered.connect(self.settingHr12Notation)
        self.ui.action_Exit.triggered.connect(self.close)
        self.ui.actionDark_Mode.triggered.connect(self.settingDarkMode)
        self.ui.actionIncrease_Font.triggered.connect(self.settingIncreaseFont)
        self.ui.actionDecrease_Font.triggered.connect(self.settingDecreaseFont)
        self.ui.actionFrameless.triggered.connect(self.settingFramelessWindowBar)
        self.ui.actionUse_Native_Theme.triggered.connect(self.settingUseNativeTheme)
        self.ui.actionUse_Bold_Font.triggered.connect(self.settingUpdateUseBoldFont)

        # Register the menu's actions on the window itself. Qt only fires an action's shortcut while
        # a widget it belongs to is visible, so when the menu bar is hidden (frameless mode) every
        # shortcut used to stop working and the only way back was editing the JSON. (#4)
        self.addActions(self.ui.menuOptions.actions())

    def contextMenuEvent(self, a0: QContextMenuEvent):
        """Right-click anywhere on the clock to open the Options menu, even with the menu bar hidden."""
        self.ui.menuOptions.exec(a0.globalPos())
        a0.accept()

    def processTimeDisplay(self):
        self.getTime()
        self.updateFont()

    def getTime(self):
        self.dt = datetime.datetime.now()

        # Update Time
        if self.json.return_specific_json("is24Hr") is True:  # 24 Hr
            self.ui.Hour.setText(self.dt.strftime("%H"))
            self.ui.hr12Notation.setText("")

        else:  # 12 Hr
            self.ui.Hour.setText(self.dt.strftime("%I"))
            if self.json.return_specific_json("showHr12") is True:  # Show AM/PM
                self.ui.hr12Notation.setText(self.dt.strftime("%p"))

            else:
                self.ui.hr12Notation.setText("")

        self.ui.Mins.setText(self.dt.strftime("%M"))
        self.ui.Secs.setText(self.dt.strftime("%S"))

        if self.json.return_specific_json("showSecs") is True:  # Show Secs
            self.ui.Secs.setVisible(True)
            self.ui.Sep2.setVisible(True)

        else:
            self.ui.Secs.setVisible(False)
            self.ui.Sep2.setVisible(False)

    def _fontKey(self):
        """Every config value that affects the fonts."""
        j = self.json.return_specific_json
        return (j("fontType"), j("fontSizeTime"), j("fontSize12Hr"),
                j("fontSizeDate"), j("useBoldFont"), j("fontWeight"))

    def _makeFont(self, size: int) -> QFont:
        j = self.json.return_specific_json
        font = QFont(j("fontType"), max(1, size))       # stops sizes going to 0 or below
        weight = FontWeight.from_label_to_weight(j("fontWeight"))
        if j("useBoldFont") and weight < QFont.Weight.Bold:
            weight = QFont.Weight.Bold                   # Bold is the minimum, so ExtraBold/Black stay as they are
        font.setWeight(weight)
        return font

    def refreshFonts(self, force: bool = False):
        """Rebuild fonts only if a font-related setting changed."""
        key = self._fontKey()
        if not force and key == self._applied_font_key:
            return
        self._applied_font_key = key
        if key[0] is not None:          # fontType None means keep the default from the .ui file
            self.updateFont()

    def updateFont(self):
        j = self.json.return_specific_json
        time_font = self._makeFont(j("fontSizeTime"))
        hr12_font = self._makeFont(min(j("fontSize12Hr"), j("fontSizeTime")))

        for w in (self.ui.Hour, self.ui.Mins, self.ui.Secs, self.ui.Sep1, self.ui.Sep2):
            w.setFont(time_font)
        self.ui.hr12Notation.setFont(hr12_font)

    def openSettings(self):
        # Write any pending size first: the dialog reads the file and would otherwise drop it
        self.flushWindowSize()
        settings_ui = TimeDisplaySettings(parent=self)
        settings_ui.setWindowTitle("Settings")
        settings_ui.exec()
        self.json.getConfigData()  # Re-formulate JSON after settings change
        self.runSettings()  # Update GUI based on formulated settings change

    def updateSettingState(self):
        self.ui.action_Float_on_Top.setChecked(self.json.return_specific_json("isFloating"))
        self.ui.actionUse_24_Hour_Format.setChecked(self.json.return_specific_json("is24Hr"))
        self.ui.actionShow_Seconds.setChecked(self.json.return_specific_json("showSecs"))
        self.ui.actionShow_Date.setChecked(self.json.return_specific_json("showDate"))
        self.ui.actionShow_AM_PM.setChecked(self.json.return_specific_json("showHr12"))
        self.ui.actionDark_Mode.setChecked(self.json.return_specific_json("darkMode"))
        self.ui.actionFrameless.setChecked(self.json.return_specific_json("framelessWindowBar"))
        self.ui.actionUse_Native_Theme.setChecked(self.json.return_specific_json("useNativeTheme"))
        self.ui.actionUse_Bold_Font.setChecked(self.json.return_specific_json("useBoldFont"))

    def onFloatChange(self):
        if self.json.return_specific_json("isFloating") is True:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)

        # Refresh Window
        self.show()

    def runSettings(self):
        self.onSwitchTheme()
        self.onFloatChange()
        self.onUpdateWinVisibility()
        self.onUpdateWindowBar()
        self.refreshFonts()

    def settingFloat(self):
        self.json.update_specific_json("isFloating", self.ui.action_Float_on_Top.isChecked())
        self.json.update_json_file()
        self.onFloatChange()

    def setting24Hr(self):
        self.json.update_specific_json("is24Hr", self.ui.actionUse_24_Hour_Format.isChecked())
        self.json.update_json_file()

    def settingSecs(self):
        self.json.update_specific_json("showSecs", self.ui.actionShow_Seconds.isChecked())
        self.json.update_json_file()

    def settingDate(self):
        self.json.update_specific_json("showDate", self.ui.actionShow_Date.isChecked())
        self.json.update_json_file()

    def settingHr12Notation(self):
        self.json.update_specific_json("showHr12", self.ui.actionShow_AM_PM.isChecked())
        self.json.update_json_file()

    def settingDarkMode(self):
        self.json.update_specific_json("darkMode", self.ui.actionDark_Mode.isChecked())
        self.json.update_json_file()
        self.onSwitchTheme()

    def settingUseNativeTheme(self):
        self.json.update_specific_json("useNativeTheme", self.ui.actionUse_Native_Theme.isChecked())
        self.json.update_json_file()
        self.onSwitchTheme()

    def settingFramelessWindowBar(self):
        self.json.update_specific_json("framelessWindowBar", self.ui.actionFrameless.isChecked())
        self.json.update_json_file()
        self.onUpdateWindowBar()

    def settingChangeFont(self, value: int):
        self.json.update_specific_json("fontSizeTime", self.json.return_specific_json("fontSizeTime") + value)
        self.json.update_specific_json("fontSizeDate", self.json.return_specific_json("fontSizeDate") + value)
        self.json.update_specific_json("fontSize12Hr", self.json.return_specific_json("fontSize12Hr") + value)
        self.json.update_json_file()
        self.refreshFonts()

    def settingIncreaseFont(self):
        self.settingChangeFont(1)

    def settingDecreaseFont(self):
        self.settingChangeFont(-1)

    def settingUpdateUseBoldFont(self):
        self.json.update_specific_json("useBoldFont", self.ui.actionUse_Bold_Font.isChecked())
        self.json.update_json_file()
        self.refreshFonts()

    def resizeEvent(self, a0: QResizeEvent):
        super().resizeEvent(a0)
        size = self.size()

        # Nothing to do if the size matches what is already stored (e.g. on first show)
        if (self.json.return_specific_json("memHWindowSize") == size.width()
                and self.json.return_specific_json("memVWindowSize") == size.height()):
            return

        # Update the in-memory config straight away; it costs nothing
        self.json.update_specific_json("memHWindowSize", size.width())
        self.json.update_specific_json("memVWindowSize", size.height())

        # Debounce the disk write: each resize event restarts the countdown,
        # so a drag only writes once, after the window has stopped changing.
        if getattr(self, "_size_save_timer", None) is None:
            self._size_save_timer = QTimer(self)
            self._size_save_timer.setSingleShot(True)
            self._size_save_timer.setInterval(SIZE_SAVE_DELAY_MS)
            self._size_save_timer.timeout.connect(self.json.update_json_file)
        self._size_save_timer.start()

    def flushWindowSize(self):
        """Write a pending window size to disk now, if a save is still waiting."""
        timer = getattr(self, "_size_save_timer", None)
        if timer is not None and timer.isActive():
            timer.stop()
            self.json.update_json_file()

    def closeEvent(self, a0: QCloseEvent):
        self.flushWindowSize()
        super().closeEvent(a0)

    def initResize(self):
        size = QSize()
        size.setWidth(self.json.return_specific_json("memHWindowSize"))
        size.setHeight(self.json.return_specific_json("memVWindowSize"))

        # print(size)

        self.resize(size)

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def onSwitchTheme(self):
        if self.json.return_specific_json("useNativeTheme"):
            self.setStyleSheet(None)
        elif self.json.return_specific_json("darkMode"):
            self.setStyleSheet(QT_STYLESHEET_DARK)
        else:
            self.setStyleSheet(QT_STYLESHEET_LIGHT)

    def onUpdateWinVisibility(self):
        self.setWindowOpacity(self.json.return_specific_json("windowVisibility")/100)
        self.show()

    def onUpdateWindowBar(self):
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, self.json.return_specific_json("framelessWindowBar"))

        # Handle Hiding of Menu Bar + Settings Option
        self.ui.menubar.setVisible(not self.json.return_specific_json("framelessWindowBar"))
        self.show()

    def mousePressEvent(self, a0):
        self.old_pos = a0.globalPosition().toPoint()

    def mouseMoveEvent(self, a0):
        # Only drag with the left button, so a right-click for the menu doesn't move the window
        if not a0.buttons() & Qt.MouseButton.LeftButton:
            return
        self.move(self.pos() + a0.globalPosition().toPoint() - self.old_pos)
        self.old_pos = a0.globalPosition().toPoint()
        a0.accept()

    def exitAndReopen(self):
        self.flushWindowSize()
        self.timer.stop()
        QApplication.exit(EXIT_CODE_REOPEN)


class TimeDisplayFullGUI(TimeDisplayGUI):
    def __init__(self, parent=None):
        super(TimeDisplayGUI, self).__init__(parent)
        self.ui = Ui_TimeDisplay()
        self.hide()  # Initial Hiding

        # Setup UI
        self.ui.setupUi(self)
        self.setWindowTitle("TimeDisplay")
        self._connectActions()

        # Config Data
        self.json = ConfigJSON(CONFIG_NAME)
        self.json.getConfigData()

        # DateTime Data
        self.dt = None

        # Run Settings
        self.initResize()
        self.centerWindow()
        self.updateSettingState()
        self.onFloatChange()
        self.onSwitchTheme()
        self.onUpdateWinVisibility()
        self.onUpdateWindowBar()

        # Menubar - macOS Disabling (FOR TEST ONLY)
        if sys.platform == "darwin":
            # Leave disabled, always use Native Menu Bar
            # self.ui.menubar.setNativeMenuBar(False)
            # self.setWindowFlag(Qt.WindowType.Window.MacWindowToolBarButtonHint, False)
            pass

        # Hotkey - Non macOS -> use Alt+S instead of CMD key
        if sys.platform != "darwin":
            self.ui.action_Settings.setShortcut("Alt+S")

        # Misc Testing Section
        self.ui.statusbar.setVisible(False)

        # Timer to Refresh UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.processTimeDisplay)
        self.timer.setInterval(self.json.return_specific_json("intervalRate"))
        self.timer.start()

        # Frameless Window Movement Position
        self.old_pos = self.pos()

        self.ui.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)

    def getTime(self):
        super().getTime()

        # Update Date
        self.ui.DayName.setText(self.dt.strftime('%A'))
        self.ui.Date.setText(f"{self.dt.day} {self.dt.strftime('%B')} {self.dt.year}")
        self.ui.DateSep.setText(",")

        if self.json.return_specific_json("showDate") is True:
            self.ui.DayName.setVisible(True)
            self.ui.Date.setVisible(True)
            self.ui.DateSep.setVisible(True)
            self.ui.line.setVisible(True)

        else:
            self.ui.DayName.setVisible(False)
            self.ui.Date.setVisible(False)
            self.ui.DateSep.setVisible(False)
            self.ui.line.setVisible(False)

    def updateFont(self):
        super().updateFont()
        date_font = self._makeFont(self.json.return_specific_json("fontSizeDate"))
        for w in (self.ui.Date, self.ui.DateSep, self.ui.DayName):
            w.setFont(date_font)

def run_TimeDisplay(config: ConfigJSON, use_mini_ui = None):
    td_app = QApplication(sys.argv) or QApplication().instance()
    td = None

    while True:
        if use_mini_ui is None:
            config.getConfigData() # Re-formulate JSON else data is outdated
            use_mini_ui = config.return_specific_json("useMiniUI")

        new_td = TimeDisplayGUI() if use_mini_ui else TimeDisplayFullGUI()

        if td is not None:
            new_td.move(td.pos())
            td.close()
            td.deleteLater()
        td = new_td

        td.setWindowIcon(QIcon(os.path.join(Path(__file__).resolve().parent.parent, "Resources","TimeDisplayIcon_V2.png").__str__()))

        exit_code = td_app.exec()

        if exit_code != EXIT_CODE_REOPEN:
            sys.exit(exit_code)

        use_mini_ui = None
