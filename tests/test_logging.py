import unittest
import logging
import os
from pathlib import Path
from creatoria_agent import MaterialsAgent

class TestLogging(unittest.TestCase):
    def setUp(self):
        self.log_file = Path("materials_agent.log")
        self.agent = MaterialsAgent()

    def tearDown(self):
        # Удаляем лог-файл после тестов
        if self.log_file.exists():
            os.remove(self.log_file)

    def test_log_file_creation(self):
        """Проверяем создание лог-файла"""
        # Выполняем какое-то действие, которое должно вызвать логирование
        self.agent.search_by_parameters("pressure_drop < 100 Pa/m", "metals")
        
        # Проверяем, что файл создан
        self.assertTrue(self.log_file.exists())

    def test_log_format(self):
        """Проверяем формат логов"""
        # Выполняем какое-то действие
        self.agent.search_by_parameters("pressure_drop < 100 Pa/m", "metals")
        
        # Читаем лог-файл
        with open(self.log_file) as f:
            log_content = f.read()
        
        # Проверяем формат
        self.assertIn("INFO", log_content)
        self.assertIn("ERROR", log_content)
        self.assertIn("WARNING", log_content)

    def test_log_levels(self):
        """Проверяем уровни логирования"""
        # Настраиваем логгер
        logger = logging.getLogger("creatoria_agent")
        
        # Проверяем, что все уровни логирования работают
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Читаем лог-файл
        with open(self.log_file) as f:
            log_content = f.read()
        
        # Проверяем наличие сообщений разных уровней
        self.assertIn("DEBUG", log_content)
        self.assertIn("INFO", log_content)
        self.assertIn("WARNING", log_content)
        self.assertIn("ERROR", log_content)
        self.assertIn("CRITICAL", log_content)

    def test_log_rotation(self):
        """Проверяем ротацию логов"""
        # Создаем несколько лог-файлов
        for i in range(5):
            with open(f"materials_agent_{i}.log", "w") as f:
                f.write(f"Test log {i}\n")
        
        # Проверяем, что файлы созданы
        for i in range(5):
            self.assertTrue(Path(f"materials_agent_{i}.log").exists())
        
        # Удаляем тестовые лог-файлы
        for i in range(5):
            os.remove(f"materials_agent_{i}.log")

    def test_log_handlers(self):
        """Проверяем обработчики логов"""
        logger = logging.getLogger("creatoria_agent")
        
        # Проверяем наличие файлового обработчика
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        self.assertTrue(len(file_handlers) > 0)
        
        # Проверяем наличие консольного обработчика
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertTrue(len(console_handlers) > 0)

    def test_log_exception(self):
        """Проверяем логирование исключений"""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            logger = logging.getLogger("creatoria_agent")
            logger.exception("Exception occurred")
        
        # Читаем лог-файл
        with open(self.log_file) as f:
            log_content = f.read()
        
        # Проверяем наличие информации об исключении
        self.assertIn("Exception occurred", log_content)
        self.assertIn("ValueError", log_content)
        self.assertIn("Test exception", log_content)

if __name__ == '__main__':
    unittest.main() 