import sys
import random
import json

from datetime import datetime

from PyQt5.QtCore import QSize
from PyQt5.QtGui import (QIcon, QPixmap, QImage, QPalette, QBrush)
from PyQt5.QtWidgets import (QTextBrowser, QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QMessageBox,
                             QAction, QFileDialog, QVBoxLayout, QComboBox, QStyleFactory)

import paho.mqtt.client as mqtt


class App(QMainWindow):

    """ App Class for initializing the UI and its abilities.

    The user interface has many capabilities that enable ease of use and provide user experience.

    TODO:
     - Extra Documentation of App Class ( Attributes & Methods )
     - Validation of Inputs
     - Code Optimization
     - Change Setters Methods

    Attributes:
        __title (str): Windows Application's title.
        __icon (str):  Stores the icon image's path.
        __left, __top, __width, __height (int): Windows Application's Size & Screen positioning.

    Methods:
        super().__init__(): QMainWindow Base Class __init__ constructor.

    """

    def __init__(self):

        """Initializing App Class"""

        super().__init__()
        self.__title = 'MQTT Client Desktop Application'
        self.__icon = 'images/mqtt.ico'
        self.__left = 50
        self.__top = 35
        self.__width = 1280
        self.__height = 680

        self.__broker_ip = 'None'
        self.__port = 'None'
        self.__username = 'None'
        self.__password = 'None'
        self.__qos = 'None'
        self.__retain = 'None'
        self.__clean_session = 'None'
        self.__topic = 'None'

        self.__current_settings = {"Broker IP": self.__broker_ip,
                                   "Port": self.__port,
                                   "Username": self.__username,
                                   "Password": self.__password,
                                   "QoS": self.__qos,
                                   "Retain": self.__retain,
                                   "Clean Session": self.__clean_session,
                                   "Topic": self.__topic}
        self.__client_id = None

        self.__current_settings_table = self.__create_text_browser(50, 150, 300, 216, "font-size: 16px;")
        self.__statusbar_table = self.__create_text_browser(250, 585, 800, 50, "font-size: 30px;")

        self.__init_ui()

    def __load_settings_from_json(self):

        """  Data Serialization - A Method designed to load hashtags list from a json file.

        Args:
           No Args

        Parameters:
             self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
             self.__hashtag_table (QTextBrowser): Displays the hashtag list at the Top Left of UI.
             self.__tag_list (dictionary): Dictionary to store the user tags.
             file (QFileDialog) = An object that handles the json file.

        Returns:
            None
        """

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:
            file = QFileDialog.getOpenFileName(self, 'Open json File For Loading Settings', "",
                                               "json file (*.json)")

            # Open the json file and load the hashtags
            with open(file[0], 'r') as f:

                self.__current_settings = json.load(f)
                print(self.__current_settings)

                self.__set_broker_ip = self.__current_settings["Broker IP"]
                self.__set_port = self.__current_settings["Port"]
                self.__set_username = self.__current_settings["Username"]
                self.__set_password = self.__current_settings["Password"]
                self.__set_qos = self.__current_settings["QoS"]
                self.__set_retain = self.__current_settings["Retain"]
                self.__set_clean_session = self.__current_settings["Clean Session"]
                self.__set_topic = self.__current_settings["Topic"]

                # Clear the Status bar
                self.__statusbar_table.clear()

                self.__update_current_settings_display()
            # Check validity of the data inside the json file - a list, empty dict or wrong input.

        except FileNotFoundError as fnfe:
            self.__statusbar_table.append("<center>File Not Found Error: {}".format(fnfe))
        except FileExistsError as fee:
            self.__statusbar_table.append("<center>File Exist Error: {}".format(fee))
        except Exception as e:
            self.__statusbar_table.append("<center>Error with Open File: {}".format(e))
        else:
            self.__statusbar_table.append("<center>Settings Has Been Successfully Loaded!")

    def __save_settings_to_json(self):

        """ Data Serialization - A Method designed to save hashtags list into a json file.

        Args:
           No Args

        Parameters:
             self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
             self.__hashtag_table (QTextBrowser): Displays the hashtag list at the Top Left of UI.
             self.__tag_list (dictionary): Dictionary to store the user tags.
             file (QFileDialog) = An object that handles the json file.

        Returns:
            None
        """

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:

                file = QFileDialog.getSaveFileName(self, 'Create json File For Saving Current Settings',
                                                   "current_settings" + datetime.now().strftime("_%d_%m_%y_%H_%M"),
                                                   "json file (*.json)")

                with open(file[0], 'w') as f:
                    #settings_serialization = self.__current_settings
                    json.dump(self.__current_settings, f, sort_keys=True)

        except FileNotFoundError as fnfe:
            self.__statusbar_table.append("<center>File Not Found Error: {}".format(fnfe))
        except FileExistsError as fee:
            self.__statusbar_table.append("<center>File Exist Error: {}".format(fee))
        except Exception as e:
            self.__statusbar_table.append("<center>Save File Error: {}".format(e))
        else:
            self.__statusbar_table.append("<center>Settings Successfully Saved!")

    def __generate_client_id(self):

        chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
        pass_len = 8

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:
            self.__uniqut_client_id_display_box.clear()
            self.__client_id = "client_" + "".join(random.sample(chars, pass_len))
            self.__uniqut_client_id_display_box.append(self.__client_id)

            self.__statusbar_table.append("<center>Unique Client ID Has Been Successfully Generated!")

        except Exception as e:
            self.__statusbar_table.append("<center>File Not Found Error: {}".format(e))

    def __create_button(self, width, height, top, left, image, func):

        """  Generic Pattern For Create Button

        Args:
           width, height, top, left (int): Size & Position of the button.
           image (str): Path of the background image.
           func (method): The function which be executed when the button clicked.
           text=None (str): A Text string for copyright button.

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
            btn.move(top, left)

            # Sets Button's Image
            btn_image = QPixmap(image)
            btn.setIcon(QIcon(btn_image))
            btn.setIconSize(QSize(200, 200))

            # Attach Function to a Button according to func & text arguments
            #if text:
            #    btn.clicked.connect(lambda checked: self.__copyrights_btn_links(text))
            #else:
            btn.clicked.connect(func)

            return btn

        except Exception as e:
            # Clear the Status bar
            self.__statusbar_table.clear()
            self.__statusbar_table.append("<center>Error Has Occurred: {}".format(e))

    def __create_line(self, width, height, top, left, size, text):

        """   Pattern For Create Line

        Args:
           width, height, top, left (int): Size & Position of the line.
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
            line.resize(width, height)
            line.move(top, left)

            # Sets Line's Default Text
            line.setPlaceholderText(text)

            # Sets Text's Size
            line.setStyleSheet("font-size: {}px;".format(size))

            return line

        except Exception as e:
            # Clear the Status bar
            self.__statusbar_table.clear()
            self.__statusbar_table.append("<center>Error Has Occurred: {}".format(e))

    def __create_text_browser(self, left, top, width, height, text_size):

        """   Pattern For Create Text Browser

        Args:
           left, top, width, height (int): Size & Position of the Text Broswer.
           text_size (str): An integer to determine the size of the text.

        Parameters:
            text_browser (QTextBrowser): The Text Browser with all the properties set.

        Returns:
            text_browser (QTextBrowser): The Text Browser with all the properties set.

        """

        try:

            text_browser = QTextBrowser(self)
            text_browser.setGeometry(left, top, width, height)
            text_browser.setStyleSheet(text_size)

            return text_browser

        except Exception as e:
            # Clear the Status bar
            self.__statusbar_table.clear()
            self.__statusbar_table.append("<center>Error Has Occurred: {}".format(e))

    def __create_label(self, left, top, width, height, img_path):

        """   Pattern For Create Text Browser

        Args:
           left, top, width, height (int): Size & Position of the Text Broswer.
           img_path (str): A text string to for image path.

        Parameters:
            label (QLineEdit): The label with all the properties set.

        Returns:
            label (QTextBrowser): The label with all the properties set.

        """

        try:

            label = QLabel(self)

            # Load Image & Resize it
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaled(QSize(width, height))

            # Set Image & Its Position
            label.setPixmap(pixmap)
            label.setGeometry(left, top, width, height)

            return label

        except Exception as e:
            # Clear the Status bar
            self.__statusbar_table.clear()
            self.__statusbar_table.append("<center>Error Has Occurred: {}".format(e))

    def __create_combo_box(self, left, top, option_list, func):

        try:

            combo_box = QComboBox(self)

            for item in option_list:
                combo_box.addItem(item)

            combo_box.move(left, top)

            combo_box.activated[str].connect(func)

            return combo_box

        except Exception as e:
            # Clear the Status bar
            self.__statusbar_table.clear()
            self.__statusbar_table.append("<center>Error Has Occurred: {}".format(e))

    def __set_main_window_conf(self, width, height, brush_size, img_path):

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
            self.setWindowIcon(QIcon(self.__icon))
            self.setWindowTitle(self.__title)
            self.setGeometry(self.__left, self.__top, self.__width, self.__height)

            bg_image = QImage(img_path)
            bg_image = bg_image.scaled(QSize(width-150, height-300))  # resize Image to widgets size

            # Sets the background image at the Main window App
            palette = QPalette()
            palette.setBrush(brush_size, QBrush(bg_image))  # 10 = Windowrole
            self.setPalette(palette)

        except Exception as e:
            # Clear the Status bar
            #self.__statusbar_table.clear()
            print("Couldn't Set The Main Window Configuration Because: {}".format(e))

    def __set_broker_ip(self, text=None):

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:
            if text is False:
                self.__broker_ip = self.__broker_ip_insert_line.text()
                self.__current_settings["Broker IP"] = self.__broker_ip
            else:
                self.__broker_ip = text

            self.__update_current_settings_display()

            self.__statusbar_table.append("<center>Broker IP Has Been Successfully Configured")

        except ValueError as ve:
            self.__statusbar_table.append("<center>Broker IP ValueError Configuration: {}".format(ve))
        except Exception as e:
            self.__statusbar_table.append("<center>Couldn't Set Broker IP Because: {}".format(e))

    def __set_port(self, text=None):

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:
            if text is 'None':
                self.__port =int(self.__port_insert_line.text())
            else:
                self.__port = text

            self.__current_settings["Port"] = str(self.__port)
            self.__update_current_settings_display()

            self.__statusbar_table.append("Broker Port Has Been Successfully Configured")

        except ValueError as ve:
            self.__statusbar_table.append("<center>Broker Port ValueError Configuration: {}".format(ve))
        except Exception as e:
            self.__statusbar_table.append("<center>Couldn't Set Broker Port Because: {}".format(e))

    def __set_username(self, text=None):

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:
            if text is 'None':
                self.__username = self.__username_insert_line.text()
                self.__current_settings["Username"] = self.__username
            else:
               self.__username = text

            self.__update_current_settings_display()

            self.__statusbar_table.append("Username Has Been Successfully Configured")

        except ValueError as ve:
            self.__statusbar_table.append("<center>Username ValueError Configuration: {}".format(ve))
        except Exception as e:
            # Clear the Status bar
            self.__statusbar_table.clear()
            self.__statusbar_table.append("<center>Couldn't Set The Username Because: {}".format(e))

    def __set_password(self, text=None):

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:

            if text is 'None':
                self.__password = self.__password_insert_line.text()
                self.__current_settings["Password"] = self.__password
            else:
                self.__password = text

            self.__update_current_settings_display()

            self.__statusbar_table.append("Password Has Been Successfully Configured")

        except ValueError as ve:
            self.__statusbar_table.append("<center>Password ValueError Configuration: {}".format(ve))
        except Exception as e:
            self.__statusbar_table.append("<center>Couldn't Set Username Because: {}".format(e))

    def __set_qos(self, text):

        # Clear Status Bar
        self.__statusbar_table.clear()

        try:

            self.__qos = int(text)
            self.__current_settings["QoS"] = text

            self.__statusbar_table.append('<center>QoS Has Been Set to: {}!'.format(text))

            self.__update_current_settings_display()

        except ValueError as ve:
            self.__statusbar_table.append('<center>ValueError: {}'.format(ve))
        except Exception as e:
            self.__statusbar_table.append('<center>Error Has Occurred: {}'.format(e))

    def __set_retain(self, text):

        # Clear Status Bar
        self.__statusbar_table.clear()

        try:

            if text != "Retain":
                self.__retain = eval(text)
                self.__current_settings["Retain"] = text

                self.__update_current_settings_display()

                self.__statusbar_table.append('<center>Retain Has Been Set to: {}!'.format(text))
            else:
                raise ValueError("Combo Box Title Can't Be Assigned.")

        except ValueError as ve:
            self.__statusbar_table.append('<center>ValueError: {}'.format(ve))
        except Exception as e:
            self.__statusbar_table.append('<center>Error Has Occurred: {}'.format(e))

    def __set_clean_session(self, text):

        # Clear Status Bar
        self.__statusbar_table.clear()

        try:

            if text != "Clean Session":
                self.__clean_session = eval(text)

                self.__current_settings["Clean Session"] = text

                self.__update_current_settings_display()

                self.__statusbar_table.append('<center>Clean Session Option Has Been Set to: {}!'.format(text))
            else:
                raise ValueError("Combo Box Title Can't Be Assigned.")

        except ValueError as ve:
            self.__statusbar_table.append('<center>ValueError: {}'.format(ve))
        except Exception as e:
            self.__statusbar_table.append('<center>Error Has Occurred: {}'.format(e))

    def __set_topic(self, text=None):

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:

            if text is 'None':
                self.__topic = self.__topic_insert_line.text()
                self.__current_settings["Topic"] = self.__topic
            else:
                self.__topic = text

            self.__update_current_settings_display()

            self.__statusbar_table.append("<center>Topic Has Been Successfully Configured")

        except ValueError as ve:
            self.__statusbar_table.append("<center>Topic ValueError Configuration: {}".format(ve))
        except Exception as e:
            self.__statusbar_table.append("<center>Couldn't Set The Topic Because: {}".format(e))

    def __set_message(self):

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:
            self.__message = self.__message_insert_line.text()

            self.__statusbar_table.append("<center>Message Has Been Successfully Configured")

        except ValueError as ve:
            self.__statusbar_table.append("<center>Message ValueError Configuration: {}".format(ve))
        except Exception as e:
            self.__statusbar_table.append("<center>Couldn't Set The Message to send Because: {}".format(e))

    def __message_publish(self):

        #self.__broker_ip = "139.162.222.115"
        #self.__username = "MATZI"
        #self.__password = "MATZI"
        #self.__topic = "matzi/iot/naty"
        #self.__message = "Naty Test"
        #self.__port = 80
        print(self.__broker_ip,self.__port, self.__username, self.__password, self.__qos,self.__retain, self.__clean_session, self.__topic, self. __message)

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:

            self.__client = mqtt.Client(self.__client_id, clean_session=self.__clean_session)  # create new client instance
            self.__client.username_pw_set(username=self.__username, password=self.__password)

            self.__client.connect(self.__broker_ip, self.__port)

            self.__client.publish(self.__topic, self.__message, self.__qos, self.__retain)

            self.__statusbar_table.append("<center>Sent: '" + self.__message + "' to: '" + self.__topic + "'")

            self.__client.disconnect()

        except ValueError as ve:
            self.__statusbar_table.append("<center>ValueError: {}".format(ve))
        except Exception as e:
            self.__statusbar_table.append("<center>Error Has Occurred: {}".format(e))

    def __update_current_settings_display(self):

        try:

            self.__current_settings_table.clear()

            for key, value in self.__current_settings.items():
                self.__current_settings_table.append(key +": " + value)


        except Exception as e:
            self.__statusbar_table.append("<center>Error Has Occured: {}".format(e))

    def __init_ui(self):

        # Main Window Configurtaion
        self.__set_main_window_conf(1500, 1024, 10, "images/bg1.jpg")

        """ Top Frame """
        # Banner\Logo
        self.__label = self.__create_label(350, 20, 500, 100, 'images/banner4.png')

        self.__save_btn = self.__create_button(109, 34, 50, 50, 'images/save.png', self.__save_settings_to_json)
        self.__load_btn = self.__create_button(109, 34, 200, 50, 'images/load.png', self.__load_settings_from_json)
        """ 1st Frame """


        ''' Center '''
        # Broker IP
        self.__broker_ip_insert_line = self.__create_line(200, 40, 400, 150, 15, "Enter Broker IP")
        self.__broker_ip_set_btn = self.__create_button(200, 40, 610, 150, 'images/set_broker_ip.png', self.__set_broker_ip)

        # Port
        self.__port_insert_line = self.__create_line(200, 40, 400, 200, 15, "Enter Port")
        self.__port_set_btn = self.__create_button(200, 40, 610, 200, 'images/set_broker_port.png', self.__set_port)

        ''' Right Side '''
        # Username
        self.__username_insert_line = self.__create_line(200, 40, 840, 150, 15, "Enter Username")
        self.__username_set_btn = self.__create_button(200, 40, 1050, 150, 'images/set_username.png', self.__set_username)

        #Password
        self.__password_insert_line = self.__create_line(200, 40, 840, 200, 15, "Enter Password")
        self.__password_set_btn = self.__create_button(200, 40, 1050, 200, 'images/set_password.png', self.__set_password)


        """ 2nd Frame """

        ''' Left Side '''
        #Unique Client ID Via text browser
        self.__uniqut_client_id_display_box = self.__create_text_browser(400, 250, 200, 40, "font-size: 15px;")
        self.__generate_client_id_btn = self.__create_button(200, 40, 610, 250, 'images/generate_client_id.png',
                                                             self.__generate_client_id)

        """ Center & Right Side"""
        #QoS
        self.__qos_combo_box = self.__create_combo_box(840, 255, ["QoS", "0", "1", "2"], self.__set_qos)

        #Retain
        self.__retain_combo_box = self.__create_combo_box(1000, 255, ["Retain", "True", "False"], self.__set_retain)

        # Clean Session
        self.__clean_session_combo_box = self.__create_combo_box(1150, 255, ["Clean Session", "True", "False"],
                                                                 self.__set_clean_session)

        """ 3rd Frame """

        #Topic
        self.__topic_insert_line = self.__create_line(200, 40, 400, 325, 15, "Enter Topic")
        self.__topic_set_btn = self.__create_button(200, 40, 610, 325, 'images/set_topic.png', self.__set_topic)

        ''' Center '''
        #Message
        self.__message_insert_line = self.__create_line(200, 40, 840, 325, 15, "Enter Message")
        self.__message_set_btn = self.__create_button(200, 40, 1050, 325, 'images/set_message.png', self.__set_message)

        """ Bottom Frame"""

        #Publish
        self.__client_publish_btn = self.__create_button(200, 40, 550, 500, 'images/publish.png', self.__message_publish)

        self.__update_current_settings_display()

        # Display the UI
        self.show()

def main():
    app = QApplication(sys.argv)
    main_window = App()
    sys.exit(app.exec_())


