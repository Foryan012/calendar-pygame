import pygame
import sys
import json
import os
from datetime import datetime, date, timedelta
import calendar

# Инициализация Pygame
pygame.init()
pygame.key.set_repeat(500, 50)  # Для повторения клавиш при зажатии

# Константы
WIDTH, HEIGHT = 900, 700
FPS = 30
BG_COLOR = (240, 240, 240)
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER = (170, 170, 170)
CALENDAR_HEADER = (100, 100, 100)
CELL_COLOR = (255, 255, 255)
CELL_BORDER = (180, 180, 180)
TODAY_COLOR = (200, 230, 255)
SELECTED_COLOR = (255, 255, 180)
EVENT_COLOR = (220, 255, 220)      # Светло-зеленый для дней с событиями
FONT_SIZE = 20
FONT_SIZE_SMALL = 16
INPUT_BG = (250, 250, 250)

# Шрифты
font = pygame.font.Font(None, FONT_SIZE)
small_font = pygame.font.Font(None, FONT_SIZE_SMALL)

# Загрузка данных
DATA_FILE = "diary.json"
data = {}
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

class Button:
    def __init__(self, x, y, w, h, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 2)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                return True
        return False

class TextBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.active = False
        self.text = ""
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                # Enter - добавить событие (будет обработано в основном коде)
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                # Добавляем символ, если он печатный
                if event.unicode.isprintable():
                    self.text += event.unicode
        return False

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:  # мигание каждые 500 мс
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        color = (100, 100, 255) if self.active else (200, 200, 200)
        pygame.draw.rect(screen, INPUT_BG, self.rect)
        pygame.draw.rect(screen, color, self.rect, 2)
        # Отображение текста
        text_surf = font.render(self.text, True, TEXT_COLOR)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
        # Курсор
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + text_surf.get_width()
            pygame.draw.line(screen, TEXT_COLOR, (cursor_x, self.rect.y + 5),
                             (cursor_x, self.rect.y + self.rect.height - 5), 2)

