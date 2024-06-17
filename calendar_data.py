"""
en: The module is designed to work with calendar data.
The module allows you to download data from the calendar,
convert it to a list of events, and filter events by keywords.
ru: Модуль предназначен для работы с данными календаря.
Модуль позволяет скачивать данные с календаря,
преобразовывать их в список событий и фильтровать события по ключевым словам.
"""
import requests
import datetime
import icalendar


class DataFromCalendar:
    """
    en: The class is designed to work with calendar data.
    ru: Класс предназначен для работы с данными календаря.
    """
    def __init__(self, url):
        self.url = url

    def get_data(self):
        """
        en: The method is designed to download calendar data.
        ru: Метод предназначен для скачивания данных календаря.
        :return: string with iCal data / None
        """
        try:
            # download calendar data / скачивание данных календаря
            web_data = requests.get(self.url).text
        except requests.exceptions.RequestException:
            web_data = None

        return web_data

    def convert_data(self):
        """
        en: The method is designed to process data and save it to the event list, each event is a dictionary.
        ru: обработка данных и сохранение в список событий, каждое событие - словарь
        :return: dict with event data / None
        """
        data = self.get_data()
        # en: setting the time zone variable and the calendar link
        # ru: установка переменной часового пояса и ссылки на календарь
        delta = datetime.timedelta(hours=5)

        if data:
            try:
                ical = icalendar.Calendar.from_ical(data)
                # en: selection of events / ru: отбор мероприятий
                ical_data = ical.walk()
                ical_data = [x for x in ical_data if x.name == 'VEVENT']

                data = []

                # en: filling in the event dictionary / ru: заполнение словаря мероприятия
                for x in ical_data:
                    temp_dict = {}
                    # en: date and time of the event start / ru: дата и время начала события
                    temp_dict['date_start'] = datetime.datetime.fromisoformat(
                        str(x.decoded('DTSTART', '2000-01-01'))) + delta
                    # en: date and time of the event end / ru: дата и время окончания события
                    temp_dict['date_end'] = datetime.datetime.fromisoformat(str(x.decoded('DTEND', '2000-01-01'))) + delta
                    # en: date and time of the event end / ru: дата и время окончания события
                    temp_dict['date_stamp'] = datetime.datetime.fromisoformat(str(x.decoded('DTEND', '2000-01-01'))) + delta
                    # en: date and time of the event creation / ru: дата и время создания события
                    temp_dict['created'] = datetime.datetime.fromisoformat(str(x.decoded('CREATED', '2000-01-01'))) + delta
                    # en: date and time of the last edit / ru: дата и время последнего редактирования
                    temp_dict['last-modified'] = datetime.datetime.fromisoformat(
                        str(x.decoded('LAST-MODIFIED', '2000-01-01'))) + delta
                    # en: unique identification number of the event / ru: уникальный индификационный номер события
                    temp_dict['uid'] = str(x.get('UID', ''))
                    # en: sequence number / ru: порядковый номер
                    temp_dict['sequence'] = str(x.get('SEQUENCE', ''))
                    # en: event title / ru: заголовок события
                    temp_dict['summary'] = str(x.get('SUMMARY', ''))
                    # en: event description / ru: описание события
                    temp_dict['description'] = self.remove_html(str(x.get('DESCRIPTION', '')))
                    # en: location / ru: место события
                    temp_dict['location'] = str(x.get('LOCATION', ''))
                    # en: status (completed / not completed) of the event
                    # ru: статус (выполнено / не выполнено) события
                    temp_dict['status'] = str(x.get('STATUS', ''))
                    # en: transparency (transparent / opaque) of the event
                    # ru: прозрачность (прозрачный/непрозрачный) события
                    temp_dict['transp'] = str(x.get('TRANSP', ''))

                    # en: adding an event dictionary to the list
                    # ru: добавление в список словарь мероприятия
                    data.append(temp_dict)
            except ValueError:
                print('Error: ValueError')
                data = None
        else:
            data = None

        return data

    def get_next_events(self):
        """
        en: The method is designed to select future events.
        ru: Метод предназначен для отбора будущих событий.
        """
        data = self.convert_data()
        if data:
            # en: screening of future events and sorting in order
            # ru: отсев будущих мероприятий и сортировка по порядку
            future_data = [x for x in data if x['date_start'].timestamp() > datetime.datetime.today().timestamp()]
            future_data = sorted(future_data, key=lambda x: x['date_start'], reverse=False)
        else:
            future_data = None

        return future_data

    @staticmethod
    def set_filter(data, filter_list):
        """
        en:
        filter for selecting events by keywords
        displays the nearest events in the title (summary) of which there are keywords
        takes a list of keywords [str, str...]
        ru:
        фильтр для отбора событий по ключевым словам
        выводит ближайшие события в заголовке (summary) которых есть ключевые слова
        принимает список ключевых слов [str, str...]
        :param data: list of events
        :param filter_list: list of keywords
        :return: list of events / None
        """
        filter_list = [i.lower() for i in filter_list]
        if data:
            filter_events_list = list(filter(lambda x: any([i in x['summary'].lower() for i in filter_list]), data))
            return filter_events_list
        return None

    def update_url(self, url):
        """
        en: method for updating the calendar link
        ru: метод для обновления ссылки календаря
        :param url: string with the calendar link
        """
        self.url = url

    #
    @staticmethod
    def remove_html(text):
        """
        en: method for removing html tags from text
        ru: метод для удаления html тегов из текста
        :param text: text with html tags
        :return: updated text without html tags
        """
        tags = [
            '<b>',
            '</b>',
            '<html-blob>',
            '</html-blob>',
            '<br>',
            '<i>',
            '</i>',
            '<u>',
            '</u>',
            '<br />',
            '&nbsp;&nbsp;',
            '<span>',
            '</span>'
        ]
        for x in tags:
            text = text.replace(x, '')
        text = text.replace(',\n', ', ')
        text = text.replace('\n', '')
        text = text.replace(',', ', ')
        return text
