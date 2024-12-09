import sys
import sqlite3
import bcrypt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit,
                             QPushButton, QLabel, QMessageBox, QCheckBox, QTextEdit, QDateEdit,
                             QFileDialog, QScrollArea)
from PyQt5 import QtCore


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            birth_date TEXT,
            location TEXT,
            description TEXT,
            photo TEXT,
            test_result TEXT
        )''')
        self.conn.commit()

    def add_user(self, username, password, first_name, last_name, birth_date, location, description='', photo=''):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.cursor.execute(
            "INSERT INTO users (username, password, first_name, last_name, birth_date, location, description, photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, hashed, first_name, last_name, birth_date, location, description, photo))
        self.conn.commit()

    def add_result(self, username, result):
        self.cursor.execute("UPDATE users SET test_result = ? WHERE username = ?", (result, username))
        self.conn.commit()

    def get_users_with_same_result(self, result):
        self.cursor.execute("SELECT username FROM users WHERE test_result = ?", (result,))
        return self.cursor.fetchall()

class RegistrationWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Регистрация')
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Логин')
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Пароль (не менее 8 символов)')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.first_name_input = QLineEdit(self)
        self.first_name_input.setPlaceholderText('Имя')
        layout.addWidget(self.first_name_input)

        self.last_name_input = QLineEdit(self)
        self.last_name_input.setPlaceholderText('Фамилия')
        layout.addWidget(self.last_name_input)

        self.birth_date_input = QDateEdit(self)
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDisplayFormat('yyyy-MM-dd')
        layout.addWidget(self.birth_date_input)

        self.location_input = QLineEdit(self)
        self.location_input.setPlaceholderText('Местоположение')
        layout.addWidget(self.location_input)

        self.description_input = QTextEdit(self)
        self.description_input.setPlaceholderText('Описание профиля (по желанию)')
        layout.addWidget(self.description_input)

        self.photo_input = QLineEdit(self)
        self.photo_input.setPlaceholderText('Фото (по желанию)')
        layout.addWidget(self.photo_input)

        self.photo_button = QPushButton('Выбрать фото', self)
        self.photo_button.clicked.connect(self.load_photo)
        layout.addWidget(self.photo_button)

        self.terms_checkbox = QCheckBox('Я согласен с пользовательским соглашением', self)
        self.terms_checkbox.stateChanged.connect(self.toggle_terms)
        layout.addWidget(self.terms_checkbox)

        self.terms_text = QLabel(
            "1. Принятие условий пользовательского соглашения\n"
            "Использование программного модуля «Бюро знакомств» возможно только при условии,\n"
            "что Вы принимаете все положения и условия, содержащиеся в соглашении.\n"
            "2. Правомерность\n"
            "• Создавая учетную запись, Вы заявляете и гарантируете, что:\n"
            "• Вам уже исполнилось 18 лет;\n"
            "• Вы имеете право, полномочия и правоспособность заключить настоящее соглашение и соблюдать его условия;\n"
            "• Вы никогда не были осуждены за тяжкое преступление или любое уголовное преступление,\n"
            "квалифицируемое как преступление сексуального характера, и не обязаны регистрироваться в качестве лица,\n"
            "совершившего преступление сексуального характера, в какой-либо государственной организации.\n"
            "• Ваша учетная запись не была ранее заблокирована и/или удалена из приложения.\n"
            "3. Учетная запись\n"
            "Вы соглашаетесь, что будете использовать Приложение и размещать в нем любой контент,\n"
            "только в соответствии с соглашением и всеми применимыми локальными,\n"
            "национальными и международными нормативно-правовыми актами.\n"
            , self)
        self.terms_text.setVisible(False)
        layout.addWidget(self.terms_text)

        self.register_button = QPushButton('Зарегистрироваться', self)
        self.register_button.clicked.connect(self.register_user)
        layout.addWidget(self.register_button)


        self.setLayout(layout)

    def load_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            self.photo_input.setText(file_name)

    def toggle_terms(self, state):
        self.terms_text.setVisible(state == QtCore.Qt.Checked)

    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        birth_date = self.birth_date_input.date().toString('yyyy-MM-dd')
        location = self.location_input.text()

        if not username or not first_name or not last_name or not birth_date or not location:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все обязательные поля.')
            return

            # Проверка на длину логина и пароля
        if len(username) > 20 or len(password) > 20:
            QMessageBox.warning(self, 'Ошибка', 'Логин и пароль не должны превышать 20 символов.')
            return

            # Проверка на пробелы и специальные символы
        if not username.isalnum() or not password.isalnum():
            QMessageBox.warning(self, 'Ошибка',
                                'Логин и пароль могут содержать только буквы и цифры, без пробелов и спецсимволов.')
            return

        if len(password) < 8:
            QMessageBox.warning(self, 'Ошибка', 'Пароль должен содержать не менее 8 символов.')
            return

        if self.terms_checkbox.isChecked():
            birth_year = int(birth_date.split('-')[0])
            if (2023 - birth_year) < 18:  # Проверка на 18 лет
                QMessageBox.warning(self, 'Ошибка', 'Вы должны быть старше 18 лет.')
                return

            description = self.description_input.toPlainText()
            photo = self.photo_input.text()
            self.db.add_user(username, password, first_name, last_name, birth_date, location, description, photo)
            QMessageBox.information(self, 'Успех', 'Вы успешно зарегистрированы!')
            self.open_test_window()  # Открываем окно тестирования
            self.close()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Вы должны согласиться с пользовательским соглашением.')

    def open_test_window(self):
        self.test_window = TestWindow(self.db, self.username_input.text())
        self.test_window.show()



class TestWindow(QWidget):
    def __init__(self, db, username):
        super().__init__()
        self.db = db
        self.username = username
        self.questions = [
            ("Какое из этих занятий Вам ближе всего?", ["Чтение книг", "Проведение времени на свежем воздухе", "Посещение мероприятий и вечеринок", "Занятия спортом"]),
            ("Какой тип общения Вам наиболее приятен?", ["Глубокие разговоры на серьезные темы", "Легкие и веселые беседы", "Обсуждение интересных фактов и знаний", "Романтические комплименты и флирт"]),
            ("Что для Вас важнее в отношениях?", ["Эмоциональная поддержка", "Общие интересы и хобби", "Приключения и новые впечатления", "Доверие и открытость"]),
            ("Какое качество партнера Вам наиболее важно?", ["Чувство юмора", "Доброта и забота", "Амбициозность и целеустремленность", "Интеллект и образованность"]),
        ]
        self.answers = [0] * len(self.questions)  # Список для хранения ответов
        self.question_index = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Тест')
        layout = QVBoxLayout()

        self.question_label = QLabel(self.questions[self.question_index][0])
        layout.addWidget(self.question_label)

        self.checkboxes = []
        for i, option in enumerate(self.questions[self.question_index][1]):
            checkbox = QCheckBox(option)
            checkbox.stateChanged.connect(lambda state, idx=i: self.record_answer(idx, state))
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        self.next_button = QPushButton('Далее')
        self.next_button.clicked.connect(self.next_question)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

    def record_answer(self, index, state):
        if state == QtCore.Qt.Checked:
            self.answers[self.question_index] = index + 1  # Сохраняем ответ (1-4)
        else:
            self.answers[self.question_index] = 0  # Сбрасываем ответ

    def next_question(self):
        self.question_index += 1
        if self.question_index < len(self.questions):
            self.question_label.setText(self.questions[self.question_index][0])
            for i, checkbox in enumerate(self.checkboxes):
                checkbox.setText(self.questions[self.question_index][1][i])
                checkbox.setChecked(False)  # Сбрасываем состояние чекбоксов
        else:
            self.calculate_result()

    def calculate_result(self):
        result_counts = [0] * 4  # Счетчики для каждого варианта
        for answer in self.answers:
            if answer > 0:
                result_counts[answer - 1] += 1

        max_count = max(result_counts)
        result_index = result_counts.index(max_count)

        # Устанавливаем результат на основе индекса
        result_map = {
            0: "Вам нужны глубокие и интеллектуальные отношения. Рекомендуем подходящих собеседников и людей с развитым внутренним миром.",
            1: "Вы ищете веселого и радостного партнера. Рекомендации для знакомства с жизнерадостными людьми.",
            2: "Вам важны приключения и активность. Лучше всего подходят люди, готовые к совместным путешествиям и новым приключениям.",
            3: "Вам нужны партнеры с доверительными и гармоничными отношениями. Рекомендованы открытые и честные люди."
        }
        result_text = result_map[result_index]

        # Сохраняем результат в базе данных
        self.db.add_result(self.username, result_text)

        QMessageBox.information(self, 'Результаты теста', result_text)
        self.show_similar_users(result_text)
        self.close()

    def show_similar_users(self, result_text):
        similar_users = self.db.get_users_with_same_result(result_text)
        if similar_users:
            users_list = ""
            for user in similar_users:
                username = user[0]
                if username == self.username:  # Пропускаем текущего пользователя
                    continue
                # Получаем информацию о пользователе
                self.db.cursor.execute(
                    "SELECT first_name, last_name, birth_date, description FROM users WHERE username = ?",
                    (username,))
                user_info = self.db.cursor.fetchone()
                if user_info:
                    first_name, last_name, birth_date, description = user_info
                    age = 2023 - int(birth_date.split('-')[0])  # Вычисляем возраст
                    users_list += f"Имя: {first_name}\nФамилия: {last_name}\nВозраст: {age}\nОписание: {description}\n\n"  # Добавляем отступ

            QMessageBox.information(self, 'Пользователи с похожими результатами',
                                    f"Пользователи с таким же результатом:\n{users_list}")
        else:
            QMessageBox.information(self, 'Пользователи с похожими результатами',
                                    "Нет пользователей с таким же результатом.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    db = Database()
    registration_window = RegistrationWindow(db)
    registration_window.show()
    sys.exit(app.exec_())
