"""
en: Module for running the program
ru: Модуль для запуска программы
"""
import sys
from ics_gui import app, MainWindow


def main():
    main_app = app(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(main_app.exec_())

if __name__ == '__main__':
    main()
