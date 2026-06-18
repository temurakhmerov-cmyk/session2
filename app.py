import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, conint
from queue_sys.manager import PrintQueueManager

# Инициализируем менеджер очереди
manager = PrintQueueManager()

# Добавим несколько стандартных принтеров по умолчанию
manager.register_printer("printer_1", "HP LaserJet Pro (Быстрый)", speed=2.5)  # 2.5 страницы в секунду
manager.register_printer("printer_2", "Epson L3150 (Цветной)", speed=1.0)     # 1.0 страница в секунду
manager.register_printer("printer_3", "Canon PIXMA (Офисный)", speed=1.5)     # 1.5 страницы в секунду

# Фоновая задача для симуляции течения времени
async def simulation_loop():
    try:
        while True:
            # Шаг симуляции 0.5 секунды
            await asyncio.sleep(0.5)
            manager.tick(0.5)
    except asyncio.CancelledError:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск фонового процесса симуляции
    sim_task = asyncio.create_task(simulation_loop())
    yield
    # Остановка при завершении работы приложения
    sim_task.cancel()
    try:
        await sim_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Print Queue Management System",
    description="Система управления очередью печати на основе двоичной кучи (Priority Queue/Heap)",
    lifespan=lifespan
)

# Модели запросов Pydantic
class JobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя документа")
    pages: int = Field(..., gte=1, lte=1000, description="Количество страниц")
    priority: int = Field(..., gte=1, lte=3, description="Приоритет: 1 - Высокий, 2 - Средний, 3 - Низкий")
    user: str = Field(..., min_length=1, max_length=50, description="Имя пользователя")

class PrinterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Название принтера")
    speed: float = Field(..., gt=0.1, lte=10.0, description="Скорость печати (стр/сек)")

# API Эндпоинты
@app.get("/api/state")
def get_state():
    """Получить текущее состояние всей системы."""
    return manager.get_state()

@app.post("/api/jobs")
def add_job(job: JobCreate):
    """Добавить новую задачу в очередь."""
    job_id = manager.add_job(job.name, job.pages, job.priority, job.user)
    return {"status": "success", "job_id": job_id}

@app.post("/api/printers")
def add_printer(printer: PrinterCreate):
    """Добавить новый принтер."""
    printer_id = f"printer_{len(manager.printers) + 1}"
    manager.register_printer(printer_id, printer.name, printer.speed)
    return {"status": "success", "printer_id": printer_id}

@app.post("/api/printers/{printer_id}/toggle")
def toggle_printer(printer_id: str):
    """Включить/выключить принтер."""
    if printer_id not in manager.printers:
        raise HTTPException(status_code=404, detail="Принтер не найден")
    manager.toggle_printer(printer_id)
    return {"status": "success"}

@app.post("/api/clear")
def clear_system():
    """Сбросить состояние симулятора."""
    manager.clear()
    return {"status": "success"}

@app.post("/api/generate-dummy")
def generate_dummy():
    """Сгенерировать случайные задачи в очередь на основе логических ролей."""
    import random
    
    # Шаблоны задач с логическим распределением приоритетов:
    # 1 (Высокий) - Деканат, Администратор, Ректорат (Срочные распоряжения, ведомости)
    # 2 (Средний) - Преподаватели (Методички, материалы лекций)
    # 3 (Низкий) - Студенты (Рефераты, курсовые, домашние работы)
    templates = [
        {"name": "Приказ_о_зачислении.pdf", "user": "Деканат", "priority": 1},
        {"name": "Срочное_распоряжение.docx", "user": "Администратор", "priority": 1},
        {"name": "Экзаменационная_ведомость_АиСД.xlsx", "user": "Деканат", "priority": 1},
        
        {"name": "Методичка_по_кучам.pdf", "user": "Преп. Васильев", "priority": 2},
        {"name": "Лекция_4_Двоичные_деревья.pptx", "user": "Доцент Петрова", "priority": 2},
        {"name": "Отчет_НИР_кафедры.docx", "user": "Профессор Смирнов", "priority": 2},
        
        {"name": "Реферат_по_физике.docx", "user": "Студент Иванов", "priority": 3},
        {"name": "Курсовая_работа_v3_исправлено.pdf", "user": "Студент Петров", "priority": 3},
        {"name": "Лабораторная_работа_3_код.py", "user": "Студентка Сидорова", "priority": 3},
        {"name": "Чертеж_детали_корпуса.dwg", "user": "Студент Смирнов", "priority": 3},
        {"name": "Фото_для_студбилета.jpg", "user": "Студентка Козлова", "priority": 3}
    ]
    
    # Генерируем от 3 до 5 задач
    num_jobs = random.randint(3, 5)
    selected_templates = random.sample(templates, min(num_jobs, len(templates)))
    
    for template in selected_templates:
        # Случайное число страниц от 5 до 60
        pages = random.randint(5, 60)
        manager.add_job(template["name"], pages, template["priority"], template["user"])
        
    return {"status": "success", "generated_count": len(selected_templates)}

# Подключение статических файлов для фронтенда
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    """Отдает главную HTML-страницу."""
    return FileResponse("static/index.html")
