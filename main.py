from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QHeaderView,
    QAbstractItemView
)
from PySide6.QtCore import Qt
import sqlite3


# добавляет новое слово и перевод используя текст из полей на экране в базу данных
# после чего вызывает add_word_into_table для добавления строки в таблицу на экране
def add_word_from_fields():
    word = word_edit.text()
    translation = word_translation_edit.text()
    query = "INSERT INTO words (word, translation) VALUES (?, ?)"
    cursor.execute(query, [word, translation])
    cursor.execute("SELECT id FROM words WHERE ROWID = ?", [cursor.lastrowid])
    word_id = cursor.fetchone()[0]
    conn.commit()
    add_word_into_table(word_id, word, translation)


def add_word_into_table(id, word, translation):
    words_count = words_table.rowCount()
    words_table.setRowCount(words_count + 1)
    word_item = QTableWidgetItem(word)
    word_item.id = id # добавили поле id к объекту word_item, куда сохранили id строки из базы данных
    word_item.setTextAlignment(Qt.AlignCenter)
    translation_item = QTableWidgetItem(translation)
    translation_item.setTextAlignment(Qt.AlignCenter)
    words_table.setItem(words_count, 0, word_item)
    words_table.setItem(words_count, 1, translation_item)


def search():
    search_text = search_edit.text()
    query = """
SELECT id, word, translation FROM words
WHERE lower(word) LIKE lower('%' || ? || '%') OR lower(translation) LIKE lower('%' || ? || '%')
"""

    cursor.execute(query, [search_text, search_text])

    words_table.setRowCount(0)
    for row in cursor.fetchall():
        add_word_into_table(row[0], row[1], row[2])


def remove_word():
    # selectionModel позволяет понять какие ячейки выделены
    # selectedIndexes возвращает идентификаторы (строка + столбец) выделенных ячеек
    ids = words_table.selectionModel().selectedIndexes()
    if len(ids) > 0:
        # достаем ячейку word_item из таблицы на экране, которую создали в функции add_word_into_table
        # из этой ячейки берем поле id, в котором ранее сохранили идентификатор строки из БД
        word_id = words_table.item(ids[0].row(), 0).id
        cursor.execute("DELETE FROM words WHERE id = ?", [word_id])
        conn.commit()
        words_table.removeRow(ids[0].row())


def sqlite_lower(value_):
    return value_.lower()


conn = sqlite3.connect('words.db')
conn.create_function("lower", 1, sqlite_lower)
cursor = conn.cursor()

cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='words'")

if cursor.fetchone()[0] == 0:
    create_table_query = "CREATE TABLE words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL, translation TEXT NOT NULL)"
    cursor.execute(create_table_query)

app = QApplication([])

search_layout = QHBoxLayout()

search_edit = QLineEdit()
search_edit.setPlaceholderText('Что искать?')
search_layout.addWidget(search_edit)

search_button = QPushButton('Найти')
search_button.clicked.connect(search)
search_layout.addWidget(search_button)

search_widget = QWidget()
search_widget.setLayout(search_layout)


word_form_layout = QHBoxLayout()

word_edit = QLineEdit()
word_edit.setPlaceholderText('Слово')
word_form_layout.addWidget(word_edit)

word_translation_edit = QLineEdit()
word_translation_edit.setPlaceholderText('Перевод')
word_form_layout.addWidget(word_translation_edit)

add_word_button = QPushButton('Добавить')
add_word_button.clicked.connect(add_word_from_fields)
word_form_layout.addWidget(add_word_button)

remove_word_button = QPushButton('Удалить')
remove_word_button.clicked.connect(remove_word)
word_form_layout.addWidget(remove_word_button)

add_word_widget = QWidget()
add_word_widget.setLayout(word_form_layout)

layout = QVBoxLayout()


words_table = QTableWidget()
# позволяем выделять только строку целиком, вместо отдельных ячеек
words_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
words_table.setRowCount(0)
words_table.setColumnCount(2)
words_table.setHorizontalHeaderLabels(['Слово', 'Перевод'])
words_header = words_table.horizontalHeader()
words_header.setSectionResizeMode(0, QHeaderView.Stretch)
words_header.setSectionResizeMode(1, QHeaderView.Stretch)

search()
# заменили эти строки на строку выше
# cursor.execute("SELECT word, translation FROM words")
# for row in cursor.fetchall():
#     add_word_into_table(row[0], row[1])

layout.addWidget(search_widget)
layout.addWidget(words_table)
layout.addWidget(add_word_widget)


central_widget = QWidget()
central_widget.setLayout(layout)

window = QMainWindow()
window.setWindowTitle('Слова')
window.setCentralWidget(central_widget)
window.show()

app.exec()

conn.close()