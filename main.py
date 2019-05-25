import sys
import os
import random
import json

import subprocess
import time
from datetime import datetime

from PyQt5.QtCore import (QSize, Qt, QRegExp, QRegularExpression)
from PyQt5.QtGui import (QIcon, QPixmap, QImage, QPalette, QBrush, QIntValidator, QRegExpValidator)
from PyQt5.QtWidgets import (QTextBrowser, QMainWindow, QLabel, QLineEdit, QPushButton,QSystemTrayIcon, QMessageBox,
                             QApplication, QMenu, QHBoxLayout, QAction, QFileDialog, QVBoxLayout, QComboBox, QWidget,
                             QTabWidget, QCheckBox, qApp)

import paho.mqtt.client as mqtt


class App(QMainWindow):

    """ App Class for initializing the UI and its abilities.

    The user interface has many capabilities that enable ease of use and provide user experience.

    Attributes:
        title (str): Windows Application's title.
        icon (str):  Stores the icon image's path.
        left, top, width, height (int): Windows Application's Size & Screen positioning.
        tray (QSystemTrayIcon): Application's icon tray with menu ability for show, hide & exit.
        statusbar (statusBar): Status bar of the UI which shows operations's status after execution.

    Methods:
        super().__init__(): QMainWindow Base Class __init__ constructor.
        create_tray(self): Creates the UI's Icon Tray and its abilities.
        system_icon_tray_events(self, reason): Sets events for the icon tray when clicking the mouse on it.
        create_button(self, width, height, image, func, func_args=None): Generic Method for creating a button.
        create_line(self, width, height, size, text): Generic Method for creating a line.
        create_text_browser(self, width, height, text_size): Generic Method for creating a Text Browser(Display Box).
        create_label(self, width, height, img_path): Generic Method for creating a Label( For Images ).
        create_combo_box(self, option_list, func, func_args=None): Generic Method for creating a combo box.
        set_main_window_conf(self, width, height, brush_size, img_path):
        init_ui(self): Initialize the UI.
        closeEvent(self, event): An Overriding Method designed to open a small window to make sure the user wants to
            exit the UI.
    """

    def __init__(self):

        """Initializing App Class"""

        super().__init__()

        self.window = MainWindow(self)
        self.setCentralWidget(self.window)

        self.title = 'MQTT Client'
        self.icon = 'images/mqtt.ico'
        self.left = 50
        self.top = 28
        self.width = 1280
        self.height = 680
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Welcome!")

        self.tray = self.create_tray()

        self.init_ui()

    def closeEvent(self, event):

        """
        Close App Event(Overiding Method):

        Args:
           event (QCloseEvent): Close Event.

        Parameters:
             close (QMessageBox): A message box to interacte with the user before closing the UI.

        Returns:
            None
        """


        try:
            close = QMessageBox()

            close.setText("<center>Are You Sure?\n")
            close.setWindowTitle("Quit Window")
            close.setWindowIcon(QIcon(self.icon))

            close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            close = close.exec()

            if close == QMessageBox.Yes:
                #self.tray.hide()
                self.tray.setVisible(False)
                event.accept()

            else:
                event.ignore()
                raise UserWarning(" Quit Canceled!")

        except UserWarning as uw:
            self.statusbar.showMessage("UserWarning: {}".format(uw))
        except Exception as e:
            self.statusbar.showMessage("Error has Occurred: {}".format(e))

    def create_tray(self):

        """
        Creates UI's Icon Tray & It's abilites.

        Args:
            None.

        Parameters:
            icon (QIcon): UI Tray Icon Image.
            show_icon (QIcon): Icon Image for show action.
            hide_icon (QIcon): Icon Image for hide action.
            quit_icon (QIcon): Icon Image for quit/exit action.
            tray (QSystemTrayIcon): UI's tray object.
            show_action (QAction): show action action ( Text & Function ).
            quit_action (QAction): quit/exit action action ( Text & Function ).
            hide_action (QAction): show action action ( Text & Function ).
            tray_menu (QMenu): A Menu object which displayed when right click of the mouse clicked by the user.

        Returns:
            tray (QSystemTrayIcon): UI's tray object.
        """

        try:
            icon = QIcon("images/mqtt.ico")
            show_icon = QIcon("images/maximize.ico")
            hide_icon = QIcon("images/minimize.ico")
            quit_icon = QIcon("images/quit.ico")

            # Create the tray
            tray = QSystemTrayIcon()

            # System Icon Tray events
            tray.activated.connect(self.system_icon_tray_events)

            tray.setIcon(icon)
            tray.setToolTip("MQTT Client")
            #self.tray.setVisible(False)
            show_action = QAction("Show", self)
            quit_action = QAction("Exit", self)
            hide_action = QAction("Hide", self)

            show_action.setIcon(show_icon)
            hide_action.setIcon(hide_icon)
            quit_action.setIcon(quit_icon)

            show_action.triggered.connect(self.show)
            hide_action.triggered.connect(self.hide)
            quit_action.triggered.connect(qApp.quit)

            # Creates a Menu
            tray_menu = QMenu()
            tray_menu.addAction(show_action)
            tray_menu.addAction(hide_action)
            tray_menu.addAction(quit_action)
            tray.setContextMenu(tray_menu)
            tray.show()

            return tray

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def system_icon_tray_events(self, reason):

        """
        UI's Icon Tray Events when the user using right click of his mouse.

        Args:
            reason (ActivationReason): Enum Value returned which described which events happend.
            3 is Double Click to show the UI.
            4 is Middle Click of the mouse to hide the UI.

        Parameters:
            None.

        Returns:
            None.
        """

        try:
            if reason == QSystemTrayIcon.DoubleClick:
                self.show()
            elif reason == QSystemTrayIcon.MiddleClick:
                self.hide()
            # mouse left single click
            #elif reason == QSystemTrayIcon.Trigger:
            #    print("Trigger")
            # mouse right click
            #elif reason == QSystemTrayIcon.Context:
            #    print("Context")
        except Exception as e:
            self.statusbar.showMessage("Error Has Occured: {}".format(e))

    def create_button(self, width, height, image, func, func_args=None):

        """  Generic Pattern For Create Button

        Args:
           width, height, (int): Size of the button.
           image (str): Path of the background image.
           func (method): The function which be executed when the button clicked.
           func_args (object or list): instance/instances of a class/classes to use.

        Parameters:
            btn (QPushButton): The button with all the properties set.
            btn_image (QPixmap):  An object to store the background image for the button.

        Returns:
            btn (QPushButton): The button with all the properties set.

        """

        try:
            # Sets Button's Size & Position
            btn = QPushButton(self)
            btn.setFixedWidth(width)
            btn.setFixedHeight(height)

            # Sets Button's Image
            btn_image = QPixmap(image)
            btn.setIcon(QIcon(btn_image))
            btn.setIconSize(QSize(200, 200))

            # Attach Function to a Button according to func & text arguments
            if func_args is not None:
                btn.clicked.connect(lambda checked: func(func_args))
            else:
                btn.clicked.connect(func)

            return btn

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def create_line(self, width, height, size, text):

        """   Pattern For Create Line

        Args:
           width, height (int): Size of the line.
           size (int): An integer to determine the size of the text.
           text (str): A Text string for a default display inside the line edit.

        Parameters:
            line (QLineEdit): The line with all the properties set.

        Returns:
            line (QLineEdit): The line with all the properties set.

        """
        try:
            # Sets Line's Size & Position
            line = QLineEdit(self)
            line.setFixedSize(width, height)

            # Sets Line's Default Text
            line.setPlaceholderText(text)

            line.setAlignment(Qt.AlignCenter)

            # Sets Text's Size & Style
            line.setStyleSheet("font-size: {}px; font: bold 14px;".format(size))

            return line

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def create_text_browser(self, width, height, text_size):

        """   Pattern For Create Text Browser

        Args:
           width, height (int): Size of the Text Browser (Display Box).
           text_size (str): An integer to determine the size of the text.

        Parameters:
            text_browser (QTextBrowser): The Text Browser with all the properties set.

        Returns:
            text_browser (QTextBrowser): The Text Browser with all the properties set.

        """

        try:

            text_browser = QTextBrowser(self)
            text_browser.setFixedSize(width, height)
            text_browser.setStyleSheet(text_size + ";font: bold 18px;")

            return text_browser

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def create_label(self, width, height, img_path):

        """   Pattern For Create Text Browser

        Args:
           width, height (int): Size of the Qlabel(for image).
           img_path (str): A text string to for image path.

        Parameters:
            label (QLabel): The label with all the properties set.

        Returns:
            label (QLabel): The label with all the properties set.

        """

        try:

            label = QLabel(self)

            # Load Image & Resize it
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaled(QSize(width, height))

            # Set Image & Its Position
            label.setPixmap(pixmap)
            label.setGeometry(0, 0, width, height)

            return label

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def create_combo_box(self, option_list, func, func_args=None):

        """   Pattern For Create Combo Box

             Args:
                option_list (list): Option list of the combo-box.
                func (method): The Method to bind to the combo box.
                func_args (object or list): instance/instances of a class/classes to use.

             Parameters:
                 combo_box (QComboBox): The Combo Box Object which created.

             Returns:
                 combo_box (QComboBox): The Combo Box Object which created.

        """

        try:

            combo_box = QComboBox(self)

            for item in option_list:
                combo_box.addItem(item)

            # Attach Function to a Button according to func & text arguments
            combo_box.activated[str].connect(lambda checked: func(combo_box.currentText(), func_args))

            return combo_box

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def set_main_window_conf(self, width, height, brush_size, img_path):

        """
        Configure Main Window of the UI.

        Args:
           width, height, brush_size: (int): An integers to configure the Size of the window & Brush size.
           img_path (str): A text string of the window background image path.

        Parameters:
             bg_image (QImage): An Object which nandels the background image.
             palette (QPalette): An Object which sets the background image at the main window app.

        Returns:
            None
        """

        try:
            self.setWindowIcon(QIcon(self.icon))
            self.setWindowTitle(self.title)
            self.setGeometry(self.left, self.top, self.width, self.height)

            bg_image = QImage(img_path)
            bg_image = bg_image.scaled(QSize(width-125, height-300))  # resize Image to widgets size

            # Sets the background image at the Main window App
            palette = QPalette()
            palette.setBrush(brush_size, QBrush(bg_image))  # 10 = Windowrole
            self.setPalette(palette)

        except Exception as e:
            print("Couldn't Set The Main Window Configuration Because: {}".format(e))

    def init_ui(self):

        # Set Main Window Configurtaion
        self.set_main_window_conf(1500, 1024, 10, "images/bg1.jpg")

        # Display the UI
        self.show()


