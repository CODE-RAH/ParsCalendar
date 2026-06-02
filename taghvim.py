import jdatetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontDatabase
import json
from plyer import notification
import threading
import time
import sys
import os
from convertdate import islamic

# تنظیمات اولیه
TASKS_FILE = "tasks.json"
tasks = {}
HOLIDAYS = {
    "1404/01/01": "نوروز",
    "1404/01/02": "نوروز",
    "1404/01/12": "روز جمهوری اسلامی",
    "1404/03/14": "رحلت امام خمینی",
    # می‌تونی تعطیلات بیشتری اضافه کنی
}

# بارگذاری تسک‌ها
def load_tasks():
    global tasks
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = {}

# ذخیره تسک‌ها
def save_tasks():
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# نمایش نوتیفیکیشن
def show_notification(task_name, date):
    notification.notify(
        title=f"یادآور: {task_name}",
        message=f"تسک شما برای تاریخ {date} است!",
        timeout=10
    )

# بررسی یادآورها
def check_reminders():
    while True:
        current_date = jdatetime.date.today().strftime("%Y/%m/%d")
        for date, task_list in tasks.items():
            if date == current_date:
                for task in task_list:
                    show_notification(task["name"], date)
        time.sleep(60)

# رابط کاربری
class PersianCalendarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تقویم کدراه")
        self.setGeometry(100, 100, 800, 600)

        # بارگذاری فونت IranNastaliq
        font_path = os.path.join("fonts", "IranNastaliq.ttf")  # مسیر فونت نسبت به پوشه پروژه
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont(font_path)
        font_families = font_db.applicationFontFamilies(font_id)
        self.font = QFont("IranNastaliq", 20) if "IranNastaliq" in font_families else QFont("Arial", 20)

        # ویجت اصلی
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # اضافه کردن QLabel برای نمایش تاریخ امروز
        self.today_label = QLabel()
        self.today_label.setFont(self.font)
        self.today_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.today_label)

        # تاریخ فعلی
        self.current_date = jdatetime.date.today()
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month

        # هدر (ماه و سال + ناوبری)
        self.header_layout = QHBoxLayout()
        self.month_label = QLabel(self.get_month_name())
        self.month_label.setFont(self.font)
        self.month_label.setAlignment(Qt.AlignCenter)
        self.prev_button = QPushButton("ماه قبل")
        self.next_button = QPushButton("ماه بعد")
        self.prev_button.setFont(self.font)
        self.next_button.clicked.connect(self.prev_month)
        self.next_button.setFont(self.font)
        self.next_button.clicked.connect(self.next_month)
        self.header_layout.addWidget(self.prev_button)
        self.header_layout.addWidget(self.month_label)
        self.header_layout.addWidget(self.next_button)
        self.main_layout.addLayout(self.header_layout)

        # تقویم
        self.calendar_widget = QWidget()
        self.calendar_layout = QGridLayout()
        self.calendar_widget.setLayout(self.calendar_layout)
        self.main_layout.addWidget(self.calendar_widget)

        # بخش اضافه کردن تسک
        self.task_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setFont(self.font)
        self.task_input.setPlaceholderText("نام تسک را وارد کنید...")
        self.add_task_button = QPushButton("اضافه کردن تسک")
        self.add_task_button.setFont(self.font)
        self.add_task_button.clicked.connect(self.add_task)
        self.task_layout.addWidget(self.task_input)
        self.task_layout.addWidget(self.add_task_button)
        self.main_layout.addLayout(self.task_layout)

        # تم‌های رنگی
        self.theme_combo = QComboBox()
        self.theme_combo.setFont(self.font)
        self.theme_combo.addItems(["تیره", "روشن"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        self.main_layout.addWidget(self.theme_combo)

        # نمایش تاریخ امروز
        self.update_today_label()

        # نمایش تقویم
        self.update_calendar()

        # اعمال استایل
        self.change_theme(0)  # تم تیره به‌صورت پیش‌فرض

    def get_month_name(self):
        month_names = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
        return f"{month_names[self.current_month - 1]} {self.current_year}"

    def update_today_label(self):
        # دریافت تاریخ امروز شمسی
        today_j = jdatetime.date.today()

        # نام ماه‌های شمسی
        persian_months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                          "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
        # نام روزهای هفته شمسی (jdatetime شنبه=0)
        persian_weekdays = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]

        # نام روز هفته شمسی امروز
        weekday_name = persian_weekdays[today_j.weekday()]
        # نام ماه شمسی امروز
        persian_month_name = persian_months[today_j.month - 1]

        # ساخت رشته تاریخ‌ها به صورت مشابه سایت باحساب:
        persian_date_str = f"{weekday_name}، {today_j.day} {persian_month_name} {today_j.year}"

        self.today_label.setText(persian_date_str)

    def update_calendar(self):
        # پاک کردن تقویم قبلی
        for i in reversed(range(self.calendar_layout.count())):
            widget = self.calendar_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # نمایش روزهای هفته
        days = ["شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setFont(self.font)
            label.setAlignment(Qt.AlignCenter)
            self.calendar_layout.addWidget(label, 0, i)

        # محاسبه روزهای ماه
        first_day = jdatetime.date(self.current_year, self.current_month, 1)
        next_month = self.current_month + 1 if self.current_month < 12 else 1
        next_year = self.current_year + 1 if self.current_month == 12 else self.current_year
        last_day = jdatetime.date(next_year, next_month, 1) - jdatetime.timedelta(days=1)
        days_in_month = last_day.day
        weekday = first_day.weekday()

        # نمایش روزها
        row = 1
        col = weekday
        for day in range(1, days_in_month + 1):
            date_str = f"{self.current_year}/{self.current_month:02d}/{day:02d}"
            btn = QPushButton(str(day))
            btn.setFont(self.font)
            btn.clicked.connect(lambda checked, d=date_str: self.show_tasks(d))
            # علامت‌گذاری تعطیلات
            if date_str in HOLIDAYS:
                btn.setStyleSheet("background-color: #ff4d4d; color: white; border-radius: 5px;")
            self.calendar_layout.addWidget(btn, row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.month_label.setText(self.get_month_name())
        self.update_calendar()
        self.update_today_label()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.month_label.setText(self.get_month_name())
        self.update_calendar()
        self.update_today_label()

    def add_task(self):
        task_name = self.task_input.text()
        if not task_name:
            QMessageBox.warning(self, "خطا", "لطفاً نام تسک را وارد کنید!")
            return
        date_str = self.current_date.strftime("%Y/%m/%d")
        if date_str not in tasks:
            tasks[date_str] = []
        tasks[date_str].append({"name": task_name, "completed": False})
        save_tasks()
        QMessageBox.information(self, "موفقیت", f"تسک '{task_name}' به تاریخ {date_str} اضافه شد!")
        self.task_input.clear()

    def show_tasks(self, date):
        task_window = QWidget()
        task_window.setWindowTitle(f"تسک‌های {date}")
        task_window.setGeometry(200, 200, 300, 200)
        layout = QVBoxLayout()

        label = QLabel(f"تسک‌های تاریخ {date}")
        label.setFont(self.font)
        layout.addWidget(label)

        if date in tasks and tasks[date]:
            for task in tasks[date]:
                checkbox = QCheckBox(task["name"])
                checkbox.setFont(self.font)
                checkbox.setChecked(task["completed"])
                checkbox.stateChanged.connect(lambda state, t=task: self.update_task_status(t, state))
                layout.addWidget(checkbox)
        else:
            layout.addWidget(QLabel("هیچ تسکی وجود ندارد!"))

        task_window.setLayout(layout)
        task_window.show()

    def update_task_status(self, task, state):
        task["completed"] = state == Qt.Checked
        save_tasks()

    def change_theme(self, index):
        if index == 0:  # تم تیره
            stylesheet = """
                QMainWindow {
                    background-color: #2b2b2b;
                }
                QLabel {
                    color: #ffffff;
                    font-size: 24px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 22px;
                    font-family: IranNastaliq;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QLineEdit {
                    background-color: #3c3c3c;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 22px;
                    font-family: IranNastaliq;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 22px;
                    font-family: IranNastaliq;
                }
                QCheckBox {
                    color: #ffffff;
                    font-size: 22px;
                    font-family: IranNastaliq;
                }
            """
        else:  # تم روشن
            stylesheet = """
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QLabel {
                    color: #333333;
                    font-size: 24px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 22px;
                    font-family: IranNastaliq;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 22px;
                    font-family: IranNastaliq;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 22px;
                    font-family: IranNastaliq;
                }
                QCheckBox {
                    color: #333333;
                    font-size: 22px;
                    font-family: IranNastaliq;
                }
            """
        self.setStyleSheet(stylesheet)
        self.update_calendar()

if __name__ == "__main__":
    load_tasks()
    app = QApplication(sys.argv)
    window = PersianCalendarApp()
    window.show()
    threading.Thread(target=check_reminders, daemon=True).start()
    sys.exit(app.exec_())
