import socket
import time
from datetime import datetime

# Функция получения данных из файла конфигурации
def load_config(config_file):
    try:
        with open(config_file, "r") as f:
            # Читаем и очищаем строки, игнорируя пустые
            lines = [line.strip() for line in f.readlines() if line.strip()]

            # Проверяем, что файл содержит как минимум 2 строки
            if len(lines) < 2:
                raise ValueError("Конфигурационный файл должен содержать как минимум 2 строки (host и port)")

            # Получаем ip-адрес (первая строка)
            if '=' not in lines[0]:
                raise ValueError("Неверный формат строки. Ожидается: ip=значение")
            host = lines[0].split('=')[1].strip()

            # Получаем port (вторая строка)
            if '=' not in lines[1]:
                raise ValueError("Неверный формат строки port. Ожидается: port=значение")
            port = int(lines[1].split('=')[1].strip())

            return host, port

    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации {config_file} не найден")
        raise
    except ValueError as e:
        print(f"Ошибка в конфигурационном файле: {e}")
        raise


# Функция записи данных в лог-файл
def write_log(log_file, message):
    # Удаляем BOM если он есть
    message = message.replace('\ufeff', '')
    with open(log_file, "a", encoding='utf-8') as f:
        f.write(message + "\n")


# Функция для разворота строки
def mirror_string(s):
    return s[::-1]


# Функция для обработки клиента
def handle_client(conn, addr, log_file):
    connect_time = datetime.now()
    write_log(log_file, f"Клиент подключен: {connect_time}, Адрес: {addr}")

    try:
        while True:
            # Получаем данные от клиента, максимум 1024 байта
            data = conn.recv(1024).decode()

            # Если соединение разорвано
            if not data:
                break

            # Ввод данных в лог-файл
            receive_time = datetime.now()
            write_log(log_file, f"Получено сообщение: {receive_time}, Сообщение: {data}")

            # Эмуляция обработки сервера
            time.sleep(5)

            # Формируем ответ: зеркальная строка + информация о сервере
            mirrored = mirror_string(data)
            response = f"{mirrored}. Сервер написан Исаевым М.А.\n"

            # Отправляем ответ клиенту
            conn.send(response.encode('utf-8'))

            send_time = datetime.now()
            write_log(log_file, f"Отправлено сообщение: {send_time}, Сообщение: {response}")

            # Отключение клиента через 30 секунд после подключения
            if (datetime.now() - connect_time).total_seconds() > 30:
                break

    finally:
        # Закрываем соединение
        disconnect_time = datetime.now()
        write_log(log_file, f"Клиент отключен: {disconnect_time}, Адрес: {addr}")
        conn.close()


# Функция запуски сервера
def run_server():
    # Загружаем конфигурацию
    host, port = load_config("server_config.txt")
    log_file = "server_log.txt"

    # Записываем время запуска сервера
    start_time = datetime.now()
    write_log(log_file, f"Сервер запущен: {start_time}")

    # Создаем сокет
    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        print(f"Сервер запущен на {host}:{port}. Ожидание подключений...")

        try:
            while True:
                # Принимаем подключение
                conn, addr = s.accept()
                print(f"Подключен клиент: {addr}")

                # Обрабатываем клиента
                handle_client(conn, addr, log_file)

        except KeyboardInterrupt:
            print("\nСервер остановлен")
        finally:
            s.close()


if __name__ == "__main__":
    run_server()