class ConfigurationWidget(QWidget):

    """ ConfigurationWidget Class for initializing the Configuration Tab.

    The user interface has many capabilities that enable ease of use and provide user experience.

    Attributes:
        broker_ip (None): Future storing for Broker IP.
        port (None): Future storing for Broker Port.
        username (None): Future storing for Username.
        password (None): Future storing for Password.
        qos (None): Future storing for Broker QoS option.
        retain (None): Future storing for Retain option.
        clean_session (None): Future storing for Clean Session option.
        topic (None): Future storing for Topic.
        current_settings (dict): A dictionary to store all the class variables.
        client_id (None): Future storing for unique client id.

        self.banner, self.curr_conf_title, self.conf_title (QLabel): Logos/Banners
        self.broker_ip_img, selff.broker_port_img, self.topic_img, self.username_img, self.password_img,
            self.client_id_img, self.clean_session_img, self.retain_img, self.qos_img (QLabel): Images for Buttons's
            background.
        self.broker_ip_insert_line, self.port_insert_line, self.topic_insert_line, self.username_insert_line,
            self.password_insert_line(QLine): Insert Line Widget.
        self.minimize_tray_btn, self.broker_ip_set_btn, self.port_set_btn, self.topic_set_btn, self.username_set_btn
            self.password_set_btn, self.generate_client_id_btn, self.save_conf_btn, self.load_conf_btn (QPushButton):
            Buttons Widget.
        self.qos_combo_box, self.retain_combo_box, self.clean_session_combo_box (QComboBox): Combo Box Widget.
        self.broker_ip_display_box, self.port_display_box, self.topic_display_box, self.username_display_box,
            self.password_display_box, self.unique_client_id_display_box, self.clean_session_display_box,
            self.retain_display_box, self.qos_display_box (QTextBrowser): Text Browser/Display Box widget.

        self.main_layout (QVBoxLayout): Creating the Main Layout to contain all the sub layouts
        banner, curr_conf_title, display_hlay, display_hlay2, display_hlay3, conf_title , conf_hlay, conf_hlay3,
        spacer, bottom_frame (QHBoxLayout): Sub frames to stores Tab's widgets.

        base_exp (str): String of base regular expersion of an int between 0 to 255.
        self.regexp (QRegExp): Regular Expertion for IP's pattern.
        self.validator (QRegExpValidator): Validator for user's input with our regular expression



    Methods:
        super(ConfigurationWidget, self).__init__(parent): ConfigurationWidget & App constructor.
        App.create_label, App.create_line, App.create_button, App.create_text_browser, App.create_combo_box: Using App's
                                                            Class Methods to build Models in the UI.
        add_widget_to_frame(self, widget_list): Adding the a sub frame list of created widgets.
        set_broker_ip(cls, instance, text=None): Set Broker IP Variable Class.
        set_port(cls, instance, text=None): Set Broker Port Variable Class.
        set_username(cls, instance, text=None): Set Username Variable Class.
        set_password(cls, instance, text=None): Set Password Variable Class.
        generate_client_id(cls, instance): Generate client id Variable Class.
        set_qos(cls, text, instance): Set QoS Option Variable Class.
        set_retain(cls, text, instance): Set Retain Option Variable Class.
        set_clean_session(cls, text, instance): Set Clean Session Option Variable Class.
        set_topic(cls, instance, text=None): Set Topic Variable Class.
        load_settings_from_json(cls, instance): Load Settings from a json file to set the variables class.
        save_settings_to_json(self), instance: Save settings to a json file from the variables class.
        update_view_conf(self): Update UI's Configuration Option Current Value.
    """

    broker_ip = 'None'
    port = 'None'
    username = 'None'
    password = 'None'
    qos = 'None'
    retain = 'None'
    clean_session = 'None'
    topic = 'None'
    current_settings = {"Broker IP": broker_ip,
                        "Port": port,
                        "Username": username,
                        "Password": password,
                        "QoS": qos,
                        "Retain": retain,
                        "Clean Session": clean_session,
                        "Topic": topic}
    client_id = 'None'

    def __init__(self, parent=None):

        super(ConfigurationWidget, self).__init__(parent)

        self.setAutoFillBackground(True)

        # Banners
        self.banner = App.create_label(parent, 500, 100, 'images/banner4.png')
        self.curr_conf_title = App.create_label(parent, 500, 60, 'images/conf_tab/curr_conf.png')
        self.conf_title = App.create_label(parent, 500, 60, 'images/conf_tab/config_pannel.png')

        # Buttons Images

        self.broker_ip_img = App.create_label(parent, 200, 60, 'images/conf_tab/broker_ip_img.png')
        self.broker_port_img = App.create_label(parent, 200, 60, 'images/conf_tab/broker_port_img.png')
        self.topic_img = App.create_label(parent, 200, 60, 'images/conf_tab/topic_img.png')

        self.username_img = App.create_label(parent, 200, 60, 'images/conf_tab/username_img.png')
        self.password_img = App.create_label(parent, 200, 60, 'images/conf_tab/password_img.png')
        self.client_id_img = App.create_label(parent, 200, 60, 'images/conf_tab/client_id_img.png')

        self.clean_session_img = App.create_label(parent, 200, 60, 'images/conf_tab/clean_session_img.png')
        self.retain_img = App.create_label(parent, 200, 60, 'images/conf_tab/retain_img.png')
        self.qos_img = App.create_label(parent, 200, 60, 'images/conf_tab/qos_img.png')

        # Insert Line

        self.broker_ip_insert_line = App.create_line(parent, 200, 35, 15, "Enter Broker IP")
        #regexp = QRegExp('^([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])$')
        # [0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}
        base_exp = '([1]|[1-9]?[0-9]|[1][0-9][0-9]|2[0-4][0-9]|25[0-5])'
        self.regexp = QRegExp('^' + base_exp + '\\.' + base_exp + '\\.' + base_exp + '\\.' + base_exp +'$')
        self.validator = QRegExpValidator(self.regexp)
        self.broker_ip_insert_line.setValidator(self.validator)

        self.port_insert_line = App.create_line(parent, 200, 35, 15, "Enter Port")
        self.port_insert_line.setMaxLength(5)
        self.port_insert_line.setValidator(QIntValidator(1, 65000))

        self.topic_insert_line = App.create_line(parent, 200, 35, 15, "Enter Topic")
        self.username_insert_line = App.create_line(parent, 200, 35, 15, "Enter Username")
        self.password_insert_line = App.create_line(parent, 200, 35, 15, "Enter Password")

        # Buttons
        self.minimize_tray_btn = App.create_button(parent, 197,38, 'images/minimize_to_tray_img.png',
                                                       parent.hide)

        self.broker_ip_set_btn = App.create_button(parent, 200, 40, 'images/conf_tab/set_broker_ip.png',
                                                   ConfigurationWidget.set_broker_ip, [self, parent])
        self.port_set_btn = App.create_button(parent, 200, 40, 'images/conf_tab/set_broker_port.png',
                                              ConfigurationWidget.set_port, [self, parent])
        self.topic_set_btn = App.create_button(parent, 200, 40, 'images/conf_tab/set_topic.png',
                                               ConfigurationWidget.set_topic, [self, parent])
        self.username_set_btn = App.create_button(parent, 200, 35, 'images/conf_tab/set_username.png',
                                                  ConfigurationWidget.set_username, [self, parent])
        self.password_set_btn = App.create_button(parent, 200, 35, 'images/conf_tab/set_password.png',
                                                  ConfigurationWidget.set_password, [self, parent])
        self.generate_client_id_btn = App.create_button(parent, 200, 40, 'images/conf_tab/generate_client_id.png',
                                                        ConfigurationWidget.generate_client_id, [self, parent])
        self.save_conf_btn = App.create_button(parent, 110, 38, 'images/conf_tab/save_conf_img.png',
                                               ConfigurationWidget.save_settings_to_json, [self, parent])
        self.load_conf_btn = App.create_button(parent, 110, 38, 'images/conf_tab/load_conf_img.png',
                                               ConfigurationWidget.load_settings_from_json, [self, parent])
        self.reset_settings_btn = App.create_button(parent, 169, 38, 'images/conf_tab/reset_settings.png',
                                               ConfigurationWidget.reset_settings_to_none, [self, parent])

        # Combo Boxes
        self.qos_combo_box = App.create_combo_box(parent, ["QoS", "0", "1", "2"], ConfigurationWidget.set_qos,
                                                  [self, parent])
        self.retain_combo_box = App.create_combo_box(parent, ["Retain", "True", "False"],
                                                     ConfigurationWidget.set_retain, [self, parent])
        self.clean_session_combo_box = App.create_combo_box(parent, ["Clean Session", "True", "False"],
                                                            ConfigurationWidget.set_clean_session, [self, parent])

        # Display Boxes
        self.broker_ip_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")
        self.port_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")
        self.topic_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")

        self.username_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")
        self.password_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")
        self.unique_client_id_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")

        self.clean_session_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")
        self.retain_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")
        self.qos_display_box = App.create_text_browser(parent, 200, 34, "font-size: 15px;")

        # Creating the Main Layout to contain all the sub layouts
        self.main_layout = QVBoxLayout(self)

        # Add Widges to sub frames
        banner = self.add_widget_to_frame([self.minimize_tray_btn ,QLabel(""), self.banner, QLabel(""),QLabel("")])

        curr_conf_title = self.add_widget_to_frame([QLabel(""), self.curr_conf_title, QLabel("")])

        display_hlay = self.add_widget_to_frame([self.broker_ip_img, self.broker_ip_display_box, self.broker_port_img,
                                                 self.port_display_box, self.topic_img, self.topic_display_box])
        display_hlay2 = self.add_widget_to_frame([self.username_img, self.username_display_box, self.password_img,
                                                  self.password_display_box, self.client_id_img,
                                                  self.unique_client_id_display_box])
        display_hlay3 = self.add_widget_to_frame([self.clean_session_img, self.clean_session_display_box,
                                                  self.retain_img, self.retain_display_box, self.qos_img,
                                                  self.qos_display_box])

        conf_title = self.add_widget_to_frame([QLabel(""), self.conf_title, QLabel("")])
        conf_hlay = self.add_widget_to_frame([self.broker_ip_insert_line, self.broker_ip_set_btn, self.port_insert_line,
                                              self.port_set_btn, self.topic_insert_line, self.topic_set_btn] )
        conf_hlay2 = self.add_widget_to_frame([self.username_insert_line, self.username_set_btn,
                                              self.password_insert_line, self.password_set_btn, QLabel(""),
                                              self.generate_client_id_btn])
        conf_hlay3 = self.add_widget_to_frame([QLabel(""), self.qos_combo_box, self.retain_combo_box,
                                               self.clean_session_combo_box, QLabel("")])

        spacer = self.add_widget_to_frame([QLabel("")])

        bottom_frame = self.add_widget_to_frame([QLabel(""), self.reset_settings_btn, self.save_conf_btn, self.load_conf_btn, QLabel("")])

        self.main_layout.addStretch()

    def add_widget_to_frame(self, widget_list):

        """
        Add Created Widgets from a list to a Sub Frame.
        After it, add the sub frame to the main frame.

        Args:
            widget_list (list): A list which stored the widgets to add into the sub frame.

        Parameters:
            temp_frame (QHBoxLayout): A temporary frame to stored widgets.
            self.main_layout(QVBoxLayot): Main frame to stores sub frame/layouts.

        Returns:
            temp_frame (QHBoxLayout): A temporary frame to stored widgets.
        """

        try:
            temp_frame = QHBoxLayout()

            for item in widget_list:
                temp_frame.addWidget(item)

            self.main_layout.addLayout(temp_frame)

            return temp_frame

        except Exception as e:
            print("Couldn't Set The Sub Frame: {}".format(e))

    @classmethod
    def set_broker_ip(cls, instance, text=None):

        """
        Set The Broker IP Class Variable.
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the broker ip.

        Parameters:
            cls.broker_ip (str): Stores the Broker IP.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:

            # Set Value
            if text is None:
                cls.broker_ip = instance[0].broker_ip_insert_line.text()
            else:
                cls.broker_ip = text

            # Update Current Configuration Dictionary Broker IP's Value
            cls.current_settings["Broker IP"] = cls.broker_ip

            # Update The Current Configuration Display
            cls.update_view_conf(instance[0])

            instance[1].statusbar.showMessage("Broker IP Has Been Successfully Configured.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("Broker IP ValueError Configuration: {}".format(ve))
        except Exception as e:
            instance[1].statusbar.showMessage("Couldn't Set Broker IP Because: {}".format(e))

    @classmethod
    def set_port(cls, instance, text=None):

        """
        Set The Broker Port Class Variable.
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the broker port.

        Parameters:
            cls.port (int): Stores the Broker port.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:

            # Set Value
            if text is None:
                cls.port = int(instance[0].port_insert_line.text())
            else:
                cls.port = text

            # Update Current Configuration Dictionary Port's Value
            cls.current_settings["Port"] = str(cls.port)

            # Update The Current Configuration Display
            cls.update_view_conf(instance[0])

            instance[1].statusbar.showMessage("Broker Port Has Been Successfully Configured.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def set_username(cls, instance, text=None):

        """
        Set The Username Class Variable(for the mqtt-client).
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the username.

        Parameters:
            cls.username (str): Stores the Username for the mqtt-client.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:

            # Set Value
            if text is None:
                cls.username = instance[0].username_insert_line.text()
            else:
                cls.username = text

            # Update Current Configuration Dictionary Port's Value
            cls.current_settings["Username"] = cls.username

            # Update The Current Configuration Display
            cls.update_view_conf(instance[0])

            instance[1].statusbar.showMessage("Username Has Been Successfully Configured.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def set_password(cls, instance, text=None):

        """
        Set The Password Class Variable(for mqtt-client).
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the password.

        Parameters:
            cls.password (str): Stores the Password for the mqtt-client.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:

            # Set Value
            if text is None:
                cls.password = instance[0].password_insert_line.text()
            else:
                cls.password = text

            # Update Current Configuration Dictionary Port's Value
            cls.current_settings["Password"] = cls.password

            # Update The Current Configuration Display
            cls.update_view_conf(instance[0])

            instance[1].statusbar.showMessage("Password Has Been Successfully Configured.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def generate_client_id(cls, instance):

        """
        Generate & Set The Client ID Class Variable(for mqtt-client).
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.

        Parameters:
            cls.password (str): Stores the client id for the mqtt-client.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
        pass_len = 8

        try:
            # Set Value
            cls.client_id = "client_" + "".join(random.sample(chars, pass_len))

            # Update The Current Configuration Display
            cls.update_view_conf(instance[0])

            instance[1].statusbar.showMessage("Client ID Has Been Successfully Configured.")

        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def set_qos(cls, text, instance):

        """
        Set The QoS Option Class Variable.
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the broker ip.

        Parameters:
            cls.qos (int): Stores the QoS Option Value.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:
            if text is not "QoS":

                # Set Value
                cls.qos = int(text)

                # Update Current Configuration Dictionary Port's Value
                cls.current_settings["QoS"] = text

                # Update The Current Configuration Display
                cls.update_view_conf(instance[0])

                instance[1].statusbar.showMessage("QoS Has Been Successfully Configured.")

        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def set_retain(cls, text, instance):

        """
        Set The Retain Option Class Variable.
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the broker ip.

        Parameters:
            cls.retain (bool): Stores the Retain Option Boolean Value.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:

            if text is not "Retain":
                # Set Value
                cls.retain = eval(text)

                # Update Current Configuration Dictionary Port's Value
                cls.current_settings["Retain"] = text

                # Update The Current Configuration Display
                cls.update_view_conf(instance[0])

                instance[1].statusbar.showMessage("Retain Has Been Successfully Configured.")

        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def set_clean_session(cls, text, instance):

        """
        Set The Clean Session Option Class Variable.
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the broker ip.

        Parameters:
            cls.clean_session (bool): Stores the Clean Session Option Boolean Value.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:

            if text != "Clean Session":
                # Set Value
                cls.clean_session = eval(text)

                # Update Current Configuration Dictionary Port's Value
                cls.current_settings["Clean Session"] = text

                # Update The Current Configuration Display
                cls.update_view_conf(instance[0])

                instance[1].statusbar.showMessage("Clean Session Has Been Successfully Configured.")

        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def set_topic(cls, instance,  text=None):

        """
        Set The Topic Class Variable.
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the topic for publish.

        Parameters:
            cls.topic (str): Stores the topic Value.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:

            # Set Value
            if text is None:
                cls.topic = instance[0].topic_insert_line.text()
            else:
                cls.topic = text

            # Update Current Configuration Dictionary Port's Value
            cls.current_settings["Topic"] = cls.topic

            # Update The Current Configuration Display
            cls.update_view_conf(instance[0])

            instance[1].statusbar.showMessage("Topic For Publish Has Been Successfully Configured.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def load_settings_from_json(cls, instance):

        """  Data Serialization - A Method designed to load configuration data from a dictionary stored inside
             a json file. After loading the configuration data, Update the UI's Display Boxes.

         Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.

         Parameters:
             file (tuple): Stores json file's full path & a string.
             f (TextIOWrapper): File Object.
             cls.current_settings (dict): Update the Current Configuration Dictionary Value.

         Returns:
             None
        """

        try:
            file = QFileDialog.getOpenFileName(instance[0], 'Open json File For Loading Settings', "",
                                               "json file (*.json)")

            # Open the json file and load settings.
            with open(file[0], 'r') as f:

                cls.current_settings = json.load(f)

                cls.broker_ip = cls.current_settings["Broker IP"]

                if cls.port is 'None':
                    if cls.current_settings["Port"] == 'None':
                        cls.port = cls.current_settings["Port"]
                    else:
                        cls.port = int(cls.current_settings["Port"])
                else:
                    if cls.current_settings["Port"] == 'None':
                        cls.port = cls.current_settings["Port"]
                    else:
                        cls.port = int(cls.current_settings["Port"])

                cls.username = cls.current_settings["Username"]
                cls.password = cls.current_settings["Password"]

                if cls.qos is 'None':
                    if cls.current_settings["QoS"] == 'None':
                        cls.qos = cls.current_settings["QoS"]
                    else:
                        cls.qos = int(cls.current_settings["QoS"])
                else:
                    if cls.current_settings["QoS"] == 'None':
                        cls.qos = cls.current_settings["QoS"]
                    else:
                        cls.qos = int(cls.current_settings["QoS"])

                cls.retain = eval(cls.current_settings["Retain"])
                cls.clean_session = eval(cls.current_settings["Clean Session"])
                cls.topic = cls.current_settings["Topic"]

                # Update The Current Configuration Display
                cls.update_view_conf(instance[0])

                instance[1].statusbar.showMessage("Current Configuration Has Been Successfully Loaded From Json File.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except FileNotFoundError as fnfe:
            instance[1].statusbar.showMessage("FileNotFoundError: {}".format(fnfe))
        except FileExistsError as fee:
            instance[1].statusbar.showMessage("FileExistsError: {}".format(fee))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def save_settings_to_json(cls, instance):

        """ Data Serialization - A Method designed to save current configuration into a json file.

         Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.

         Parameters:
             file (tuple): Stores json file's full path & a string.
             f (TextIOWrapper): File Object.
             cls.current_settings (dict): Update the Current Configuration Dictionary Value.

         Returns:
             None
        """

        try:
            file = QFileDialog.getSaveFileName(instance[0], 'Create json File For Saving Current Settings',
                                                     "current_settings" + datetime.now().strftime("_%d_%m_%y_%H_%M"),
                                                     "json file (*.json)")

            with open(file[0], 'w') as f:
                json.dump(cls.current_settings, f)

            instance[1].statusbar.showMessage("Current Configuration Has Been Successfully Saved To Json File.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except FileNotFoundError as fnfe:
            instance[1].statusbar.showMessage("FileNotFoundError: {}".format(fnfe))
        except FileExistsError as fee:
            instance[1].statusbar.showMessage("FileExistsError: {}".format(fee))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    def update_view_conf(self):
        
        """
        Update the Current Configuration Value & UI Display.

        Args:
            None.

        Parameters:
            self.broker_ip_display_box, self.port_display_box, self.topic_display_box, self.username_display_box,
            self.password_display_box, self.unique_client_id_display_box, self.clean_session_display_box,
            self.retain_display_box, self.qos_display_box.clear (QTextBrowser): Displays Class Variables Current Value.

        Returns:
            None.
        """
        try:
            self.broker_ip_display_box.clear()
            self.broker_ip_display_box.append("<center>{}".format(ConfigurationWidget.broker_ip))
    
            self.port_display_box.clear()
            self.port_display_box.append("<center>{}".format(ConfigurationWidget.port))
    
            self.topic_display_box.clear()
            self.topic_display_box.append("<center>{}".format(ConfigurationWidget.topic))
    
            self.username_display_box.clear()
            self.username_display_box.append("<center>{}".format(ConfigurationWidget.username))
    
            self.password_display_box.clear()
            self.password_display_box.append("<center>{}".format(ConfigurationWidget.password))
    
            self.unique_client_id_display_box.clear()
            self.unique_client_id_display_box.append("<center>{}".format(ConfigurationWidget.client_id))
    
            self.clean_session_display_box.clear()
            self.clean_session_display_box.append("<center>{}".format(ConfigurationWidget.clean_session))
    
            self.retain_display_box.clear()
            self.retain_display_box.append("<center>{}".format(ConfigurationWidget.retain))
    
            self.qos_display_box.clear()
            self.qos_display_box.append("<center>{}".format(ConfigurationWidget.qos))
        
        except Exception as e:
            print("Error: {}".format(e))

    @classmethod
    def reset_settings_to_none(cls, instance):

        try:
            cls.broker_ip = 'None'
            cls.port = 'None'
            cls.username = 'None'
            cls.password = 'None'
            cls.topic = 'None'
            cls.clean_session = 'None'
            cls.retain = 'None'
            cls.qos = 'None'
            cls.client_id = 'None'

            instance[0].update_view_conf()

            instance[1].statusbar.showMessage("Current Configuration Has Been Successfully Reset!.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))


class ClientGuiWidget(QWidget):

    """ ClientGuiWidget Class for initializing the Client Tab.

    The user interface has many capabilities that enable ease of use and provide user experience.

    Attributes:
        message_sent (str): Stores the message to publish.
        message_received (str): Stores the message which received from subscribing topic.
        topic (str): Stores the topic for subscribe.
        client (NoneType): Stores the mqtt-client object.
            
        self.banner, self.publish_logo, self.subscribe_logo, self.mqtt_client_status_img (QLabel): Images/Logos Widgets.
        self.minimize_to_tray_btn, self.connect_btn, self.disconnect_btn, self.set_message_btn, self.set_topic_btn,
            self.publish_btn, self.subscribe_btn, self.publish_delete_msg_btn,
            self.subscribe_delete_msg_btn (QPushButton): Buttons Widgets.
        self.message_insert_line, self.topic_insert_line(QLineEdit): Insert Line Widgets.
        self.status_display_box, self.message_display_box, self.received_message_display_box (QTextBrowser): Display Box
            to show current Value.
        self.main_layout (QVBoxLayout): Creating the Main Layout to contain all the sub layouts
        banner, status_frame, sub_logos, set_message_frame, display_message_frame, publish_frame (QHBoxLayout): Add
            Widgets to sub frames.

    Methods:
        super(ClientGuiWidget, self).__init__(parent): ClientGuiWidget & App constructor.
        App.create_label, App.create_line, App.create_button, App.create_text_browser, App.create_combo_box: Using App's
                                                            Class Methods to build Models in the UI.
        add_widget_to_frame(self, widget_list): Adding the a sub frame list of created widgets.
        set_message(cls, instance): Sets the message to publish.
        set_topic(cls, instance): Sets the subscribing topic.
        client_connect(cls, instance): A method for creating mqtt-client, connect to a broker, update the client current
        status.
        client_disconnect(cls, instance): A method  for disconnect the mqtt-client & update the client current status.
        message_publish(cls, instance): A method to publish a message via mqtt-client.
        topic_subscribe(cls, instance): A method to subscribe mqtt-client to a topic and update the display box.
        clear_publish_display_box(self): Clear the sent messages ( publish mode) inside the display box.
        clear_subscribe_display_box(self): Clear the received messages ( subscribe mode ) inside the display box.

        on_connect(client, userdata, flags, rc), on_disconnect(client, userdata, flags, rc=0),
            on_message(client, userdata, msg): Overding Methods to perform actions when the mqtt-client connect,
            disconnect, subscribe to a topic etc.


    """

    message_sent = None
    topic = None
    qos = None
    client = None
    message_received = None

    def __init__(self, parent=None, app=None):

        super(ClientGuiWidget, self).__init__(parent)

        self.setAutoFillBackground(True)

        # Banner/Logos
        self.banner = App.create_label(parent, 500, 100, 'images/banner4.png')
        self.publish_logo = App.create_label(parent, 400, 60, 'images/client_gui_tab/client_publish.png')
        self.subscribe_logo = App.create_label(parent, 400, 60, 'images/client_gui_tab/client_subscribe.png')

        # Images
        self.mqtt_client_status_img = App.create_label(parent, 350, 60, 'images/client_gui_tab/client_status.png')

        # Buttons
        self.minimize_to_tray_btn = App.create_button(parent, 197, 38, 'images/minimize_to_tray_img.png',
                                                      app.hide)

        self.connect_btn = App.create_button(parent, 200, 38, 'images/client_gui_tab/connect.png',
                                                self.client_connect, [parent, self, app])
        self.disconnect_btn = App.create_button(parent, 200, 40, 'images/client_gui_tab/disconnect.png',
                                                self.client_disconnect, [parent, self])
        self.set_message_btn = App.create_button(parent, 200, 38, 'images/client_gui_tab/set_message_img.png',
                                                self.set_message, [self,app])
        self.set_topic_btn = App.create_button(parent, 200, 38, 'images/client_gui_tab/set_topic_img.png',
                                                self.set_topic, [self,app])
        self.publish_btn = App.create_button(parent, 200, 38, 'images/client_gui_tab/publish_img.png',
                                                self.message_publish, [parent, self, app])
        self.subscribe_btn = App.create_button(parent, 200, 38, 'images/client_gui_tab/subscribe_img.png',
                                                self.topic_subscribe, [parent, self, app])
        self.publish_delete_msg_btn = App.create_button(parent, 200, 38, 'images/client_gui_tab/delete_messages_img.png',
                                                self.clear_publish_display_box)
        self.subscribe_delete_msg_btn = App.create_button(parent, 200, 38, 'images/client_gui_tab/delete_messages_img.png',
                                                self.clear_subscribe_display_box)

        # Insert Lines
        self.message_insert_line = App.create_line(parent, 342, 35, 15, "Enter Message")
        self.topic_insert_line = App.create_line(parent, 292, 35, 15, "Enter Topic")

        # Display Boxes
        self.status_display_box = App.create_text_browser(parent, 200, 40, "font-size: 15px;")
        self.status_display_box.append("<center>Disconnected")
        self.status_display_box.setStyleSheet("background-color: red;color: #ffffff; font: bold 20px;"
                                              " border: 3px solid #000000;border-radius: 20px 20px 25px 25px;")
        self.message_display_box = App.create_text_browser(parent, 550, 240, "font-size: 15px;")
        self.received_message_display_box = App.create_text_browser(parent, 550, 240, "font-size: 15px;")

        # Combo Box
        self.qos_combo_box = App.create_combo_box(parent, ["QoS", "0", "1", "2"], ClientGuiWidget.set_qos,
                                                  [self, app])

        # Creating the Main Layout to contain all the sub layouts
        self.main_layout = QVBoxLayout(self)

        # Add Widges to sub frames
        banner = self.add_widget_to_frame([self.minimize_to_tray_btn, QLabel(""), self.banner,QLabel(""),  QLabel("")])

        status_frame = self.add_widget_to_frame([QLabel(""), self.connect_btn, self.disconnect_btn,
                                                 self.mqtt_client_status_img, self.status_display_box, QLabel("")])
        sub_logos = self.add_widget_to_frame([QLabel(""), self.publish_logo, QLabel(""), self.subscribe_logo, QLabel("")])
        set_message_frame = self.add_widget_to_frame([QLabel(""), self.message_insert_line, self.set_message_btn,
                                                       QLabel(""), self.topic_insert_line, self.set_topic_btn,
                                                      self.qos_combo_box, QLabel("")])

        display_message_frame = self.add_widget_to_frame([QLabel(""), self.message_display_box, QLabel(""),
                                                          self.received_message_display_box, QLabel("")])
        publish_frame = self.add_widget_to_frame([QLabel(""), self.publish_btn, self.publish_delete_msg_btn,QLabel(""), QLabel(""),
                                                  self.subscribe_btn, self.subscribe_delete_msg_btn, QLabel("")])

        self.main_layout.addStretch()

    def add_widget_to_frame(self, widget_list):

        """
        Add Created Widgets from a list to a Sub Frame.
        After it, add the sub frame to the main frame.

        Args:
            widget_list (list): A list which stored the widgets to add into the sub frame.

        Parameters:
            temp_frame (QHBoxLayout): A temporary frame to stored widgets.
            self.main_layout(QVBoxLayot): Main frame to stores sub frame/layouts.

        Returns:
            temp_frame (QHBoxLayout): A temporary frame to stored widgets.
        """

        try:
            temp_frame = QHBoxLayout()

            for item in widget_list:
                temp_frame.addWidget(item)

            self.main_layout.addLayout(temp_frame)

            return temp_frame

        except Exception as e:
            print("Couldn't Set The Sub Frame: {}".format(e))

    @classmethod
    def set_message(cls, instance):

        """
        Set The Message To Publish (Class Variable).

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.

        Parameters:
            cls.message_sent (str): Stores a string of the message to publish.

        Returns:
            None.
        """

        try:
            # Set Value
            cls.message_sent = instance[0].message_insert_line.text()

            instance[1].statusbar.showMessage("Message To Send Has Been Successfully Configured.")

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def set_topic(cls, instance):

        """
        Set The Topic To Subscribe (Class Variable).

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.

        Parameters:
            cls.topic (str): Stores a string of the topic to subscribe.

        Returns:
            None.
        """

        try:
            cls.topic = instance[0].topic_insert_line.text()

            instance[1].statusbar.showMessage("Subscribe Topic '{}' Has Been Successfully Configured.".format(cls.topic))

        except ValueError as ve:
            instance[1].statusbar.showMessage("ValueError: {}".format(ve))
        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def set_qos(cls, text, instance):

        """
        Set The QoS Option Class Variable.
        Update the Current Configuration Value & UI Display.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar.
            text (str): String which has the broker ip.

        Parameters:
            cls.qos (int): Stores the QoS Option Value.
            cls.current_settings (dict): Update the Current Configuration Dictionary Value.

        Returns:
            None.
        """

        try:
            if text is not "QoS":

                # Set Value
                cls.qos = int(text)

                instance[1].statusbar.showMessage("Subscribe QoS of '{}' Has Been Successfully Configured.".format(cls.qos))

        except Exception as e:
            instance[1].statusbar.showMessage("Error: {}".format(e))

    @classmethod
    def client_connect(cls, instance):

        """
        Method to connect mqtt-client to a broker.
        Creates a flag inside mqtt-client to show the client connection's indication.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar. instance[0] = ConfigurationWidget, instance[1] = ClientGuiWidget , instance[2] = App.

        Parameters:
            cls.client (Client): Mqtt-client object.
            mqtt.Client (paho.mqtt.client.Client): Using MQTT Python client library

        Returns:
            None.
        """

        try:

            if cls.client is None:

                # Add Connection Status Flag.
                mqtt.Client.connected_flag = False
                # Object to store the received message.
                mqtt.Client.message_received = None
                # Create a flag for subscribe mode
                mqtt.Client.subscribe_status = False

                # Creates mqtt-client & sent instances for future actions.
                cls.client = mqtt.Client(instance[0].client_id, clean_session=instance[0].clean_session,
                                         userdata=instance)
                cls.client.username_pw_set(username=instance[0].username, password=instance[0].password)

                # Overiding Functions
                cls.client.on_connect = cls.on_connect
                cls.client.on_disconnect = cls.on_disconnect
                cls.client.on_message = cls.on_message
                cls.client.on_subscribe = cls.on_subscribe

            if cls.client.connected_flag is False:
                # Connect the mqtt-client to the broker
                cls.client.connect(instance[0].broker_ip, instance[0].port)
                print("Connecting to broker {}... ".format(instance[0].broker_ip))

                cls.client.loop_start()
                time.sleep(0.5)
                cls.client.loop_stop()

            if cls.client.connected_flag is True:
                instance[2].statusbar.showMessage("Mqtt Client Has Been Connected successfully!")
                instance[1].status_display_box.clear()
                instance[1].status_display_box.append("<center>Connected")
                instance[1].status_display_box.setStyleSheet("background-color: green;color: #ffffff; font: bold 20px;"
                                                             "border: 3px solid #000000;"
                                                             "border-radius: 20px 20px 25px 25px;")
            else:
                raise Exception("Mqtt Client Couldn't Connect!")

        except Exception as e:
            instance[2].statusbar.showMessage("Error Has Occurred: {}".format(e))

    @classmethod
    def client_disconnect(cls, instance):

        """
        Method to disconnect mqtt-client from the broker.
        Disconnect mqtt-client, update the mqtt-client connection's flag to False by using overrided function
        on_dissconnect and update the current client status display box.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar. instance[0] = ConfigurationWidget, instance[1] = ClientGuiWidget , instance[2] = App.

        Parameters:
            cls.client (Client): Mqtt-client object.

        Returns:
            None.
        """

        try:
            cls.client.disconnect()

            instance[1].status_display_box.clear()
            instance[1].status_display_box.append("<center>Disconnected")
            instance[1].status_display_box.setStyleSheet("background-color: red;color: #ffffff; font: bold 20px;"
                                                         "border: 3px solid black;border-radius: 20px 20px 25px 25px;")
        except Exception as e:
            instance[2].statusbar.showMessage("Error Has Occurred: {}".format(e))

    @classmethod
    def message_publish(cls, instance):


        """
        Method to publish a message via mqtt-client with a specific topic.
        Whether the mqtt-client is connected - publish the message.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar. instance[0] = ConfigurationWidget, instance[1] = ClientGuiWidget , instance[2] = App.

        Parameters:
            cls.client (Client): Mqtt-client object.

        Returns:
            None.
        """

        try:

            if cls.client.connected_flag is True:
                if cls.message_sent is not None:
                    cls.client.publish(instance[0].topic, cls.message_sent, instance[0].qos, instance[0].retain)

                    time_date = datetime.now().strftime("%H:%M:%S %d/%m/%y")

                    instance[1].message_display_box.append("Sent:  {}  to: {} at: {}".format(cls.message_sent,
                                                           instance[0].topic, time_date))
                    print("Mqtt Client Publish -  Sent:  {}  to: {} at: {}".format(cls.message_sent, instance[0].topic,
                                                                                   time_date))
                else:
                    raise UserWarning("You Didn't Set a Message to Send.")
            else:
                raise UserWarning("You Are Disconnected!")

        except UserWarning as uw:
            instance[2].statusbar.showMessage("UserWarning: {}".format(uw))
        except Exception as e:
            instance[2].statusbar.showMessage("Error Has Occurred: {}".format(e))

    @classmethod
    def topic_subscribe(cls, instance):

        """
        Method to use mqtt-client for subscribing to a topic.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar. instance[0] = ConfigurationWidget, instance[1] = ClientGuiWidget , instance[2] = App.

        Parameters:
            cls.client (Client): Mqtt-client object.

        Returns:
            None.
        """

        try:

            if cls.client.connected_flag is True:
                if cls.client.subscribe_status is False:
                    if cls.topic is not None and cls.qos is not None:
                        # Update Subscribe Status Flag
                        cls.client.subscribe_status = True

                        # Start the loop
                        cls.client.loop_start()
                        cls.client.subscribe(cls.topic, cls.qos)
                        time.sleep(0.1)
                    else:
                        raise UserWarning("You Didn't Set a Topic or QoS For Subscribing.")
                else:
                    raise UserWarning("You Already In Subscribe Mode")
            else:
                raise UserWarning("You Are Disconnected!")

        except UserWarning as uw:
            instance[2].statusbar.showMessage("UserWarning: {}".format(uw))

        except Exception as e:
            instance[2].statusbar.showMessage("Error Has Occurred: {}".format(e))

    def clear_publish_display_box(self):

        """
        Method to clean Published Messages inside Display Box.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar. instance[0] = ConfigurationWidget, instance[1] = ClientGuiWidget , instance[2] = App.

        Parameters:
            cls.message_display_box (QTextBrowser): Display box of the messages which published.

        Returns:
            None.
        """

        try:
            self.message_display_box.clear()
        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def clear_subscribe_display_box(self):

        """
        Method to clean Received Messages inside Display Box.

        Args:
            instance (list): List of Instances which let us get the text from the insert line & Update
            the status bar. instance[0] = ConfigurationWidget, instance[1] = ClientGuiWidget , instance[2] = App.

        Parameters:
            cls.received_message_display_box (QTextBrowser): Display box of the messages which received.

        Returns:
            None.
        """

        try:
            self.received_message_display_box.clear()
        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    @staticmethod
    def on_connect(client, userdata, flags, rc):

        """
        Overriding Method which called on client connect.

        Args:
            client (Client): the client instance for this callback
            userdata (list): the private user data.
            flags (dict): response flags sent by the broker
            rc (int): the disconnection result

        Parameters:
            None.

        Returns:
            None.
        """

        try:
            if rc == 0:
                print("Mqtt Client Has Been Connected successfully!")
                client.connected_flag = True

            else:
                print("Mqtt Client Has Bad Connection Returned code=", rc)
                client.bad_connection_flag = True

        except Exception as e:
            userdata[2].statusbar.showMessage("Error Has Occurred: {}".format(e))

    @staticmethod
    def on_disconnect(client, userdata, flags, rc=0):

        """
        Overriding Method which called on client disconnect.

        Args:
            client (Client): the client instance for this callback
            userdata (list): the private user data.
            flags (dict): response flags sent by the broker
            rc (int): the disconnection result

        Parameters:
            None.

        Returns:
            None.
        """

        try:
            client.connected_flag = False
            client.subscribe_status = False
            print("Mqtt Client Has Been Disconnected successfully With Result Code: {} ".format(str(rc)))
            userdata[2].statusbar.showMessage("Mqtt Client Has Been Disconnected successfully With Result Code: {} ".
                                              format(str(rc)))

        except Exception as e:
            userdata[2].statusbar.showMessage("Error Has Occurred: {}".format(e))

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):

        """
        Overriding Method which called on client subscribe to topic.

        Args:
            client (Client): the client instance for this callback
            userdata (list): the private user data.
            mid (dict): message id.
            granted_qos(int): qos value.

        Parameters:
            None.

        Returns:
            Non
        """

        print("Subscribed to: '{}' with Granted QoS: '{}'".format(userdata[1].topic, granted_qos[0]))

    @staticmethod
    def on_message(client, userdata, msg):

        """
        Overiding Method which called on client disconnect.

        Args:
            client (Client): the client instance for this callback
            userdata (list): the private user data.
            msg (MQTTMessage): Containes the topic & message which sent.

        Parameters:
            m_decode (str): The message string.
            time_date (str): A string of the current time & date
        Returns:
            None.
        """

        try:
            topic = msg.topic
            m_decode = str(msg.payload.decode("utf-8", "ignore"))
            userdata[0].message_received = m_decode

            time_date = datetime.now().strftime("%H:%M:%S %d/%m/%y")

            userdata[1].received_message_display_box.append("Received: {} from: {} at: {}".format(m_decode, topic, time_date))
            print(("Mqtt Client Subsribe - Received: {} from: {} at: {}".format(m_decode, topic, time_date)))

            userdata[1].automation_action(m_decode)

        except Exception as e:
            userdata[2].statusbar.showMessage("Error Has Occurred: {}".format(e))

    @staticmethod
    def automation_action(action):

        """
        A method to perform automation when received known message.

        Args:
            action (str): The message/action string.

        Parameters:
            returned_value (str): Return value from shell command.

        Returns:
            None.
        """

        if action == "ping":
            os.system("start /wait cmd /c ping -t 8.8.8.8")
        elif action == "chrome":
            subprocess.call(['C:\Program Files (x86)\Google\Chrome\Application\\chrome.exe'])
        elif action == "lock":
            os.system("start /wait cmd /c rundll32.exe user32.dll, LockWorkStation")
        elif action == "shutdown":
            os.system("start /wait cmd /c shutdown /s /t 0")
            # os.system("start /wait cmd /c rundll32.exe user32.dll, ExitWindowsEx")
        elif action == "getmac":
            returned_value = subprocess.call("getmac", shell=True)
            print(returned_value)
        elif action == "arp":
            returned_value = subprocess.call("arp -a", shell=True)
            print(returned_value)
        else:
            print("No Automation for this message.")


class MainWindow(QWidget):

    """ MainWindow Class for initializing the Main Window of the UI.

      Attributes:
          title (str): Windows Application's title.
          icon (str):  Stores the icon image's path.
          left, top, width, height (int): Windows Application's Size & Screen positioning.
          tray (QSystemTrayIcon): Application's icon tray with menu ability for show, hide & exit.
          statusbar (statusBar): Status bar of the UI which shows operations's status after execution.

      Methods:
          super(MainWindow, self).__init__(parent) MainWinodw & App constructor.
    """

    def __init__(self, parent):

        super(MainWindow, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        # Initialize tabs
        self.tab_holder = QTabWidget()   # Create tab holder

        icon1 = QIcon()
        icon1.addPixmap(QPixmap("images/conf_tab/settings.png"), QIcon.Normal, QIcon.Off)

        icon2 = QIcon()
        icon2.addPixmap(QPixmap("images/client_gui_tab/publish_icon.png"), QIcon.Normal, QIcon.Off)

        tab_1 = ConfigurationWidget(parent)
        tab_2 = ClientGuiWidget(tab_1, parent)
        self.tab_holder.addTab(tab_1, icon1, "Configuration")
        self.tab_holder.addTab(tab_2, icon2,  "Client GUI")

        self.layout.addWidget(self.tab_holder)


def main():

    app = QApplication(sys.argv)
    instance = App()
    sys.exit(app.exec_())