class Calendar:
    def __init__(self, x, y, cell_w, cell_h):
        self.x = x
        self.y = y
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.current_date = date.today()
        self.selected_date = self.current_date
        self.days = []  # список дней для отображения

    def update_days(self):
        """Заполняет self.days днями текущего месяца (включая пустые ячейки)"""
        cal = calendar.Calendar()
        month_days = cal.monthdays2calendar(self.current_date.year, self.current_date.month)
        self.days = []
        for week in month_days:
            for day, weekday in week:
                self.days.append(day)

    def draw(self, screen, data):
        """Рисует календарь, выделяя цветом дни с событиями (data)"""
        # Заголовок с месяцем и годом
        month_year = self.current_date.strftime("%B %Y")
        text = font.render(month_year, True, TEXT_COLOR)
        screen.blit(text, (self.x, self.y - 30))

        # Дни недели
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, wd in enumerate(weekdays):
            wd_surf = small_font.render(wd, True, TEXT_COLOR)
            wd_x = self.x + i * self.cell_w + self.cell_w // 2 - wd_surf.get_width() // 2
            screen.blit(wd_surf, (wd_x, self.y - 20))

        # Рисуем сетку
        for i, day in enumerate(self.days):
            row = i // 7
            col = i % 7
            cell_x = self.x + col * self.cell_w
            cell_y = self.y + row * self.cell_h
            cell_rect = pygame.Rect(cell_x, cell_y, self.cell_w, self.cell_h)

            # Определяем цвет ячейки
            if day != 0:
                cell_date = date(self.current_date.year, self.current_date.month, day)
                # Проверяем наличие событий в data
                has_events = data and cell_date.isoformat() in data and data[cell_date.isoformat()]
                if cell_date == date.today():
                    color = TODAY_COLOR
                elif cell_date == self.selected_date:
                    color = SELECTED_COLOR
                elif has_events:
                    color = EVENT_COLOR
                else:
                    color = CELL_COLOR
            else:
                color = CELL_COLOR

            pygame.draw.rect(screen, color, cell_rect)
            pygame.draw.rect(screen, CELL_BORDER, cell_rect, 1)

            if day != 0:
                day_text = small_font.render(str(day), True, TEXT_COLOR)
                screen.blit(day_text, (cell_x + 5, cell_y + 5))

    def handle_click(self, pos):
        """Обрабатывает клик по календарю, возвращает выбранную дату или None"""
        for i, day in enumerate(self.days):
            if day == 0:
                continue
            row = i // 7
            col = i % 7
            cell_x = self.x + col * self.cell_w
            cell_y = self.y + row * self.cell_h
            cell_rect = pygame.Rect(cell_x, cell_y, self.cell_w, self.cell_h)
            if cell_rect.collidepoint(pos):
                return date(self.current_date.year, self.current_date.month, day)
        return None

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ежедневник")
    clock = pygame.time.Clock()

    # Создаем элементы интерфейса
    # Календарь сдвинут ниже: y = 130 (было 100)
    calendar = Calendar(50, 130, 80, 60)
    calendar.update_days()

    # Кнопки для смены месяца
    prev_month_btn = Button(50, 50, 80, 30, "<")
    next_month_btn = Button(140, 50, 80, 30, ">")

    # Поле ввода
    textbox = TextBox(650, 500, 200, 30)

    # Кнопка добавления события
    add_btn = Button(650, 540, 100, 30, "Добавить")

    # Область отображения событий
    events_rect = pygame.Rect(650, 100, 200, 380)

    # Выбранная дата
    selected_date = date.today()

    running = True
    dt = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                save_data()

            # Обработка кнопок
            if prev_month_btn.handle_event(event):
                calendar.current_date = calendar.current_date.replace(day=1) - timedelta(days=1)
                calendar.update_days()
                # Сброс выбранной даты на первый день нового месяца
                calendar.selected_date = date(calendar.current_date.year, calendar.current_date.month, 1)

            if next_month_btn.handle_event(event):
                # Переход на следующий месяц
                next_month = calendar.current_date.replace(day=28) + timedelta(days=4)
                calendar.current_date = next_month.replace(day=1)
                calendar.update_days()
                calendar.selected_date = date(calendar.current_date.year, calendar.current_date.month, 1)

            # Обработка кликов по календарю
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_date = calendar.handle_click(event.pos)
                if clicked_date:
                    calendar.selected_date = clicked_date
                    selected_date = clicked_date

            # Обработка текстового поля
            textbox.handle_event(event)

            # Добавление события по кнопке или Enter
            if add_btn.handle_event(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and textbox.active):
                if textbox.text.strip():
                    date_key = selected_date.isoformat()
                    if date_key not in data:
                        data[date_key] = []
                    data[date_key].append(textbox.text.strip())
                    textbox.text = ""
                    save_data()

            # Удаление события по клику на него в списке
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if events_rect.collidepoint(event.pos):
                    # Определяем, на каком событии кликнули
                    date_key = selected_date.isoformat()
                    if date_key in data:
                        # Вычисляем индекс по координате Y
                        y_offset = event.pos[1] - events_rect.y - 5
                        if y_offset >= 0:
                            line_height = 25
                            index = y_offset // line_height
                            if 0 <= index < len(data[date_key]):
                                del data[date_key][index]
                                save_data()

        # Обновление
        textbox.update(dt)

        # Отрисовка
        screen.fill(BG_COLOR)

        # Рисуем календарь с передачей данных для подсветки дней с событиями
        calendar.draw(screen, data)

        # Кнопки
        prev_month_btn.draw(screen)
        next_month_btn.draw(screen)

        # Заголовок для событий
        events_title = font.render(f"События на {selected_date.strftime('%d.%m.%Y')}:", True, TEXT_COLOR)
        screen.blit(events_title, (650, 70))

        # Список событий
        date_key = selected_date.isoformat()
        if date_key in data:
            events = data[date_key]
            y = events_rect.y + 5
            for i, ev in enumerate(events):
                ev_text = small_font.render(f"{i+1}. {ev}", True, TEXT_COLOR)
                if ev_text.get_width() > events_rect.width - 10:
                    # Обрезаем текст, если слишком длинный
                    while ev_text.get_width() > events_rect.width - 10 and len(ev) > 3:
                        ev = ev[:-1]
                        ev_text = small_font.render(f"{i+1}. {ev}...", True, TEXT_COLOR)
                screen.blit(ev_text, (events_rect.x + 5, y))
                y += 25
                if y > events_rect.y + events_rect.height - 30:
                    break  # Не выходим за границы

        # Поле ввода и кнопка
        textbox.draw(screen)
        add_btn.draw(screen)

        pygame.display.flip()
        dt = clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()