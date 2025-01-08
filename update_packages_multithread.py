import sys
import subprocess
import logging
import asyncio
from tqdm.asyncio import tqdm  # Для асинхронного прогресс-бара

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Асинхронная функция для обновления пакета
async def update_package(package):
    try:
        logger.info(f"Обновление пакета {package}...")
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "--upgrade", package,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.info(f"Пакет {package} успешно обновлен.")
        else:
            logger.error(f"Ошибка при обновлении пакета {package}: {stderr.decode()}")
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при обновлении пакета {package}: {e}")

# Асинхронная функция для получения списка устаревших библиотек
async def get_outdated_packages():
    try:
        result = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "list", "--outdated",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await result.communicate()

        if result.returncode != 0:
            logger.error(f"Ошибка при получении списка устаревших пакетов: {stderr.decode()}")
            return []

        outdated_packages = []
        for line in stdout.decode().splitlines():
            parts = line.split()
            if len(parts) > 1:
                outdated_packages.append(parts[0])

        return outdated_packages
    except Exception as e:
        logger.exception("Неизвестная ошибка при получении списка устаревших пакетов.")
        return []

# Асинхронная функция для обновления всех пакетов
async def update_all_packages(max_threads=5):
    outdated_packages = await get_outdated_packages()
    if not outdated_packages:
        logger.info("Нет устаревших пакетов для обновления.")
        return

    logger.info(f"Найдено устаревших пакетов: {len(outdated_packages)}")

    # Асинхронный прогресс-бар
    tasks = [update_package(package) for package in outdated_packages]
    for _ in tqdm(asyncio.gather(*tasks), total=len(tasks), desc="Обновление пакетов"):
        pass

# Запуск асинхронного обновления
if __name__ == "__main__":
    asyncio.run(update_all_packages())
