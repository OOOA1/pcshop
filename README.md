PC Shop Tracker
PC Shop Tracker — это ERP-система на базе фреймворка Django, предназначенная для автоматизации учета комплектующих, управления процессом сборки рабочих станций и финансового анализа деятельности предприятия.

Приложение реализует полный цикл учета: от планирования закупок и оприходования товара на склад до реализации готовой продукции и расчета чистой прибыли с учетом амортизации и комиссионных сборов.

Техническое описание
Проект построен на архитектуре MTV (Model-Template-View) и использует стандартный стек технологий Django.

Стек технологий
Backend: Python 3, Django 5.2.10

СУБД: SQLite (конфигурация по умолчанию для dev-среды)

Template Engine: Django Templates (DTL)

Frontend: HTML5, CSS3, JavaScript (Chart.js для визуализации данных)

Медиа: Библиотека Pillow для обработки изображений товаров и сборок

Ключевые модули и архитектура
Проект разделен на конфигурационную директорию pcshop и основное приложение tracker, инкапсулирующее бизнес-логику.

1. Модели данных (tracker/models.py)
Система базируется на реляционной модели данных, описывающей сущности предметной области:

InventoryItem: Модель единицы хранения (SKU). Поддерживает категоризацию (CPU, GPU, RAM и др.), хранение серийных номеров и отслеживание жизненного цикла товара через статусы (in_stock, installed, sold, written_off).

Build: Сущность сборки (системного блока).

Реализует динамический расчет себестоимости через свойство @property cost, агрегирующее стоимость связанных компонентов (BuildItem) и расходных материалов (BuildConsumable).

Содержит поле work_hours для учета трудозатрат.

Sale: Модель транзакции продажи.

Инкапсулирует логику финансового расчета: при сохранении экземпляра автоматически вычисляется сумма комиссии (на основе fees_percentage) и фиксируется чистая прибыль.

Триггерит изменение статусов связанных объектов (Сборки или Товара) на SOLD.

PurchasePlan: Модель планирования закупок (Wishlist) с флагом состояния приобретения.

2. Бизнес-логика и контроллеры (tracker/views.py)
Обработка запросов реализована преимущественно на Class-Based Views (CBV) с использованием миксина LoginRequiredMixin для разграничения доступа.

DashboardView: Агрегатор аналитических данных. Выполняет ORM-запросы для вычисления:

Общей выручки и чистой прибыли.

Текущей стоимости складских остатков.

Подготовки JSON-структур для рендеринга графиков динамики продаж и распределения прибыли по категориям.

InventoryListView: Реализует функционал фильтрации QuerySet по параметрам GET-запроса (поиск по Q-объектам для имени/серийного номера, фильтрация по статусу и категории, сортировка).

BuildDetailView: Контроллер детального просмотра сборки. Обрабатывает POST-запросы для добавления компонентов и списания расходных материалов в контексте конкретной сборки.

3. Конфигурация (pcshop/settings.py)
Локализация: Установлен код языка ru-ru и часовой пояс Asia/Yekaterinburg.

Безопасность: Настроены параметры авторизации с перенаправлением на дашборд (LOGIN_REDIRECT_URL = 'dashboard').

Установка и развертывание
Инструкция по развертыванию проекта в локальной среде разработки.

Клонирование репозитория

git clone <URL_репозитория>
cd pcshop
Инициализация виртуального окружения и установка зависимостей


python -m venv venv
# Для Windows
venv\Scripts\activate
# Для Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
Применение миграций базы данных


python manage.py migrate
Создание администратора Для доступа к административной панели управления.


python manage.py createsuperuser
Запуск сервера разработки

python manage.py runserver
Приложение будет доступно по адресу: http://127.0.0.1:8000/

Диаграмимы:
<img width="619" height="475" alt="image" src="https://github.com/user-attachments/assets/1153ffa1-b3ed-49b6-a572-a4e5438bee34" />

<img width="652" height="419" alt="image" src="https://github.com/user-attachments/assets/2fa5815f-fa8f-47ce-80c6-d26256ea7fe7" />

<img width="771" height="475" alt="image" src="https://github.com/user-attachments/assets/3c427904-8ad9-4880-a85b-e12f44bb2276" />

<img width="890" height="438" alt="image" src="https://github.com/user-attachments/assets/855b61cc-190f-4465-b8c8-1be733968aed" />

<img width="876" height="480" alt="image" src="https://github.com/user-attachments/assets/693d74ae-e01f-4c34-b64e-bba0ce7bc687" />

<img width="1225" height="218" alt="image" src="https://github.com/user-attachments/assets/1d1e7d3b-76b3-4df9-81aa-545a2fae9826" />

<img width="1002" height="617" alt="image" src="https://github.com/user-attachments/assets/5b06e4fb-b576-4d95-9375-28a1f535730c" />

<img width="725" height="654" alt="image" src="https://github.com/user-attachments/assets/0ca5a091-fbba-4c1c-a12f-f1fcacc1c3d0" />

<img width="627" height="467" alt="image" src="https://github.com/user-attachments/assets/4ce7785b-552a-4f54-80a9-a5900b851bba" />

<img width="593" height="648" alt="image" src="https://github.com/user-attachments/assets/b331db3b-7090-4d1c-8b5c-4c47636890b4" />

<img width="843" height="541" alt="image" src="https://github.com/user-attachments/assets/34729f22-5076-41c3-8a89-cea0d4b0b002" />

<img width="721" height="313" alt="image" src="https://github.com/user-attachments/assets/d7552bfb-a5ed-48a2-8e4c-440bf5bf249c" />

<img width="748" height="369" alt="image" src="https://github.com/user-attachments/assets/61151a7a-395c-4393-abca-b554fba2e222" />

<img width="560" height="301" alt="image" src="https://github.com/user-attachments/assets/5eb4e23c-ec1a-4422-92c7-7f39d637a246" />
