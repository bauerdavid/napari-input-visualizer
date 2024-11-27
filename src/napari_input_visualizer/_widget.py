import re
from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QHBoxLayout, QSizePolicy
from qtpy.QtCore import QEvent, Qt, QSize, QTemporaryFile, QTimer
from qtpy.QtGui import QKeyEvent
from napari import Viewer

key_lookup = {
    Qt.Key_Space: "Space",
    Qt.Key_Enter: "Enter",
    Qt.Key_Return: "Return",
    Qt.Key_Escape: "Esc",
    Qt.Key_Tab: "Tab",
    Qt.Key_Delete: "Del",
    Qt.Key_Minus: "-",
    Qt.Key_Plus: "+",
    Qt.Key_Backspace: "Backspace",
    Qt.Key_Home: "Home",
    Qt.Key_End: "End",
    Qt.Key_PageUp: "Page Up",
    Qt.Key_PageDown: "Page Down",
    Qt.Key_Slash: "/",
    Qt.Key_Asterisk: "*",
    Qt.Key_Comma: ",",
    Qt.Key_Period: ".",
    Qt.Key_Left: u"\u2190",
    Qt.Key_Right: u"\u2192",
    Qt.Key_Up: u"\u2191",
    Qt.Key_Down: u"\u2193"
} | {key: "F%d" % (key-Qt.Key_F1 + 1) for key in range(Qt.Key_F1, Qt.Key_F12+1)}\
  | {key: chr(key) for key in set(range(Qt.Key_A, Qt.Key_Z+1)) | set(range(Qt.Key_0, Qt.Key_9+1))}

