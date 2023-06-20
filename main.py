import sys
import os
import sqlite3
from PIL import Image, ImageEnhance, ImageFilter
from PIL.ImageQt import ImageQt

from photofilters.grey import grey_filter
from photofilters.sepia import sepia_filter
from photofilters.three_d import three_d_filter
from photofilters.texture import texture_filter

from PyQt6 import uic
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QIcon, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QFileDialog, QDialog, QInputDialog, QColorDialog


NEW_FILE = 'new_img.png'
NEW_FILE_WITHOUT_FILTERS = 'new_img_without_filters.png'
NEW_FILE_WITHOUT_EFFECTS = 'new_img_without_effects.png'
NORMAL_WIDTH = 800
NORMAL_HEIGHT = 600
BRIGHTNESS_IS_OPENED = False
NAME= '?'
PATH = '?'
    

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ImageSizeDialog(QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.main = root
        uic.loadUi(resource_path(r"design_image_size_dialog.ui"), self)

        self.button_ok.clicked.connect(self.close_action)
        self.button_cancel.clicked.connect(self.close_action)

    def set_size(self, w, h):
        self.input_width.setText(str(w))
        self.input_height.setText(str(h))

    def close_action(self):
        n_w = self.input_width.text()
        n_h = self.input_height.text()
        Window.change_img_size(win, int(n_w), int(n_h))
        self.close()


class OpacityDialog(QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.main = root
        uic.loadUi(resource_path(r"design_image_opacity_dialog.ui"), self)

        self.slider.setInvertedAppearance(True)
        self.slider.valueChanged.connect(self.action)

        self.button_ok.clicked.connect(self.close_action)

    def action(self):
        opacity = 100 - self.sender().value()
        img = win.working_copy_img.copy()
        img.putalpha(opacity * 255 // 100)
        win.pixmap = QPixmap.fromImage(ImageQt(img))
        win.label_image.setPixmap(win.pixmap)

    def close_action(self):
        win.pixmap.save(NEW_FILE, "PNG")
        win.working_copy_img = Image.open(NEW_FILE)
        win.working_copy_img_without_filters = win.working_copy_img.copy()
        win.working_copy_img_without_effects = win.working_copy_img.copy()
        self.close()


class BrightnessDialog(QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.main = root
        uic.loadUi(resource_path(r"design_image_brightness.ui"), self)

        global BRIGHTNESS_IS_OPENED
        if BRIGHTNESS_IS_OPENED is False:
            self.slider.setValue(50)
        else:
            BRIGHTNESS_IS_OPENED = True

        self.slider.valueChanged.connect(self.action)
        self.button_ok.clicked.connect(self.close_action)

    def action(self):
        val = self.sender().value() / 50
        self.cur = win.working_copy_img_without_effects.copy()
        enhancer = ImageEnhance.Brightness(self.cur)
        self.cur = enhancer.enhance(val)
        qt = ImageQt(self.cur).copy()
        win.pixmap = QPixmap.fromImage(qt)
        win.label_image.setPixmap(win.pixmap)

    def close_action(self):
        win.pixmap.save(NEW_FILE, "PNG")
        win.working_copy_img = Image.open(NEW_FILE)
        win.working_copy_img_without_filters = win.working_copy_img.copy()
        win.working_copy_img_without_effects = win.working_copy_img.copy()
        self.close()


class BlurDialog(QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.main = root
        uic.loadUi(resource_path(r"design_blur_dialog.ui"), self)

        self.slider.valueChanged.connect(self.action)
        self.button_ok.clicked.connect(self.close_action)

    def action(self):
        blur = self.sender().value() // 10
        img = win.working_copy_img.copy()
        img = img.filter(ImageFilter.GaussianBlur(blur))
        qt = ImageQt(img).copy()
        win.pixmap = QPixmap.fromImage(qt)
        win.label_image.setPixmap(win.pixmap)

    def close_action(self):
        win.pixmap.save(NEW_FILE, "PNG")
        win.working_copy_img = Image.open(NEW_FILE)
        win.working_copy_img_without_filters = win.working_copy_img.copy()
        win.working_copy_img_without_effects = win.working_copy_img.copy()
        self.close()


class PropertiesDialog(QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.main = root
        uic.loadUi(resource_path(r"design_properties.ui"), self)


class SettingsDialog(QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.main = root
        uic.loadUi(resource_path(r"design_settings.ui"), self)

        with open(resource_path(r"current_theme.txt"), encoding="utf-8") as f:
            theme_name = f.read()

        if theme_name == "light":
            self.radio_light.setChecked(True)
        elif theme_name == "dark":
            self.radio_dark.setChecked(True)

        self.button_ok.clicked.connect(self.action_close)

    def action_close(self):
        theme_name = ''
        if self.radio_light.isChecked():
            theme_name = "light"
        elif self.radio_dark.isChecked():
            theme_name = "dark"
        with open(resource_path(r"current_theme.txt"), "w") as f:
            f.write(theme_name)
        win.set_theme()
        self.close()

    
class FillColorDialog(QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.main = root
        uic.loadUi(resource_path(r"design_fill_color_dialog.ui"), self)

        self.button_without.clicked.connect(self.without_color)
        self.button_change_color.clicked.connect(self.change_color)

    def without_color(self):
        win.fill_color = None
        win.action_color_fill.setIcon(QIcon(resource_path(r"cross.jpg")))
        self.close()

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            win.fill_color = color
            img = Image.open(resource_path(r"color.jpg"))
            pixels = img.load()
            x, y = img.size
            for i in range(y):
                for j in range(x):
                    pixels[j, i] = color.red(), color.green(), color.blue()
            img.save(resource_path(r"color.jpg"))
            win.action_color_fill.setIcon(QIcon(resource_path(r"color.jpg")))
        self.close()


class OutlineDialog(QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.main = root
        uic.loadUi(resource_path(r"design_outline.ui"), self)

        self.button_without_color.clicked.connect(self.without_color)
        self.button_change_color.clicked.connect(self.change_color)
        self.button_ok.clicked.connect(self.ok)

    def ok(self):
        win.outline_width = self.spinBox.value()
        self.close()

    def without_color(self):
        win.outline_color = None
        win.outline_width = self.spinBox.value()
        win.action_outline.setIcon(QIcon(resource_path(r"cross.jpg")))
        self.close()

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            win.outline_color = color
            img = Image.open(resource_path(r"outline_color.jpg"))
            pixels = img.load()
            x, y = img.size
            for i in range(y):
                for j in range(x):
                    pixels[j, i] = color.red(), color.green(), color.blue()
            for i in range(20, y - 20):
                for j in range(20, x - 20):
                    pixels[j, i] = 255, 255, 255
            img.save(r"outline_color.jpg")
            win.action_outline.setIcon(QIcon(resource_path(r"outline_color.jpg")))
        win.outline_width = self.spinBox.value()
        self.close()


class Rectangle:
    def __init__(self, x, y, x2, y2, color, outline_color, outline_width):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.outline_color = outline_color
        self.outline_width = outline_width
    
    def draw(self, painter):
        if self.color is not None:
            painter.setBrush(self.color)
        else:
            painter.setBrush(QColor(0, 0, 0, 0))

        pen_color = QColor(0, 0, 0, 0)
        if self.outline_color is not None:
            pen_color = self.outline_color
        pen = QPen(pen_color)
        pen.setWidth(self.outline_width)
        painter.setPen(pen)
        painter.drawRect(self.x, self.y, self.x2 - self.x, self.y2 - self.y)


class Circus:
    def __init__(self, x, y, x2, y2, color, outline_color, outline_width):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.outline_color = outline_color
        self.outline_width = outline_width

    def draw(self, painter):
        cx = self.x + int((self.x2 - self.x) / 2)
        cy = self.y + int((self.y2 - self.y) / 2)
        rx = cx - self.x
        ry = cy - self.y
        
        if self.color is not None:
            painter.setBrush(self.color)
        else:
            painter.setBrush(QColor(0, 0, 0, 0))
        pen_color = QColor(0, 0, 0, 0)
        if self.outline_color is not None:
            pen_color = self.outline_color
        pen = QPen(pen_color)
        pen.setWidth(self.outline_width)
        painter.setPen(pen)
        painter.drawEllipse(self.x, self.y, 2 * rx, 2 * ry)


class Line:
    def __init__(self, sx, sy, ex, ey, outline_color, outline_width):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.outline_color = outline_color
        self.outline_width = outline_width

    def draw(self, painter):
        pen_color = QColor(0, 0, 0, 0)
        if self.outline_color is not None:
            pen_color = self.outline_color
        pen = QPen(pen_color)
        pen.setWidth(self.outline_width)
        painter.setPen(pen)
        painter.drawLine(self.sx, self.sy, self.ex, self.ey)

    
class Text:
    def __init__(self, x, y, txt, font_size, color, outline_color, outline_width):
        self.x = x
        self.y = y
        self.txt = txt
        self.font_size = font_size
        self.color = color
        self.outline_color = outline_color
        self.outline_width = outline_width

    def draw(self, painter):
        font = QFont()
        font.setPixelSize(self.font_size)
        painter.setFont(font)
        if self.color is not None:
            painter.setBrush(self.color)
        else:
            painter.setBrush(QColor(0, 0, 0, 0))
        pen_color = QColor(0, 0, 0, 0)
        if self.outline_color is not None:
            pen_color = self.outline_color
        pen = QPen(pen_color)
        pen.setWidth(self.outline_width)
        painter.setPen(pen)
        painter.drawText(QPoint(self.x, self.y), self.txt)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path(r"design.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(resource_path(r"logo.png"))))
        self.set_theme()

        # пока что не доделанные функции
        self.action_crop.setEnabled(False)
        # self.action_crop.setStyleSheet("""color: grey;""")
        self.action_warm.setEnabled(False)
        self.menu_4.setEnabled(False)
        self.toolBar.setEnabled(False)

        # основа
        self.page = QWidget()
        self.page.setLayout(self.main_layout)
        self.setCentralWidget(self.page)

        # требующиеся переменные
        self.flag_is_saved = False  # сохраняем первый раз или нет
        self.is_saved = False  # сохранены ли последние изменения
        self.do_paint = False
        self.objects = []
        self.instrument = "brush"
        self.font_size = 18
        self.fill_color = QColor(0, 0, 0)
        self.outline_color = QColor(0, 0, 0)
        self.outline_width = 1

        # Диалоги
        self.properties_dialog = PropertiesDialog(self)
        self.settings_dialog = SettingsDialog(self)
        self.image_size_dialog = ImageSizeDialog(self)
        self.opacity_dialog = OpacityDialog(self)
        self.brightness_dialog = BrightnessDialog(self)
        self.blur_dialog = BlurDialog(self)
        self.fill_color_dialog = FillColorDialog(self)
        self.outline_dialog = OutlineDialog(self)

        # Файл
        self.action_open.triggered.connect(self.open)
        self.action_save.triggered.connect(self.save_img)
        self.action_save_as.triggered.connect(self.save_as_img)
        self.action_close.triggered.connect(self.close_img)
        self.action_properties.triggered.connect(self.open_properties_dialog)
        self.action_settings.triggered.connect(self.open_settings_dialog)
        
        # Редактирование
        self.action_size.triggered.connect(self.open_img_dialog)
        self.action_rotate_clockwise.triggered.connect(self.rotate_img)
        self.action_rotate_counterclockwise.triggered.connect(self.rotate_img)
        self.action_rotate_arbitary.triggered.connect(self.rotate_img_arbitary)
        self.action_reflect_horizontal.triggered.connect(self.reflect_img)
        self.action_reflect_vertical.triggered.connect(self.reflect_img)

        # Эффекты
        self.action_opacity.triggered.connect(self.open_opacity_dialog)
        self.action_brightness.triggered.connect(self.open_brightness_dialog)
        self.action_blur.triggered.connect(self.open_blur_dialog)

        # Фильтры
        self.action_without_filters.triggered.connect(self.normal)
        self.action_grey.triggered.connect(self.grey)
        self.action_filter_sepia.triggered.connect(self.sepia)
        self.action_3d.triggered.connect(self.three_d)
        self.action_texture.triggered.connect(self.texture)

        # Инструменты
        self.action_rectangle.triggered.connect(self.setRectangle)
        self.action_circus.triggered.connect(self.setCircus)
        self.action_line.triggered.connect(self.setLine)
        self.action_text_2.triggered.connect(self.setTxt)
        self.action_color_fill.triggered.connect(self.open_color_dialog)
        self.action_outline.triggered.connect(self.open_outline_dialog)
        self.img_fill_color = Image.new(mode="RGB", size=(50, 50))

        self.action_rectangle.setIcon(QIcon(resource_path(r"rec.jpg")))
        self.action_circus.setIcon(QIcon(resource_path(r"circus.jpg")))
        self.action_line.setIcon(QIcon(resource_path(r"line.jpg")))
        self.action_text_2.setIcon(QIcon(resource_path(r"text.jpg")))

        # формируем и устанавливаем иконки цвета заливки и контура
        img = Image.open(resource_path(r"color.jpg"))
        pixels = img.load()
        x, y = img.size
        for i in range(y):
            for j in range(x):
                pixels[j, i] = 0, 0, 0
        img.save(resource_path(r"color.jpg"))
        self.action_color_fill.setIcon(QIcon(resource_path(r"color.jpg")))

        img = Image.open(resource_path(r"outline_color.jpg"))
        pixels = img.load()
        x, y = img.size
        for i in range(y):
            for j in range(x):
                pixels[j, i] = 0, 0, 0
        for i in range(20, y - 20):
            for j in range(20, x - 20):
                pixels[j, i] = 255, 255, 255
        img.save(resource_path(r"outline_color.jpg"))
        self.action_outline.setIcon(QIcon(resource_path(r"outline_color.jpg")))

    def set_theme(self):
        with open(resource_path(r"current_theme.txt"), encoding="utf-8") as f:
            theme_name = f.read()
        db_name = resource_path(r"theme_style.db")
        con = sqlite3.connect(db_name)
        cur = con.cursor()

        res_id_theme_name = cur.execute(f"""SELECT Type.id FROM Type INNER JOIN Theme ON Type.id = Theme.id_type WHERE Type.name = '{theme_name}'""")
        for elem in res_id_theme_name:
            id_theme_name = elem[0]

        res_hex_menu_color = cur.execute(f"""SELECT Color.hex_color FROM Color INNER JOIN Theme ON Color.id = Theme.id_menu_color WHERE id_type = {id_theme_name}""")
        for elem in res_hex_menu_color:
            hex_menu_color = elem[0]

        res_hex_toolbar_color = cur.execute(f"""SELECT Color.hex_color FROM Color INNER JOIN Theme ON Color.id = Theme.id_toolbar_color WHERE id_type = {id_theme_name}""")
        for elem in res_hex_toolbar_color:
            hex_toolbar_color = elem[0]

        res_hex_background_color = cur.execute(f"""SELECT Color.hex_color FROM Color INNER JOIN Theme ON Color.id = Theme.id_background_color WHERE id_type = {id_theme_name}""")
        for elem in res_hex_background_color:
            hex_background_color = elem[0]

        res_hex_text_color = cur.execute(f"""SELECT Color.hex_color FROM Color INNER JOIN Theme ON Color.id = Theme.id_text_color WHERE id_type = {id_theme_name}""")
        for elem in res_hex_text_color:
            hex_text_color = elem[0]

        cur.close()
        con.close()
 
        self.menubar.setStyleSheet(f"color: {hex_text_color}; background-color: {hex_menu_color}")
        self.toolBar.setStyleSheet(f"color: {hex_toolbar_color}; background-color: {hex_menu_color}")
        self.setStyleSheet(f"color: {hex_text_color}; background-color: {hex_background_color}")

    # Общие функции
    # сохранение изображения туда, куда хотел пользователь
    def save_cur_img(self, name):
        self.label_image.pixmap().save(name)

    # сохранение рабочих копий
    def save_working_img(self):
        self.working_copy_img.save(NEW_FILE)
        self.working_copy_img_without_filters.save(NEW_FILE_WITHOUT_FILTERS)
        self.working_copy_img_without_effects.save(NEW_FILE_WITHOUT_EFFECTS)

    def set_pixmap(self):
        # self.pixmap = QPixmap.fromImage(ImageQt(self.working_copy_img.copy()))
        self.pixmap = QPixmap(NEW_FILE)
        self.label_image.setPixmap(self.pixmap)

    # Размеры изображения на экране (ориентация по максимальной стороне)
    def set_view_size(self, w, h):
        if w > h:
            img_w = NORMAL_WIDTH
            img_h = int(NORMAL_WIDTH * h / w)
        else:
            img_h = NORMAL_HEIGHT
            img_w = int(NORMAL_HEIGHT * w / h)
        return (img_w, img_h)

    # Файл

    # Открываем изображение
    def open(self):
        fname = QFileDialog.getOpenFileName(self, 'Выберите изображение', ' ')[0]
        try:
            self.img = Image.open(fname)  # картика для сохранения
        except:
            return
        self.working_copy_img = self.img.copy()  # рабочая копия с фильтрами
        self.working_copy_img_without_filters = self.img.copy()  # рабочая копия без фильтров
        self.working_copy_img_without_effects = self.img.copy()  # рабочая копия без эффектов
        self.pixmap = QPixmap(fname)
        pixmap_w = self.pixmap.width()
        pixmap_h = self.pixmap.height()
        cur_size = self.set_view_size(pixmap_w, pixmap_h)
        self.label_image.setScaledContents(True)
        self.label_image.setFixedSize(*cur_size)
        self.label_image.setPixmap(self.pixmap)
        self.is_saved = False
    
    # Сохраняем текущие изменения
    # Если это первое сохранение, сохраняем изображение
    def save_img(self):
        self.is_saved = True
        if self.flag_is_saved is not True:
            self.save_as_img()
        else:
            self.save_cur_img(self.cur_filename)

    # Первое сохранение
    def save_as_img(self):
        self.is_saved = True
        filename = QFileDialog.getSaveFileName(self, "Сохранить как", ' ', 'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')
        self.cur_filename = filename[0]
        global PATH, NAME
        PATH = filename[0]
        ind = filename[0].rfind(r"/")
        NAME = filename[0][(ind + 1):]
        self.save_cur_img(self.cur_filename)
        self.flag_is_saved = True

    # Закрываем изображение
    def close_img(self):
        self.label_image.clear()

    # Свойства
    def open_properties_dialog(self):
        self.properties_dialog.name_value.setText(NAME)

        if self.flag_is_saved is True:
            x, y = self.working_copy_img.size
            self.properties_dialog.size_value.setText(f"{x} x {y}")
        else:
            self.properties_dialog.size_value.setText("?")

        txt = ''
        if self.flag_is_saved is False: 
            txt = "Изображение не сохранено"
        elif self.is_saved is False:
            txt = "Последние изменения не сохранены"
        else:
            txt = 'Сохранено'
        self.properties_dialog.saved_value.setText(txt)

        self.properties_dialog.path_value.setText(PATH)
        self.properties_dialog.open()

    # Настройки
    def open_settings_dialog(self):
        self.settings_dialog.open()

    # Редактирование

    # Изменение размеров изображения
    def open_img_dialog(self):
        w, h = self.working_copy_img.size
        self.image_size_dialog.set_size(w, h)
        self.image_size_dialog.open()

    def change_img_size(self, w, h):
        self.working_copy_img = self.working_copy_img.resize((w, h))
        self.working_copy_img_without_filters = self.working_copy_img_without_filters.resize((w, h))
        cur_size = self.set_view_size(w, h)
        self.label_image.setFixedSize(*cur_size)
        self.is_saved = False

    # Обрезка изображения
    def crop_img(self):
        pass

    # Повороты

    # Базовая функция для поворота изображения
    def do_rotate(self, angle):
        self.working_copy_img = self.working_copy_img.rotate(angle, expand=True, fillcolor=(255, 255, 255))
        self.working_copy_img_without_filters = self.working_copy_img_without_filters.rotate(angle, expand=True, fillcolor=(255, 255, 255))
        self.is_saved = False
        # self.save_working_img()
        pixmap_w = self.pixmap.width()
        pixmap_h = self.pixmap.height()
        cur_size = self.set_view_size(pixmap_h, pixmap_w)
        self.label_image.setFixedSize(*cur_size)
        self.save_working_img()
        self.set_pixmap()

    # Поворот на +-90 градусов
    def rotate_img(self):
        if self.sender() == self.action_rotate_clockwise:
            self.do_rotate(-90)
        else:
            self.do_rotate(90)

    # Поворот на произвольное количество градусов (от -360 до 360 включительно)
    def rotate_img_arbitary(self):
        angle, ok_pressed = QInputDialog.getInt(self, "Введите угол поворота",
                                                "Угол поворота (в градусах):", 90, -360, 360, 1)
        if ok_pressed:
            self.do_rotate(angle)

    # Отражения

    def reflect_img(self):
        if self.sender() == self.action_reflect_horizontal:
            self.working_copy_img = self.working_copy_img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            self.working_copy_img_without_filters = self.working_copy_img_without_filters.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        else:
            self.working_copy_img = self.working_copy_img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.working_copy_img_without_filters = self.working_copy_img_without_filters.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.is_saved = False
        self.save_working_img()
        self.set_pixmap()

    # Эффекты

    # Прозрачность
    def open_opacity_dialog(self):
        self.is_saved = False
        self.opacity_dialog.open()

    # Яркость
    def open_brightness_dialog(self):
        self.is_saved = False
        self.brightness_dialog.open()

    # Теплота
    def open_warmness_dialog(self):
        pass

    # Размытие
    def open_blur_dialog(self):
        self.is_saved = False
        self.blur_dialog.open()

    # Фильтры
    # Без фильтров (отмена фильтров, исходное изображение)
    def normal(self):
        self.working_copy_img = self.working_copy_img_without_filters.copy()
        self.working_copy_img_without_effects = self.working_copy_img_without_filters.copy()
        self.is_saved = False
        self.save_working_img()
        self.set_pixmap()
            
    # Градации серого
    def grey(self):
        self.working_copy_img = grey_filter(self.working_copy_img_without_filters.copy())
        self.working_copy_img_without_effects = self.working_copy_img.copy()
        self.is_saved = False
        self.save_working_img()
        self.set_pixmap()

    # Сепия
    def sepia(self):
        self.working_copy_img = sepia_filter(self.working_copy_img_without_filters.copy())
        self.working_copy_img_without_effects = self.working_copy_img.copy()
        self.is_saved = False
        self.save_working_img()
        self.set_pixmap()

    # 3d
    def three_d(self):
        self.working_copy_img = three_d_filter(self.working_copy_img_without_filters.copy())
        self.working_copy_img_without_effects = self.working_copy_img.copy()
        self.is_saved = False
        self.save_working_img()
        self.set_pixmap()

    # Наложение текстуры
    def texture(self):
        fname = QFileDialog.getOpenFileName(self, 'Выберите текстуру', ' ')[0]
        try:
            tx = Image.open(fname)
        except:
            return None
        self.working_copy_img = texture_filter(self.working_copy_img_without_filters.copy(), tx.copy())
        self.working_copy_img_without_effects = self.working_copy_img.copy()
        self.is_saved = False
        self.save_working_img()
        self.set_pixmap()

    # Инструменты
    # Событие рисования
    def paintEvent(self, event):
        if self.do_paint is True:
            painter = QPainter()
            painter.begin(self.pixmap)
            # print(self.objects)
            for obj in self.objects:
                obj.draw(painter)
            painter.end()
            self.label_image.setPixmap(self.pixmap)

    # Нажатие мыши
    def mousePressEvent(self, event):
        if self.instrument == "rectangle":
            self.objects.append(Rectangle(event.pos().x(), event.pos().y(),
                                        event.pos().x(), event.pos().y(),
                                        self.fill_color, self.outline_color, self.outline_width))
        elif self.instrument == "circus":
            self.objects.append(Circus(event.pos().x(), event.pos().y(),
                                    event.pos().x(), event.pos().y(),
                                    self.fill_color, self.outline_color, self.outline_width))
        elif self.instrument == "line":
            self.objects.append(Line(event.pos().x(), event.pos().y(),
                                    event.pos().x(), event.pos().y(),
                                    self.outline_color, self.outline_width))
        elif self.instrument == "text":
            self.objects.append(Text(event.pos().x(), event.pos().y(), "aaa",
                                    self.font_size, self.fill_color, self.outline_color, self.outline_width))
        self.repaint()

    # Передвижение мыши
    def mouseMoveEvent(self, event):
        if self.instrument == "rectangle":
            self.objects[-1].x2 = event.pos().x()
            self.objects[-1].y2 = event.pos().y()
        elif self.instrument == "circus":
            self.objects[-1].x2 = event.pos().x()
            self.objects[-1].y2 = event.pos().y()
        elif self.instrument == "line":
            self.objects[-1].ex = event.pos().x()
            self.objects[-1].ey = event.pos().y()
        self.repaint()

    # Нажатие клавиш
    def keyPressEvent(self, event):
        if self.instrument == "text":
            self.objects[-1].txt += event.text()

    # Установка инструментов
    def setRectangle(self):
        self.do_paint = True
        self.instrument = "rectangle"

    def setCircus(self):
        self.do_paint = True
        self.instrument = "circus"

    def setLine(self):
        self.do_paint = True
        self.instrument = "line"

    def setTxt(self):
        self.do_paint = True
        self.instrument = "text"
        font_size, ok_pressed = QInputDialog.getInt(
            self, "Размер шрифта", "Введите размер шрифта",
            18, 1, 100, 1)

        if ok_pressed:
            self.font_size = font_size

    def open_color_dialog(self):
        self.fill_color_dialog.open()

    def open_outline_dialog(self):
        self.outline_dialog.open()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon(r"logo.png"))
    win = Window()
    win.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())