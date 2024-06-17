"""
en: This is a GUI application for displaying events from Google Calendar.
ru: Это GUI для отображения событий из Google Calendar.
"""
import sys
import datetime

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal

import calendar_data
from ics_gui_settings import *

app = QtWidgets.QApplication

class MainWindow(QtWidgets.QWidget):
    """
    en: Main window class
    ru: Класс главного окна
    """
    def __init__(self):
        super().__init__()
        # en: Define variable for create a thread object / ru: Определение переменной для создания объекта потока
        self.thread = None

        # en: Load the GUI from the file / ru: Загрузка GUI из файла
        uic.loadUi('ui/new_gui.ui', self)

        # en: Create an object of the settings window / ru: Создать объект окна настроек
        self.settings_window = SettingsWindow()
        self.settings_window.SignalToMain.connect(self.after_settings)

        # en: Load settings from the settings window / ru: Загрузка настроек из окна настроек
        self.data = self.settings_window.data

        # en: Timer for the clock - every second updates the real time clock
        # ru: Таймер для часов - каждую секунду обновляет часы реального времени
        self.timer = QtCore.QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.clock)

        # en: Start the thread / ru: Запускаем поток
        self.start_worker()

        # en: List of month names / ru: Список названий месяцев
        self.month_list = [
            'ЯНВАРЯ',
            'ФЕВРАЛЯ',
            'МАРТА',
            'АПРЕЛЯ',
            'МАЯ',
            'ИЮНЯ',
            'ИЮЛЯ',
            'АВГУСТА',
            'СЕНТЯБРЯ',
            'ОКТЯБРЯ',
            'НОЯБРЯ',
            'ДЕКАБРЯ'
        ]

        # en: List of day names / ru: Список названий дней недели
        self.day_list = [
            'ПОНЕДЕЛЬНИК',
            'ВТОРНИК',
            'СРЕДА',
            'ЧЕТВЕРГ',
            'ПЯТНИЦА',
            'СУББОТА',
            'ВОСКРЕСЕНЬЕ'
        ]

        # en: List of labels for event headers on the right side
        # ru: Список полей для заголовков событий справа
        self.summary_r_list = self.setup_label_list('label_summary_r', 7)
        # en: List of labels for event headers on the left side
        # ru: Список полей для заголовков событий слева
        self.summary_l_list = self.setup_label_list('label_summary_l', 7)
        # en: List of fields for event descriptions on the right side
        # ru: Список полей для описаний событий справа
        self.description_r_list = self.setup_label_list('label_description_r', 7)
        # en: List of fields for event descriptions on the left side
        # ru: Список полей для описаний событий слева
        self.description_l_list = self.setup_label_list('label_description_l', 7)
        # en: List of fields for the date number of the event on the right side
        # ru: Список полей для числа даты события справа
        self.date_r_list = self.setup_label_list('label_date_r', 7)
        # en: List of fields for the date number of the event on the left side
        # ru: Список полей для числа даты события слева
        self.date_l_list = self.setup_label_list('label_date_l', 7)
        # en: List of fields for the month of the event date on the right side
        # ru: Список полей для месяца даты события справа
        self.month_r_list = self.setup_label_list('label_month_r', 7)
        # en: List of fields for the month of the event date on the left side
        # ru: Список полей для месяца даты события слева
        self.month_l_list = self.setup_label_list('label_month_l', 7)
        # en: List of fields for the day of the week of the event on the right side
        # ru: Список полей для дня недели события справа
        self.week_r_list = self.setup_label_list('label_week_r', 7)
        # en: List of fields for the day of the week of the event on the left side
        # ru: Список полей для дня недели события слева
        self.week_l_list = self.setup_label_list('label_week_l', 7)
        # en: List of fields for the event time on the right side
        # ru: Список полей для времени события справа
        self.time_r_list = self.setup_label_list('label_time_r', 7)
        # en: List of fields for the event time on the left side
        # ru: Список полей для времени события слева
        self.time_l_list = self.setup_label_list('label_time_l', 7)

    def set_bg_color(self):
        """
        en: set the color of the fields
        ru: установка цвета полей
        """
        self.setStyleSheet(f"background-color:{self.data.get('color_bg', '#000000')};")

    def set_labels_color(self):
        """
        en: set font color
        ru: установка цвета шрифта
        """
        font_color = f"color:{self.data.get('color_font', '#000000')};"
        left_bg_color = f"background-color:{self.data.get('color_left', '#000000')};"
        right_bg_color = f"background-color:{self.data.get('color_right', '#000000')};"

        left_labels_list = [
            self.summary_l_list,
            self.date_l_list,
            self.month_l_list,
            self.week_l_list,
            self.time_l_list,
        ]
        right_labels_list = [
            self.summary_r_list,
            self.date_r_list,
            self.month_r_list,
            self.week_r_list,
            self.time_r_list
        ]
        for x in left_labels_list:
            for i in x:
                i.setStyleSheet(f'{left_bg_color}{font_color}')
        for x in right_labels_list:
            for i in x:
                i.setStyleSheet(f'{right_bg_color}{font_color}')
        for x in self.description_l_list:
            x.setStyleSheet(f'{font_color}')
        for x in self.description_r_list:
            x.setStyleSheet(f'{font_color}')

        self.label_title_main.setStyleSheet(font_color)
        self.label_title_current_time.setStyleSheet(font_color)

        self.label_title_l.setStyleSheet(
            f"color:{self.data.get('color_left', '#000000')};")
        self.label_title_r.setStyleSheet(
            f"color:{self.data.get('color_right', '#000000')};")

    def mousePressEvent(self, QMouseEvent):
        """
        en: Handling the right mouse button click - pop-up menu (exit, settings, cancel)
        ru: Отработка нажатия правой кнопки - всплывающее меню (выход, настройки, отмена)
        :param QMouseEvent: event
        """
        if QMouseEvent.button() == QtCore.Qt.MouseButton.RightButton:
            self.message_box()

    def message_box(self):
        """
        en: Pop-up menu (exit, settings, cancel)
        ru: Всплывающее меню (выход, настройки, отмена)
        """
        box = QtWidgets.QMessageBox()
        box.setText('QUIT or SETTINGS?')
        box.addButton('QUIT', QtWidgets.QMessageBox.ButtonRole.ActionRole)
        box.addButton('SETTINGS', QtWidgets.QMessageBox.ButtonRole.ActionRole)
        box.addButton('CANCEL', QtWidgets.QMessageBox.ButtonRole.ActionRole)

        result = box.exec()

        if result == 0:
            if self.settings_window.isVisible():
                self.settings_window.close()
            self.close()
        if result == 1:
            self.open_settings()

    def open_settings(self):
        """
        en: Open the settings window
        ru: Открыть окно настроек
        """
        self.settings_window.show()

    #
    def after_settings(self, message):
        """
        en: After closing the settings window, update the data
        ru: После закрытия окна настроек обновить данные
        :param message:
        :return:
        """
        if message:
            self.update()
        return

    #
    def update(self):
        """
        en: Update the data
        ru: Обновить данные
        """
        all_labels_list = [
            self.summary_l_list,
            self.summary_r_list,
            self.description_l_list,
            self.description_r_list,
            self.date_l_list,
            self.date_r_list,
            self.month_l_list,
            self.month_r_list,
            self.week_l_list,
            self.week_r_list,
            self.time_l_list,
            self.time_r_list
        ]
        for i in all_labels_list:
            for x in i:
                x.clear()

        self.data = self.settings_window.data

        self.thread.url = self.data.get('url', '')
        self.thread.filter_list_left = self.data.get('filter_left', [])
        self.thread.filter_list_right = self.data.get('filter_right', [])
        self.thread.events_dict = {}

        self.resize(self.data.get('size_w', 600), self.data.get('size_h', 400))
        self.label_title_main.setText(self.data.get('main_title', ''))
        self.label_title_l.setText(self.data.get('left_title', ''))
        self.label_title_r.setText(self.data.get('right_title', ''))

        self.label_title_current_time.setStyleSheet('color:white')

        self.set_bg_color()
        self.set_labels_color()

    def clock(self):
        """
        en: Update the real time clock
        ru: Обновление часов реального времени
        """
        t = QtCore.QTime.currentTime()
        t_text = t.toString('hh : mm : ss')
        self.label_title_current_time.setText(t_text)

    def start_worker(self):
        """
        en: Start the thread
        ru: Запуск потока
        """
        self.thread = ThreadClass()
        self.thread.url = self.data.get('url', '')
        self.thread.filter_list_left = self.data.get('filter_left', [])
        self.thread.filter_list_right = self.data.get('filter_right', [])
        self.thread.start()
        self.thread.any_signal.connect(self.check_web)

    def check_web(self, events):
        """
        en: Check the status of the Internet connection
        ru: Проверка статуса подключения к интернету
        :param events:
        :return:
        """
        if events.get('status', '') == 'online':
            self.online_function(events)
        else:
            self.offline_function()

    def offline_function(self):
        """
        en: Display a message about the lack of an Internet connection
        ru: Вывод сообщения об отсутствии подключения к интернету
        """
        self.label_title_online.setText('!OFFLINE!')
        self.label_title_online.setStyleSheet('color:red')

        self.label_title_main.setText('!!! ВНИМАНИЕ !!! ОТСУТСТВУЕТ ПОДКЛЮЧЕНИЕ К ИНТЕРНЕТУ !!!')

    def online_function(self, event_list):
        """
        en: Display events
        ru: Вывод событий
        :param event_list: data of events
        :return:
        """
        self.label_title_online.setText('ONLINE')
        self.label_title_online.setStyleSheet('color:green')
        self.label_title_main.setText(self.data.get('main_title', ''))

        events = event_list

        self.update()

        # update summary and location / обновление заголовков и местоположения
        self.update_label_text(self.summary_r_list,
                               [f"{e.get('summary', '')} ({e.get('location', '')})" for e in events['right_side']])
        self.update_label_text(self.summary_l_list,
                               [f"{e.get('summary', '')} ({e.get('location', '')})" for e in events['left_side']])

        # update descriptions / обновление описаний
        self.update_label_text(self.description_r_list,
                               [self.edit_description(e.get('description', '')) for e in events['right_side']])
        self.update_label_text(self.description_l_list,
                               [self.edit_description(e.get('description', '')) for e in events['left_side']])

        # update dates / обновление дат
        self.update_label_text(self.date_r_list, [self.get_date(e.get('date_start', '')) for e in events['right_side']])
        self.update_label_text(self.date_l_list, [self.get_date(e.get('date_start', '')) for e in events['left_side']])

        # update times / обновление времени
        self.update_label_text(self.time_r_list,
                               [self.get_time_range(e.get('date_start', ''), e.get('date_end', '')) for e in
                                events['right_side']])
        self.update_label_text(self.time_l_list,
                               [self.get_time_range(e.get('date_start', ''), e.get('date_end', '')) for e in
                                events['left_side']])

        # update months / обновление месяцев
        self.update_label_text(self.month_r_list,
                               [self.get_month(e.get('date_start', '')) for e in events['right_side']])
        self.update_label_text(self.month_l_list,
                               [self.get_month(e.get('date_start', '')) for e in events['left_side']])

        # update weekdays / обновление дней недели
        self.update_label_text(self.week_l_list,
                               [self.get_weekday(e.get('date_start', '')) for e in events['left_side']])
        self.update_label_text(self.week_r_list,
                                 [self.get_weekday(e.get('date_start', '')) for e in events['right_side']])

    @staticmethod
    def get_date(date):
        """
        en: Get the day of the month
        ru: Получить день месяца
        :param date: datime.datetime
        """
        if type(date) is datetime.datetime:
            return str(date.day)
        return ''

    @staticmethod
    def get_time_range(start, end):
        """
        en: Get the time range
        ru: Получить временной диапазон
        :param start:
        :param end:
        :return:
        """
        if type(start) is datetime.datetime:
            start = start.strftime('%H:%M')
        if type(end) is datetime.datetime:
            end = end.strftime('%H:%M')
        return f'{start} -- {end}'

    def get_month(self, date):
        """
        en: Get the month
        ru: Получить месяц
        :param date:
        :return:
        """
        if type(date) is datetime.datetime:
            return self.month_list[date.month - 1]
        return ''

    def get_weekday(self, date):
        """
        en: Get the day of the week
        ru: Получить день недели
        """
        if type(date) is datetime.datetime:
            return self.day_list[date.weekday() - 1]
        return ''

    # исправление описания

    @staticmethod
    def edit_description(text):
        """
        en: Edit the description
        ru: Исправление описания
        :param text:
        :return:
        """
        assistant_list = [
            'TEST'
        ]
        for x in assistant_list:
            text = text.replace(x, '\n{}\n'.format(x))
        return text

    def setup_label_list(self, label_prefix, count):
        """
        en: Create a list of labels
        ru: Создание списка полей
        :param label_prefix:
        :param count:
        :return:
        """
        return [getattr(self, f"{label_prefix}_{i}") for i in range(1, count + 1)]

    @staticmethod
    def update_label_text(labels, texts):
        """
        en: Update the text in the labels
        ru: Обновление текста в полях
        :param labels:
        :param texts:
        :return:
        """
        for label, text in zip(labels, texts):
            label.setText(text)


class ThreadClass(QtCore.QThread):
    """
    en: Thread class
    ru: Класс потока
    """
    any_signal = pyqtSignal(dict)

    def __init__(self):
        """
        en: Initialize the class
        ru: Инициализация класса
        """
        super().__init__()
        self.events_dict = {}
        self.url = ''
        self.filter_list_left = []
        self.filter_list_right = []

    def run(self):
        """
        en: Run the thread
        ru: Запуск потока
        :return:
        """
        while True:
            cal = calendar_data.DataFromCalendar(self.url)
            cal_all = cal.get_next_events()

            if cal_all:
                self.events_dict['left_side'] = cal.set_filter(cal_all, self.filter_list_left)[0:7]
                while len(self.events_dict['left_side']) < 7:
                    self.events_dict['left_side'].append({})
                self.events_dict['right_side'] = cal.set_filter(cal_all, self.filter_list_right)[0:7]
                while len(self.events_dict['right_side']) < 7:
                    self.events_dict['right_side'].append({})

                self.events_dict['status'] = 'online'

            else:
                self.events_dict['status'] = 'offline'
            self.any_signal.emit(self.events_dict)
            self.sleep(10)
