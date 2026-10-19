from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog
from Qt6UI.QtStyleSheet import QT_STYLESHEET_DARK, QT_STYLESHEET_LIGHT
from Qt6UI.TimeDisplaySettings import Ui_Settings
from TimeDisplayLib.FontHandler import FontWeight
from UtilLib.ConfigJSON import ConfigJSON, CONFIG_NAME


class TimeDisplaySettings(QDialog):
    def __init__(self, parent):
        super(TimeDisplaySettings, self).__init__(parent)
        self.ui = Ui_Settings()
        self.json = ConfigJSON(CONFIG_NAME)
        self.json.generate_config()
        self.json.getConfigData()
        self.parent = parent

        # Setup UI
        self.ui.setupUi(self)
        self.onSwitchTheme()
        self.onUpdateFont()

        # Setup Config States
        if self.json.return_specific_json("fontType") is not None:
            self.ui.FontUsage.setCurrentFont(QFont(self.json.return_specific_json("fontType")))
        self.ui.TimeSize.setValue(self.json.return_specific_json("fontSizeTime"))
        self.ui.DateSize.setValue(self.json.return_specific_json("fontSizeDate"))
        self.ui.Hr12NotationSize.setValue(self.json.return_specific_json("fontSize12Hr"))
        self.ui.hr24Usage.setChecked(self.json.return_specific_json("is24Hr"))
        self.ui.FloatWindow.setChecked(self.json.return_specific_json("isFloating"))
        self.ui.Hr12NotUsage.setChecked(self.json.return_specific_json("showHr12"))
        self.ui.ShowSeconds.setChecked(self.json.return_specific_json("showSecs"))
        self.ui.ShowDate.setChecked(self.json.return_specific_json("showDate"))
        self.ui.useDarkMode.setChecked(self.json.return_specific_json("darkMode"))
        self.ui.WindowVisibilitySlider.setValue(self.json.return_specific_json("windowVisibility"))
        self.ui.setFrameless.setChecked(self.json.return_specific_json("framelessWindowBar"))
        self.ui.setUseNativeTheme.setChecked(self.json.return_specific_json("useNativeTheme"))
        self.ui.UseBoldFont.setChecked(self.json.return_specific_json("useBoldFont"))
        self.ui.FontWeightSelection.setCurrentIndex(FontWeight.from_label_to_index(self.json.return_specific_json("fontWeight")))
        self.ui.useMiniUI.setChecked(self.json.return_specific_json("useMiniUI"))

        # RemState - MiniUI
        # self.remStateUI = self.json.return_specific_json("useMiniUI")

        # Font
        if self.json.return_specific_json("fontType") is not None:
            # font = QFont(self.json.return_specific_json("fontType"), 20)
            title_font = QFont(self.json.return_specific_json("fontType"), 30)

            # Set Bold
            # font.setBold(self.json.return_specific_json("useBoldFont"))
            title_font.setBold(self.json.return_specific_json("useNativeTheme"))

            # Set Weight
            # font.setWeight(FontWeight.from_label_to_weight(self.json.return_specific_json("fontWeight")))
            title_font.setWeight(FontWeight.from_label_to_weight(self.json.return_specific_json("fontWeight")))

            # self.ui.TimeSize.setFont(font)
            # self.ui.DateSize.setFont(font)
            # self.ui.Hr12NotUsage.setFont(font)
            # self.ui.FloatWindow.setFont(font)
            # self.ui.FontLabel.setFont(font)
            # self.ui.hr24Usage.setFont(font)
            # self.ui.TimeSizeLabel.setFont(font)
            # self.ui.DateSizeLabel.setFont(font)
            # self.ui.Hr12NotationSizeLabel.setFont(font)
            # self.ui.FontUsage.setFont(font)
            # self.ui.Hr12NotationSize.setFont(font)
            # self.ui.ShowSeconds.setFont(font)
            # self.ui.ShowDate.setFont(font)
            # self.ui.useDarkMode.setFont(font)
            # self.ui.WindowVisibilitySlider.setFont(font)
            # self.ui.setFrameless.setFont(font)
            # self.ui.setUseNativeTheme.setFont(font)
            # self.ui.UseBoldFont.setFont(font)
            # self.ui.FontWeightSelection.setFont(font)
            # self.ui.useMiniUI.setFont(font)
            self.ui.label.setFont(title_font)

    def accept(self):
        # Update Values
        self.json.update_specific_json("fontType", self.ui.FontUsage.currentText())
        self.json.update_specific_json("fontSizeTime", self.ui.TimeSize.value())
        self.json.update_specific_json("fontSizeDate", self.ui.DateSize.value())
        self.json.update_specific_json("fontSize12Hr", self.ui.Hr12NotationSize.value())
        self.json.update_specific_json("is24Hr", self.ui.hr24Usage.isChecked())
        self.json.update_specific_json("isFloating", self.ui.FloatWindow.isChecked())
        self.json.update_specific_json("showHr12", self.ui.Hr12NotUsage.isChecked())
        self.json.update_specific_json("showSecs", self.ui.ShowSeconds.isChecked())
        self.json.update_specific_json("showDate", self.ui.ShowDate.isChecked())
        self.json.update_specific_json("darkMode", self.ui.useDarkMode.isChecked())
        self.json.update_specific_json("windowVisibility", self.ui.WindowVisibilitySlider.value())
        self.json.update_specific_json("framelessWindowBar", self.ui.setFrameless.isChecked())
        self.json.update_specific_json("useNativeTheme", self.ui.setUseNativeTheme.isChecked())
        self.json.update_specific_json("useBoldFont", self.ui.UseBoldFont.isChecked())
        self.json.update_specific_json("fontWeight", self.ui.FontWeightSelection.currentText())
        self.json.update_specific_json("useMiniUI", self.ui.useMiniUI.isChecked())

        # Update JSON File
        self.json.update_json_file()

        # Update UI
        self.onSwitchTheme()
        self.onUpdateFont()

        # Close UI
        self.close()

    def onSwitchTheme(self):
        if self.json.return_specific_json("useNativeTheme"):
            self.setStyleSheet(None)
        elif self.json.return_specific_json("darkMode") is True:
            self.setStyleSheet(QT_STYLESHEET_DARK)
        else:
            self.setStyleSheet(QT_STYLESHEET_LIGHT)

    def onUpdateFont(self):
        if self.json.return_specific_json("fontType") is not None:
            # font = QFont(self.json.return_specific_json("fontType"), 20)
            title_font = QFont(self.json.return_specific_json("fontType"), 30)

            # Set Bold
            # font.setBold(self.json.return_specific_json("useBoldFont"))
            title_font.setBold(self.json.return_specific_json("useBoldFont"))

            # Set Weight
            # font.setWeight(FontWeight.from_label_to_weight(self.json.return_specific_json("fontWeight")))
            title_font.setWeight(FontWeight.from_label_to_weight(self.json.return_specific_json("fontWeight")))

            # self.ui.TimeSize.setFont(font)
            # self.ui.DateSize.setFont(font)
            # self.ui.Hr12NotUsage.setFont(font)
            # self.ui.FloatWindow.setFont(font)
            # self.ui.FontLabel.setFont(font)
            # self.ui.hr24Usage.setFont(font)
            # self.ui.TimeSizeLabel.setFont(font)
            # self.ui.DateSizeLabel.setFont(font)
            # self.ui.Hr12NotationSizeLabel.setFont(font)
            # self.ui.FontUsage.setFont(font)
            # self.ui.Hr12NotationSize.setFont(font)
            # self.ui.ShowSeconds.setFont(font)
            # self.ui.ShowDate.setFont(font)
            # self.ui.useDarkMode.setFont(font)
            # self.ui.WindowVisibilityLabel.setFont(font)
            # self.ui.setFrameless.setFont(font)
            # self.ui.setUseNativeTheme.setFont(font)
            # self.ui.useMiniUI.setFont(font)
            self.ui.label.setFont(title_font)
