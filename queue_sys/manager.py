import time
from .heap import MinHeap
from .models import PrintJob, Printer

class PrintQueueManager:
    """
    Менеджер управления очередью печати.
    Координирует работу приоритетной очереди (кучи) и принтеров.
    """
    def __init__(self):
        self.heap = MinHeap()
        self.printers = {}
        self.completed_jobs = []
        self.logs = []
        self.job_id_counter = 0

    def add_log(self, message: str):
        """Добавляет запись в лог с меткой времени."""
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        # Ограничиваем лог последними 100 записями
        if len(self.logs) > 100:
            self.logs.pop(0)

    def register_printer(self, printer_id: str, name: str, speed: float = 1.0):
        """Регистрирует новый принтер в системе."""
        printer = Printer(printer_id, name, speed)
        self.printers[printer_id] = printer
        self.add_log(f"Принтер '{name}' подключен к системе (скорость: {speed} стр/сек).")

    def add_job(self, name: str, pages: int, priority: int, user: str) -> str:
        """
        Создает и добавляет новую задачу в очередь печати.
        Приоритет: 1 - Высокий, 2 - Средний, 3 - Низкий.
        """
        self.job_id_counter += 1
        job_id = f"JOB_{self.job_id_counter:03d}"
        
        job = PrintJob(job_id, name, pages, priority, user)
        self.heap.insert(job, priority)
        
        priority_names = {1: "Высокий", 2: "Средний", 3: "Низкий"}
        p_name = priority_names.get(priority, str(priority))
        self.add_log(f"Добавлена задача {job_id}: '{name}' ({pages} стр.), автор: {user}, приоритет: {p_name}.")
        
        # Сразу пытаемся распределить задачи
        self.dispatch_jobs()
        return job_id

    def dispatch_jobs(self):
        """
        Распределяет задачи из очереди по свободным принтерам.
        Поддерживает вытеснение (preemption): если в куче появляется более приоритетная задача,
        чем те, что печатаются на принтерах, то принтер с наименее приоритетной задачей прерывается.
        """
        # Шаг 1: Сначала раздаем задачи свободным принтерам
        for printer in self.printers.values():
            if printer.status == "idle" and not self.heap.is_empty():
                job = self.heap.extract_min()
                if job:
                    printer.assign_job(job)
                    self.add_log(f"Принтер '{printer.name}' начал печать задачи {job.id}: '{job.name}'.")

        # Шаг 2: Вытесняющая приоритетная печать (Preemption)
        # Если в куче все еще есть задачи, проверяем, не вытесняют ли они текущие задачи на принтерах.
        while not self.heap.is_empty():
            # Заглядываем в корень кучи (наивысший приоритет из ожидающих)
            heap_job = self.heap.peek()
            if not heap_job:
                break
                
            # Ищем занятые принтеры, у которых приоритет задачи ниже (числовое значение больше), чем у heap_job.
            # Нам нужно вытеснить самый низкий приоритет из выполняющихся.
            preemptable_printers = [
                p for p in self.printers.values()
                if p.status == "printing" and p.current_job and p.current_job.priority > heap_job.priority
            ]
            
            if not preemptable_printers:
                # Если никто не печатает задачи с более низким приоритетом, прерываем цикл вытеснения.
                break
                
            # Сортируем принтеры так, чтобы в начале списка были принтеры с наименьшим приоритетом текущей задачи 
            # (наибольшим числовым значением) и наибольшим количеством оставшихся страниц.
            preemptable_printers.sort(key=lambda p: (p.current_job.priority, p.remaining_pages), reverse=True)
            
            # Принтер для вытеснения
            printer_to_preempt = preemptable_printers[0]
            
            # Извлекаем более приоритетную задачу из кучи
            high_prio_job = self.heap.extract_min()
            if not high_prio_job:
                break
            
            # Прерываем принтер
            interrupted_job = printer_to_preempt.current_job
            
            # Сохраняем оставшиеся страницы (округляем в большую сторону, минимум 1 страница)
            interrupted_job.pages = max(1, int(round(printer_to_preempt.remaining_pages)))
            
            # Сбрасываем принтер (set_offline сбрасывает текущую задачу)
            printer_to_preempt.set_offline()
            # Возвращаем принтер в статус готовности (idle)
            printer_to_preempt.set_online()
            
            # Возвращаем прерванную задачу обратно в кучу
            self.heap.insert(interrupted_job, interrupted_job.priority)
            
            # Назначаем новую супер-приоритетную задачу
            printer_to_preempt.assign_job(high_prio_job)
            
            self.add_log(
                f"Печать задачи {interrupted_job.id} ('{interrupted_job.name}') приостановлена (осталось {interrupted_job.pages} стр.). "
                f"Принтер '{printer_to_preempt.name}' переключен на более приоритетную задачу {high_prio_job.id}: '{high_prio_job.name}'."
            )

    def toggle_printer(self, printer_id: str):
        """Переключает состояние принтера (в сети / вне сети)."""
        if printer_id not in self.printers:
            return

        printer = self.printers[printer_id]
        if printer.status == "offline":
            printer.set_online()
            self.add_log(f"Принтер '{printer.name}' вернулся в сеть (готов к работе).")
            self.dispatch_jobs()
        else:
            # Если принтер печатал, возвращаем задачу обратно в кучу
            interrupted_job = printer.set_offline()
            self.add_log(f"Принтер '{printer.name}' отключен от сети.")
            if interrupted_job:
                # Возвращаем задачу в кучу с ее оригинальным приоритетом
                self.heap.insert(interrupted_job, interrupted_job.priority)
                self.add_log(f"Печать задачи {interrupted_job.id} прервана. Задача возвращена в очередь.")

    def tick(self, delta_time: float):
        """
        Продвигает симуляцию времени на delta_time секунд.
        Обновляет статус принтеров и распределяет новые задачи.
        """
        for printer in self.printers.values():
            completed_job = printer.tick(delta_time)
            if completed_job:
                self.completed_jobs.append(completed_job)
                self.add_log(f"Принтер '{printer.name}' завершил печать задачи {completed_job.id}: '{completed_job.name}'.")
        
        # Распределяем задачи по освободившимся принтерам
        self.dispatch_jobs()

    def get_state(self):
        """Возвращает текущее состояние системы для отображения во фронтенде."""
        return {
            "printers": [p.to_dict() for p in self.printers.values()],
            "heap": self.heap.get_array(),
            "heap_size": self.heap.size(),
            "completed_jobs": [j.to_dict() for j in self.completed_jobs[-15:]], # Возвращаем последние 15
            "logs": self.logs[-20:] # Возвращаем последние 20 логов
        }

    def clear(self):
        """Сброс состояния системы."""
        self.heap.clear()
        self.completed_jobs = []
        self.logs = []
        self.job_id_counter = 0
        for printer in self.printers.values():
            printer.status = "idle"
            printer.current_job = None
            printer.remaining_pages = 0.0
        self.add_log("Система сброшена в исходное состояние.")
