"""
en: Settings window for ics_gui.py
ru: Окно настроек для ics_gui.py
"""
import json

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QColorDialog, QInputDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal

from screeninfo import get_monitors


class SettingsWindow(QtWidgets.QWidget):
    """
    en: Settings window
    ru: Окно настроек
    """
    # en: variable for signal / ru: переменная для сигнала
    SignalToMain = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        # en: load ui file / ru: загрузка ui файла
        self.ui = uic.loadUi('ui/settings.ui', self)
        self.data = {}
        self.display = get_monitors()
        self.display_index = 0
        # en: read config file / ru: чтение файла конфигурации
        try:
            with open('config.json') as file:
                self.data = json.load(file)
        except FileNotFoundError or json.decoder.JSONDecodeError:
            self.default_data()
        # en: for status message to main window / ru: для статуса сообщения в главное окно
        self.exit_status = 0
        # en: set data to widgets / ru: установка данных в виджеты
        self.from_config()
        # en: choose settings page / ru: выбор страницы настроек
        self.listWidget.currentItemChanged.connect(self.change_page)
        # en: change colors / ru: изменение цветов
        self.pushButton_color_bg.clicked.connect(self.set_color_bg)
        self.pushButton_color_font.clicked.connect(self.set_color_font)
        self.pushButton_color_left.clicked.connect(self.set_color_left)
        self.pushButton_color_right.clicked.connect(self.set_color_right)
        self.fontComboBox.currentFontChanged.connect(self.set_current_font)
        # en: open subwindow for adding items for list / ru: открытие окна для добавления элементов в список
        self.pushButton_filter_left.clicked.connect(self.add_filter_left)
        self.pushButton_filter_right.clicked.connect(self.add_filter_right)
        self.pushButton_additional.clicked.connect(self.add_additional)
        # en: main buttons / ru: основные кнопки
        self.pushButton_save.clicked.connect(self.save_data)
        self.pushButton_default.clicked.connect(self.default_data)
        self.pushButton_cancel.clicked.connect(self.cancel)

    def set_current_font(self):
        """
        en: set current font to data
        ru: установка текущего шрифта в данные

        """
        self.data['font_name'] = self.fontComboBox.currentFont().family()

    def change_page(self):
        """
        en: switch current page of stackedWidget
        ru: переключение текущей страницы stackedWidget
        :return:
        """
        self.stackedWidget.setCurrentIndex(self.listWidget.currentRow())

    def add_filter_left(self):
        """
        en: open subwindow for adding items to left side
        ru: открытие окна для добавления элементов в левый список
        """
        side = 'filter_left'
        dialog = AddToList((side, self.data[side]))
        dialog.Signal_Message.connect(self.message_from_list)
        if dialog.check:
            dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            dialog.show()
        else:
            box = QtWidgets.QMessageBox.warning(self, 'WARNING!', 'Отсутсвует конфигурационный файл')

    def add_filter_right(self):
        """
        en: open subwindow for adding items to right side
        ru: открытие окна для добавления элементов в правый список
        :return:
        """
        side = 'filter_right'
        dialog = AddToList((side, self.data[side]))
        dialog.Signal_Message.connect(self.message_from_list)
        if dialog.check:
            dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            dialog.show()
        else:
            box = QtWidgets.QMessageBox.warning(self, 'WARNING', 'Отсутствует конфигурационный файл')

    def add_additional(self, box=None):
        """
        en: open subwindow for adding items to additional settings
        ru: открытие окна для добавления элементов в дополнительные настройки
        :param box:
        :return:
        """
        side = 'additional'
        dialog = AddToList((side, self.data[side]))
        dialog.Signal_Message.connect(self.message_from_list)
        if dialog.check:
            dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            dialog.show()
        else:
            box.QtWidgets.QMessageBox.warning(self, 'WARNING', 'Отсутствует конфигурационный файл')

    def message_from_list(self, mes):
        """
        en: message from subwindow to main window
        ru: сообщение из подокна в главное окно
        :param mes:
        """
        self.data[mes[0]] = mes[1]

    def set_color_bg(self):
        """
        en: open color dialog and save data
        ru: открытие диалога цвета и сохранение данных
        """
        color = QColorDialog.getColor()
        self.pushButton_color_bg.setStyleSheet(f'background-color:{str(color.name())}')
        self.data['color_bg'] = color.name()

    def set_color_font(self):
        """
        en: open color dialog and save data
        ru: открытие диалога цвета и сохранение данных
        """
        color = QColorDialog.getColor()
        self.pushButton_color_font.setStyleSheet(f'background-color:{str(color.name())}')
        self.data['color_font'] = color.name()

    def set_color_left(self):
        """
        en: open color dialog and save data
        ru: открытие диалога цвета и сохранение данных
        """
        color = QColorDialog.getColor()
        self.pushButton_color_left.setStyleSheet(f'background-color:{str(color.name())}')
        self.data['color_left'] = color.name()

    def set_color_right(self):
        """
        en: open color dialog and save data
        ru: открытие диалога цвета и сохранение данных
        """
        color = QColorDialog.getColor()
        self.pushButton_color_right.setStyleSheet(f'background-color:{str(color.name())}')
        self.data['color_right'] = color.name()

    def from_config(self):
        """
        en: set data to widget
        ru: установка данных в виджеты
        """
        # page 1 from stackedWidget / страница 1 из stackedWidget
        self.lineEdit_url.setText(self.data.get('url', ''))
        # page 2 from stackedWidget / страница 2 из stackedWidget
        self.spinBox_size_w.setValue(int(self.data.get('size_w', 600)))
        self.spinBox_size_h.setValue(int(self.data.get('size_h', 400)))
        self.spinBox_allign_left.setValue(int(self.data.get('allign_left', 0)))
        self.spinBox_allign_right.setValue(int(self.data.get('allign_right', 0)))
        self.spinBox_allign_up.setValue(int(self.data.get('allign_up', 0)))
        self.spinBox_allign_down.setValue(int(self.data.get('allign_down', 0)))
        # page 3 from stackedWidget / страница 3 из stackedWidget
        self.lineEdit_main_title.setText(self.data.get('main_title', ''))
        self.lineEdit_right_title.setText(self.data.get('right_title', ''))
        self.lineEdit_left_title.setText(self.data.get('left_title', ''))
        # page 4 from stackedWidget / страница 4 из stackedWidget
        self.fontComboBox.setCurrentFont(QFont(self.data.get('font_name', 'Sans Serif')))
        self.spinBox_big_font.setValue(int(self.data.get('big_font', 10)))
        self.spinBox_main_font.setValue(int(self.data.get('main_font', 10)))
        self.spinBox_regular_font.setValue(int(self.data.get('regular_font', 10)))
        self.spinBox_small_font.setValue(int(self.data.get('small_font', 10)))
        # page 5 from stackedWidget / страница 5 из stackedWidget
        self.pushButton_color_bg.setStyleSheet(f'background-color: {self.data.get("color_bg", "#000000")}')
        self.pushButton_color_font.setStyleSheet(f'background-color: {self.data.get("color_font", "#ffffff")}')
        self.pushButton_color_left.setStyleSheet(f'background-color: {self.data.get("color_left", "#000000")}')
        self.pushButton_color_right.setStyleSheet(f'background-color: {self.data.get("color_right", "#000000")}')

    def save_data(self):
        """
        en: save all data to config file
        ru: сохранение всех данных в файл конфигурации
        """
        # page 1 from stackedWidget / страница 1 из stackedWidget
        self.data['url'] = self.lineEdit_url.text()
        # page 2 from stackedWidget / страница 2 из stackedWidget
        self.data['size_w'] = self.spinBox_size_w.value()
        self.data['size_h'] = self.spinBox_size_h.value()
        self.data['allign_left'] = self.spinBox_allign_left.value()
        self.data['allign_right'] = self.spinBox_allign_right.value()
        self.data['allign_up'] = self.spinBox_allign_up.value()
        self.data['allign_down'] = self.spinBox_allign_down.value()
        # page 3 from stackedWidget / страница 3 из stackedWidget
        self.data['main_title'] = self.lineEdit_main_title.text()
        self.data['right_title'] = self.lineEdit_right_title.text()
        self.data['left_title'] = self.lineEdit_left_title.text()
        # page 4 from stackedWidget / страница 4 из stackedWidget
        self.data['big_font'] = self.spinBox_big_font.value()
        self.data['main_font'] = self.spinBox_main_font.value()
        self.data['regular_font'] = self.spinBox_regular_font.value()
        self.data['small_font'] = self.spinBox_small_font.value()
        # save to json file / сохранение в json файл
        with open('config.json', 'w') as file:
            json.dump(self.data, file, ensure_ascii=False)
        # status message to main window / статус сообщения в главное окно
        self.exit_status = 1
        self.emit_to_main()
        self.close()

    def default_data(self):
        """
        en: set default data to widgets
        ru: установка данных по умолчанию в виджеты
        """
        # page 1 from stackedWidget / страница 1 из stackedWidget
        self.data['url'] = 'https://calendar.ics'
        # page 2 from stackedWidget / страница 2 из stackedWidget
        self.data['size_w'] = self.display[self.display_index].width
        self.data['size_h'] = self.display[self.display_index].height
        self.data['allign_left'] = 0
        self.data['allign_right'] = 0
        self.data['allign_up'] = 0
        self.data['allign_down'] = 0
        # page 3 from stackedWidget / страница 3 из stackedWidget
        self.data['main_title'] = 'MAIN TITLE / ГЛАВНЫЙ ЗАГОЛОВОК'
        self.data['right_title'] = 'RIGHT TITLE / ПРАВЫЙ ЗАГОЛОВОК'
        self.data['left_title'] = 'LEFT TITLE / ЛЕВЫЙ ЗАГОЛОВОК'
        # page 4 from stackedWidget / страница 4 из stackedWidget
        self.data['font_name'] = 'Sans Serif'
        self.data['big_font'] = int(self.data['size_h'] // 60)
        self.data['main_font'] = int(self.data['size_h'] // 77)
        self.data['regular_font'] = int(self.data['size_h'] // 90)
        self.data['small_font'] = int(self.data['size_h'] // 108)
        self.data['filter_left'] = []
        self.data['filter_right'] = []
        self.data['additional'] = []
        self.data['color_bg'] = '#000000'
        self.data['color_font'] = '#ffffff'
        self.data['color_left'] = '#000000'
        self.data['color_right'] = '#000000'

        # save to json file / сохранение в json файл
        with open('config.json', 'w') as file:
            json.dump(self.data, file, ensure_ascii=False)

        self.exit_status = 2
        self.emit_to_main()
        self.close()

    def cancel(self):
        """
        en: exit without any change
        ru: выход без изменений
        """
        self.exit_status = 0
        self.emit_to_main()
        self.close()

    def emit_to_main(self):
        """
        en: send signal to main window
        ru: отправка сигнала в главное окно
        :return:
        """
        self.SignalToMain.emit(self.exit_status)


class AddToList(QtWidgets.QWidget):
    """
    en: subwindow for adding items to list
    ru: дочернее окно для добавления элементов в список
    """
    # create signal / создание сигнала
    Signal_Message = pyqtSignal(tuple)

    def __init__(self, message):
        super().__init__()
        self.ui = uic.loadUi('ui/addToList.ui', self)
        # var for check config file / переменная для проверки файла конфигурации
        self.check = True
        # en: var for check list (left or right filter or additional)
        # ru: переменная для проверки списка (левый или правый фильтр или дополнительные)
        self.side = message[0]
        # var for local list data / переменная для локального списка данных
        self.data_list = message[1]
        # set title for subwindow / установка заголовка окна
        self.set_subwin_title()
        # set data to listWidget / установка данных в listWidget
        self.listWidget.addItems(self.data_list)
        # buttons / кнопки
        self.pushButton_add.clicked.connect(self.add_item)
        self.pushButton_edit.clicked.connect(self.edit_item)
        self.pushButton_delete.clicked.connect(self.delete_item)
        self.pushButton_clear.clicked.connect(self.clear_items)
        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_save.clicked.connect(self.save_items)

    def set_subwin_title(self):
        """
        en: set text for label at subwindow
        ru: установка текста для label в дочернем окне
        """
        if self.side == 'filter_left':
            self.label_title.setText('Filter list for left side')
        elif self.side == 'filter_right':
            self.label_title.setText('Filter list for right side')
        elif self.side == 'additional':
            self.label_title.setText('Filter list for additional settings')
        else:
            pass

    def save_items(self):
        """
        en: save and send data to main window
        ru: сохранение и отправка данных в главное окно
        :return:
        """
        message = (self.side, self.data_list)
        self.Signal_Message.emit(message)
        self.close()

    def add_item(self):
        """
        en: open inputDialog to adding item
        ru: открытие inputDialog для добавления элемента
        """
        text, ok = QInputDialog.getText(self, 'add to list', 'ADD TO: ', text='add new')
        self.data_list.append(text)
        self.listWidget.clear()
        self.listWidget.addItems(self.data_list)

    def edit_item(self):
        """
        en: open inputDialog to edit current item
        ru: открытие inputDialog для редактирования текущего элемента
        """
        index = self.listWidget.currentRow()
        if self.listWidget.currentItem():
            editable_text = str(self.listWidget.currentItem().text())
        else:
            editable_text = ''
        text, ok = QInputDialog.getText(self, 'EDIT item', 'EDIT :', text=editable_text)
        self.data_list[index] = text
        self.listWidget.clear()
        self.listWidget.addItems(self.data_list)

    def delete_item(self):
        """
        en: delete current item
        ru: удаление текущего элемента
        """
        index = self.listWidget.currentRow()
        self.data_list.pop(index)
        self.listWidget.clear()
        self.listWidget.addItems(self.data_list)

    def clear_items(self):
        """
        en: clear all items
        ru: очистка всех элементов
        """
        self.data_list = []
        self.listWidget.clear()
        self.listWidget.addItems(self.data_list)

    def cancel(self):
        """
        en: exit without any change
        ru: выход без изменений
        """
        self.close()
