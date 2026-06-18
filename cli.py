import time
import sys
from queue_sys.manager import PrintQueueManager

# Настройка кодировки для корректного отображения кириллицы в консоли Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def print_divider():
    print("-" * 60)

def main():
    manager = PrintQueueManager()
    
    # Регистрация принтеров
    manager.register_printer("P1", "HP LaserJet (Быстрый)", speed=2.0)
    manager.register_printer("P2", "Epson Inkjet (Медленный)", speed=0.5)

    print("=== Симуляция Системы Очереди Печати (CLI) ===")
    print("Используется собственная реализация двоичной кучи (Min-Heap)")
    print_divider()

    # Добавление тестовых задач
    print("Добавление задач в очередь...")
    manager.add_job("Дипломная_работа.pdf", pages=30, priority=2, user="Студент Петров")
    manager.add_job("Приказ_Ректора.docx", pages=5, priority=1, user="Ректорат")
    manager.add_job("Фото_кафедры.jpg", pages=15, priority=3, user="Лаборант")
    manager.add_job("Расписание.xlsx", pages=10, priority=2, user="Учебная часть")
    manager.add_job("Срочная_объявка.txt", pages=2, priority=1, user="Деканат")

    print_divider()
    print("Состояние очереди после заполнения:")
    state = manager.get_state()
    for idx, entry in enumerate(state["heap"]):
        job = entry["item"]
        print(f"  [{idx}] {job.id}: {job.name} | Приоритет: {job.priority} | Страниц: {job.pages} (Автор: {job.user})")
    print_divider()

    print("Начинаем пошаговую симуляцию печати (шаг = 5 секунд):")
    # Сделаем 5 шагов по 5 секунд каждый
    for step in range(1, 7):
        print(f"\n--- Шаг {step} (прошло {step * 5} сек.) ---")
        manager.tick(5.0)
        
        state = manager.get_state()
        print("Состояние принтеров:")
        for printer in state["printers"]:
            if printer["status"] == "printing" and printer["current_job"]:
                print(f"  {printer['name']}: Печать '{printer['current_job']['name']}' (осталось {printer['remaining_pages']} стр.)")
            elif printer["status"] == "idle":
                print(f"  {printer['name']}: Свободен")
            else:
                print(f"  {printer['name']}: Отключен")

        print(f"Задач в очереди кучи: {state['heap_size']}")
        
        # Если все принтеры свободны и очередь пуста, заканчиваем симуляцию
        active_printing = any(p["status"] == "printing" for p in state["printers"])
        if state["heap_size"] == 0 and not active_printing:
            print("\nОчередь пуста, все задачи напечатаны!")
            break
            
        time.sleep(1.0) # Задержка для читаемости вывода в консоли

    print_divider()
    print("Выполненные задачи:")
    state = manager.get_state()
    for job in state["completed_jobs"]:
        print(f"  - {job['id']}: '{job['name']}' ({job['pages']} стр.), автор: {job['user']}")
    print_divider()
    print("Логи симулятора:")
    for log in state["logs"]:
        print(log)
    print("==============================================")

if __name__ == "__main__":
    main()