event_lookup = {"0": "QEvent::None",
                "114": "QEvent::ActionAdded",
                "113": "QEvent::ActionChanged",
                "115": "QEvent::ActionRemoved",
                "99": "QEvent::ActivationChange",
                "121": "QEvent::ApplicationActivate",
                "122": "QEvent::ApplicationDeactivate",
                "36": "QEvent::ApplicationFontChange",
                "37": "QEvent::ApplicationLayoutDirectionChange",
                "38": "QEvent::ApplicationPaletteChange",
                "214": "QEvent::ApplicationStateChange",
                "35": "QEvent::ApplicationWindowIconChange",
                "68": "QEvent::ChildAdded",
                "69": "QEvent::ChildPolished",
                "71": "QEvent::ChildRemoved",
                "40": "QEvent::Clipboard",
                "19": "QEvent::Close",
                "200": "QEvent::CloseSoftwareInputPanel",
                "178": "QEvent::ContentsRectChange",
                "82": "QEvent::ContextMenu",
                "183": "QEvent::CursorChange",
                "52": "QEvent::DeferredDelete",
                "60": "QEvent::DragEnter",
                "62": "QEvent::DragLeave",
                "61": "QEvent::DragMove",
                "63": "QEvent::Drop",
                "170": "QEvent::DynamicPropertyChange",
                "98": "QEvent::EnabledChange",
                "10": "QEvent::Enter",
                "150": "QEvent::EnterEditFocus",
                "124": "QEvent::EnterWhatsThisMode",
                "206": "QEvent::Expose",
                "116": "QEvent::FileOpen",
                "8": "QEvent::FocusIn",
                "9": "QEvent::FocusOut",
                "23": "QEvent::FocusAboutToChange",
                "97": "QEvent::FontChange",
                "198": "QEvent::Gesture",
                "202": "QEvent::GestureOverride",
                "188": "QEvent::GrabKeyboard",
                "186": "QEvent::GrabMouse",
                "159": "QEvent::GraphicsSceneContextMenu",
                "164": "QEvent::GraphicsSceneDragEnter",
                "166": "QEvent::GraphicsSceneDragLeave",
                "165": "QEvent::GraphicsSceneDragMove",
                "167": "QEvent::GraphicsSceneDrop",
                "163": "QEvent::GraphicsSceneHelp",
                "160": "QEvent::GraphicsSceneHoverEnter",
                "162": "QEvent::GraphicsSceneHoverLeave",
                "161": "QEvent::GraphicsSceneHoverMove",
                "158": "QEvent::GraphicsSceneMouseDoubleClick",
                "155": "QEvent::GraphicsSceneMouseMove",
                "156": "QEvent::GraphicsSceneMousePress",
                "157": "QEvent::GraphicsSceneMouseRelease",
                "182": "QEvent::GraphicsSceneMove",
                "181": "QEvent::GraphicsSceneResize",
                "168": "QEvent::GraphicsSceneWheel",
                "18": "QEvent::Hide",
                "27": "QEvent::HideToParent",
                "127": "QEvent::HoverEnter",
                "128": "QEvent::HoverLeave",
                "129": "QEvent::HoverMove",
                "96": "QEvent::IconDrag",
                "101": "QEvent::IconTextChange",
                "83": "QEvent::InputMethod",
                "207": "QEvent::InputMethodQuery",
                "169": "QEvent::KeyboardLayoutChange",
                "6": "QEvent::KeyPress",
                "7": "QEvent::KeyRelease",
                "89": "QEvent::LanguageChange",
                "90": "QEvent::LayoutDirectionChange",
                "76": "QEvent::LayoutRequest",
                "11": "QEvent::Leave",
                "151": "QEvent::LeaveEditFocus",
                "125": "QEvent::LeaveWhatsThisMode",
                "88": "QEvent::LocaleChange",
                "176": "QEvent::NonClientAreaMouseButtonDblClick",
                "174": "QEvent::NonClientAreaMouseButtonPress",
                "175": "QEvent::NonClientAreaMouseButtonRelease",
                "173": "QEvent::NonClientAreaMouseMove",
                "177": "QEvent::MacSizeChange",
                "43": "QEvent::MetaCall",
                "102": "QEvent::ModifiedChange",
                "4": "QEvent::MouseButtonDblClick",
                "2": "QEvent::MouseButtonPress",
                "3": "QEvent::MouseButtonRelease",
                "5": "QEvent::MouseMove",
                "109": "QEvent::MouseTrackingChange",
                "13": "QEvent::Move",
                "197": "QEvent::NativeGesture",
                "208": "QEvent::OrientationChange",
                "12": "QEvent::Paint",
                "39": "QEvent::PaletteChange",
                "131": "QEvent::ParentAboutToChange",
                "21": "QEvent::ParentChange",
                "212": "QEvent::PlatformPanel",
                "217": "QEvent::PlatformSurface",
                "75": "QEvent::Polish",
                "74": "QEvent::PolishRequest",
                "123": "QEvent::QueryWhatsThis",
                "106": "QEvent::ReadOnlyChange",
                "199": "QEvent::RequestSoftwareInputPanel",
                "14": "QEvent::Resize",
                "204": "QEvent::ScrollPrepare",
                "205": "QEvent::Scroll",
                "117": "QEvent::Shortcut",
                "51": "QEvent::ShortcutOverride",
                "17": "QEvent::Show",
                "26": "QEvent::ShowToParent",
                "50": "QEvent::SockAct",
                "192": "QEvent::StateMachineSignal",
                "193": "QEvent::StateMachineWrapped",
                "112": "QEvent::StatusTip",
                "100": "QEvent::StyleChange",
                "87": "QEvent::TabletMove",
                "92": "QEvent::TabletPress",
                "93": "QEvent::TabletRelease",
                "171": "QEvent::TabletEnterProximity",
                "172": "QEvent::TabletLeaveProximity",
                "219": "QEvent::TabletTrackingChange",
                "22": "QEvent::ThreadChange",
                "1": "QEvent::Timer",
                "120": "QEvent::ToolBarChange",
                "110": "QEvent::ToolTip",
                "184": "QEvent::ToolTipChange",
                "194": "QEvent::TouchBegin",
                "209": "QEvent::TouchCancel",
                "196": "QEvent::TouchEnd",
                "195": "QEvent::TouchUpdate",
                "189": "QEvent::UngrabKeyboard",
                "187": "QEvent::UngrabMouse",
                "78": "QEvent::UpdateLater",
                "77": "QEvent::UpdateRequest",
                "111": "QEvent::WhatsThis",
                "118": "QEvent::WhatsThisClicked",
                "31": "QEvent::Wheel",
                "132": "QEvent::WinEventAct",
                "24": "QEvent::WindowActivate",
                "103": "QEvent::WindowBlocked",
                "25": "QEvent::WindowDeactivate",
                "34": "QEvent::WindowIconChange",
                "105": "QEvent::WindowStateChange",
                "33": "QEvent::WindowTitleChange",
                "104": "QEvent::WindowUnblocked",
                "203": "QEvent::WinIdChange",
                "126": "QEvent::ZOrderChange", }

