import time

class PrintJob:
    """Модель задачи печати."""
    def __init__(self, job_id: str, name: str, pages: int, priority: int, user: str):
        self.id = job_id
        self.name = name
        self.pages = pages
        self.priority = priority  # 1 - Высокий, 2 - Средний, 3 - Низкий
        self.user = user
        self.created_at = time.time()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "pages": self.pages,
            "priority": self.priority,
            "user": self.user,
            "created_at": self.created_at
        }


class Printer:
    """Модель принтера с симуляцией процесса печати."""
    def __init__(self, printer_id: str, name: str, speed: float = 1.0):
        self.id = printer_id
        self.name = name
        self.speed = speed  # Количество страниц в секунду
        self.status = "idle"  # Возможные статусы: idle (свободен), printing (печать), offline (отключен)
        self.current_job = None
        self.remaining_pages = 0.0

    def assign_job(self, job: PrintJob):
        """Назначает принтеру задачу для печати."""
        self.current_job = job
        self.status = "printing"
        self.remaining_pages = float(job.pages)

    def set_offline(self):
        """Отключает принтер. Если шла печать, задача прерывается и сбрасывается."""
        returned_job = self.current_job
        self.status = "offline"
        self.current_job = None
        self.remaining_pages = 0.0
        return returned_job

    def set_online(self):
        """Включает принтер в сеть."""
        if self.status == "offline":
            self.status = "idle"

    def tick(self, delta_time: float):
        """
        Обновляет состояние принтера за прошедшее время (delta_time в секундах).
        Возвращает завершенную задачу PrintJob, если печать закончилась, иначе None.
        """
        if self.status != "printing" or not self.current_job:
            return None

        # Печатаем страницы пропорционально времени и скорости
        printed = self.speed * delta_time
        self.remaining_pages -= printed

        if self.remaining_pages <= 0:
            completed_job = self.current_job
            self.current_job = None
            self.status = "idle"
            self.remaining_pages = 0.0
            return completed_job

        return None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "speed": self.speed,
            "status": self.status,
            "current_job": self.current_job.to_dict() if self.current_job else None,
            "remaining_pages": max(0, int(round(self.remaining_pages)))
        }
