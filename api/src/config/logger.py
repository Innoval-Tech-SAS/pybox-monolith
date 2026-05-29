"""
Sistema de logging con rotación diaria y organización mensual de archivos.

Este módulo proporciona un sistema de logging personalizado que organiza los logs
en carpetas mensuales y rota los archivos diariamente. Es esencial para el
monitoreo, debugging y auditoría del sistema, permitiendo un seguimiento detallado
de todas las operaciones del microservicio de administración de usuarios.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from tools.config_tools import get_or_throw


class MonthlyDailyRotatingFileHandler(TimedRotatingFileHandler):
    """
    Manejador de logs que rota archivos diariamente y crea carpetas mensuales.

    Esta clase extiende TimedRotatingFileHandler para organizar los logs en una
    estructura de carpetas por mes, facilitando la gestión y archivo de logs
    históricos del sistema.
    """

    def __init__(
        self,
        base_dir="./logs",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding=None,
    ):
        """
        Inicializa el manejador de rotación mensual-diaria.

        Args:
            base_dir: Directorio base donde se almacenarán los logs
            when: Cuándo rotar ('midnight' para rotación diaria)
            interval: Intervalo de rotación (1 para cada día)
            backupCount: Número de archivos de respaldo a mantener
            encoding: Codificación de archivos de log
        """
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.current_month = None
        log_path = self._get_log_path()
        super().__init__(
            log_path,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
        )

    def _get_log_path(self):
        """
        Genera la ruta del archivo de log basada en la fecha actual.

        Returns:
            str: Ruta completa del archivo de log para el día actual
        """
        now = datetime.now()
        month_folder = os.path.join(self.base_dir, now.strftime("%Y-%m"))
        os.makedirs(month_folder, exist_ok=True)
        return os.path.join(month_folder, now.strftime("%Y-%m-%d") + ".log")

    def doRollover(self):
        """
        Sobrescribe la rotación para manejar la creación de carpetas mensuales.

        Este método se ejecuta automáticamente cuando es necesario rotar el archivo
        de log, asegurando que se cree la estructura de carpetas apropiada.
        """
        self.stream.close()
        self.baseFilename = self._get_log_path()
        self.stream = self._open()


class Logger:
    """
    Clase singleton para manejo centralizado de logging del sistema.

    Esta clase configura y proporciona acceso a un logger que escribe tanto
    a consola como a archivos con rotación automática. Es fundamental para
    el monitoreo y debugging del sistema de administración de usuarios.
    """

    _ENVIROMENT = get_or_throw("ENV")

    @classmethod
    def get_logger(cls):
        """
        Obtiene la instancia singleton del logger.

        Returns:
            logging.Logger: Instancia configurada del logger del sistema
        """
        if not hasattr(cls, "_logger_instance"):
            cls._logger_instance = cls()
        return cls._logger_instance.logger

    def __init__(self):
        """
        Inicializa el logger con configuración para consola y archivo.

        Configura dos manejadores: uno para salida de consola y otro para
        archivos con rotación diaria y organización mensual.
        """
        self.logger = logging.getLogger("TEMPLATE")

        if not self.logger.hasHandlers():

            self.formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
            )

            if self._ENVIROMENT == "development":
                handler = logging.StreamHandler()
                handler.setLevel(logging.DEBUG)
                handler.setFormatter(self.formatter)
                self.logger.setLevel(logging.DEBUG)
            else:
                handler = MonthlyDailyRotatingFileHandler("./logs")
                handler.setLevel(logging.INFO)
                handler.setFormatter(self.formatter)
                self.logger.setLevel(logging.INFO)

            self.logger.propagate = False
            self.logger.addHandler(handler)


logger = Logger.get_logger()