class InputVisualizerWidget(QWidget):
    def __init__(self, viewer: Viewer):
        super().__init__(viewer.window.qt_viewer.window())
        self.button_count = 0
        self.shift_down = False
        self.ctrl_down = False
        self.alt_down = False
        self.meta_down = False
        main_layout = QVBoxLayout()
        visualizers_layout = QHBoxLayout()

        modifiers_layout = QVBoxLayout()
        self.ctrl_label = QLabel("Ctrl")
        font = self.ctrl_label.font()
        font.setPointSize(11)
        self.ctrl_label.setFont(font)
        modifiers_layout.addWidget(self.ctrl_label)
        self.shift_label = QLabel("Shift")
        self.shift_label.setFont(font)
        modifiers_layout.addWidget(self.shift_label)
        self.alt_label = QLabel("Alt")
        self.alt_label.setFont(font)
        modifiers_layout.addWidget(self.alt_label)
        modifiers_layout.addStretch()
        self.update_modifiers_color()
        visualizers_layout.addLayout(modifiers_layout)

        layout = QVBoxLayout()
        self.key_seq_label = QLabel("                  ")
        self.key_seq_label.setStyleSheet("color: black; background-color: white")
        self.key_seq_label.setSizePolicy(self.key_seq_label.sizePolicy().horizontalPolicy(), QSizePolicy.Maximum)
        self.key_seq_label.setAlignment(Qt.AlignCenter)
        font.setPointSize(20)
        self.key_seq_label.setFont(font)
        layout.addWidget(self.key_seq_label)
        arrow_up_svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28.35 141.73"><defs><style>.cls-1,.cls-2{fill:none;}.cls-2{stroke:#1d1d1b;stroke-linecap:round;stroke-linejoin:round;stroke-width:4px;}</style></defs><title>Asset 2</title><g id="Layer_2" data-name="Layer 2"><g id="Layer_1-2" data-name="Layer 1"><rect class="cls-1" width="28.35" height="141.73" rx="14.17"/><polyline class="cls-2" points="4.63 26.85 14.17 17.3 23.72 26.85"/><polyline class="cls-2" points="4.63 43.59 14.17 34.04 23.72 43.59"/><polyline class="cls-2" points="4.63 60.32 14.17 50.77 23.72 60.32"/></g></g></svg>'
        file_arrow_up = QTemporaryFile(self)
        if file_arrow_up.open():
            file_arrow_up.write(arrow_up_svg)
            file_arrow_up.flush()
            self.arrow_up_path = file_arrow_up.fileName()

        arrow_down_svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28.35 141.73"><defs><style>.cls-1,.cls-2{fill:none;}.cls-2{stroke:#1d1d1b;stroke-linecap:round;stroke-linejoin:round;stroke-width:4px;}</style></defs><title>Asset 3</title><g id="Layer_2" data-name="Layer 2"><g id="Layer_1-2" data-name="Layer 1"><rect class="cls-1" width="28.35" height="141.73" rx="14.17" transform="translate(28.35 141.73) rotate(-180)"/><polyline class="cls-2" points="23.72 114.88 14.17 124.43 4.63 114.88"/><polyline class="cls-2" points="23.72 98.15 14.17 107.69 4.63 98.15"/><polyline class="cls-2" points="23.72 81.41 14.17 90.96 4.63 81.41"/></g></g></svg>'
        file_arrow_down = QTemporaryFile(self)
        if file_arrow_down.open():
            file_arrow_down.write(arrow_down_svg)
            file_arrow_down.flush()
            self.arrow_down_path = file_arrow_down.fileName()
        self.left_btn_display = QWidget()
        self.left_btn_display.setFixedSize(QSize(30, 50))
        self.middle_btn_display = QWidget()
        self.middle_btn_display.setFixedSize(QSize(10, 50))
        self.right_btn_display = QWidget()
        self.right_btn_display.setFixedSize(QSize(30, 50))
        self.update_mouse_btn_color()
        mouse_display_layout = QHBoxLayout()
        mouse_display_layout.addStretch()
        mouse_display_layout.addWidget(self.left_btn_display)
        mouse_display_layout.addWidget(self.middle_btn_display)
        mouse_display_layout.addWidget(self.right_btn_display)
        mouse_display_layout.addStretch()
        mouse_display_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(mouse_display_layout)

        visualizers_layout.addLayout(layout)
        main_layout.addLayout(visualizers_layout)
        self.last_key_seq = QLabel()
        self.last_key_seq.setStyleSheet("color: black; background-color: gray; border-radius: 5px;")
        font.setPointSize(11)
        self.last_key_seq.setFont(font)
        main_layout.addWidget(self.last_key_seq)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        QApplication.instance().installEventFilter(self)

    def update_mouse_btn_color(self, buttons=0, double_click=False):
        stylesheet_format = "background-color: %s; border-radius: 5px;"
        button_color = "green" if double_click else "red"
        self.left_btn_display.setStyleSheet(stylesheet_format % (button_color if buttons & Qt.LeftButton else "lightgray"))
        self.right_btn_display.setStyleSheet(stylesheet_format % (button_color if buttons & Qt.RightButton else "lightgray"))
        self.middle_btn_display.setStyleSheet(stylesheet_format % (button_color if buttons & Qt.MiddleButton else "lightgray"))

    def update_modifiers_color(self, modifiers=0):
        stylesheet_format = "color: black; background-color: %s; border-radius: 5px;"
        self.ctrl_label.setStyleSheet(stylesheet_format % ("red" if modifiers & Qt.ControlModifier else "lightgray"))
        self.alt_label.setStyleSheet(stylesheet_format % ("red" if modifiers & Qt.AltModifier else "lightgray"))
        self.shift_label.setStyleSheet(stylesheet_format % ("red" if modifiers & Qt.ShiftModifier else "lightgray"))


    def update_wheel_direction(self, direction=0):
        stylesheet = self.middle_btn_display.styleSheet()
        if direction:
            new_url = self.arrow_up_path if direction>0 else self.arrow_down_path
            if "border-image" not in stylesheet:
                stylesheet += "border-image: url(%s) 0 0 0 0 stretch stretch;" % new_url
            else:
                stylesheet = re.sub("url\\(.*\\)", "url(%s)" % new_url, stylesheet, 1)
            stylesheet = re.sub("background-color: [^;]*;", "background-color: orange;", stylesheet, 1)
        else:
            stylesheet = re.sub("border-image: url\\(.*\\) 0 0 0 0 stretch stretch;", "", stylesheet, 1)
            stylesheet = re.sub("background-color: [^;]*;", "background-color: lightgray;", stylesheet, 1)
        self.middle_btn_display.setStyleSheet(stylesheet)

    def eventFilter(self, source: 'QObject', event: 'QEvent') -> bool:
        sequence_str = ""
        sequence_end = ""
        wheel_direction = 0
        if event.type() in [QEvent.ApplicationDeactivate, QEvent.ApplicationActivate]:
            self.shift_down = False
            self.ctrl_down = False
            self.alt_down = False
            self.meta_down = False
            self.update_mouse_btn_color()
            self.update_modifiers_color()
        elif event.type() in [QEvent.KeyPress, QEvent.KeyRelease] and not event.isAutoRepeat():
            modifiers = event.modifiers()
            self.shift_down = modifiers & Qt.ShiftModifier
            self.ctrl_down = modifiers & Qt.ControlModifier
            self.alt_down = modifiers & Qt.AltModifier
            self.meta_down = modifiers & Qt.MetaModifier
            self.update_modifiers_color(modifiers)
            if event.key() in key_lookup:
                if event.type() != QKeyEvent.KeyRelease:
                    button_text = sequence_end = key_lookup[event.key()]
                else:
                    button_text = ""
                self.key_seq_label.setText(button_text)
        elif event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease]:
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() & Qt.LeftButton:
                    sequence_end = "Left click"
                elif event.buttons() & Qt.RightButton:
                    sequence_end = "Right click"
                elif event.buttons() & Qt.MiddleButton:
                    sequence_end = "Middle click"
            self.update_mouse_btn_color(event.buttons())
        elif event.type() == QEvent.MouseButtonDblClick:
            if event.buttons() & Qt.LeftButton:
                sequence_end = "Left double-click"
            elif event.buttons() & Qt.RightButton:
                sequence_end = "Right double-click"
            elif event.buttons() & Qt.MiddleButton:
                sequence_end = "Middle double-click"
            self.update_mouse_btn_color(event.buttons(), True)
        elif event.type() == QEvent.Wheel:
            if event.angleDelta().y() > 0:
                sequence_end = "Wheel " + u"\u2191"
            else:
                sequence_end = "Wheel " + u"\u2193"
            wheel_direction = event.angleDelta().y()
            QTimer.singleShot(200, self.update_wheel_direction)
        else:
            print(source.objectName(), event.type(), event_lookup.get(event.type(), "NOT FOUND"))
            return super().eventFilter(source, event)
        self.update_wheel_direction(wheel_direction)
        if self.ctrl_down:
            sequence_str += "Ctrl + "
        if self.shift_down:
            sequence_str += "Shift + "
        if self.alt_down:
            sequence_str += "Alt + "
        if self.meta_down:
            sequence_str += "Meta + "
        if sequence_end:
            sequence_str += sequence_end
            self.last_key_seq.setText("Last action: %s" % sequence_str)
        return super().eventFilter(source, event)
