import asyncio
import shutil
from pathlib import Path
import logging
import argparse
import aiopath
from colorama import Fore, Style, init
import csv
init(autoreset=True)

# Для дефольта по файлам(ШІ help)
def generate_test_files(target_folder: str = 'start_folder'):
    folder = Path(target_folder)
    folder.mkdir(parents=True, exist_ok=True)

    # TXT
    (folder / 'example.txt').write_text("Це приклад текстового файлу.\nМожна сортувати по розширенню .txt.")

    # HTML
    (folder / 'index.html').write_text("<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Привіт, світ!</h1></body></html>")

    # JSON
    (folder / 'data.json').write_text('{"name": "Petro", "role": "developer", "skills": ["Python", "AsyncIO", "aiopath"]}')

    print(f"✅ {Fore.LIGHTBLUE_EX}Створено тестові файли у папці: {folder.resolve()}{Style.RESET_ALL}")



# Логування і налаштування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)
logger = logging.getLogger(__name__)

# для звіту
report_data = []

# Копіювання файлів, запис даних для звіту
async def copy_files(file_path: Path, destination_folder: Path):
    extension = file_path.suffix.lower().strip('.') or "unknown"
    destination_direct = destination_folder / extension

    try:
        destination_direct.mkdir(parents=True, exist_ok=True)
        dest_file = destination_direct / file_path.name
        shutil.copy2(file_path, dest_file)
        logger.info(f"{Fore.LIGHTGREEN_EX}Copied:{Style.RESET_ALL} {file_path} {Fore.LIGHTGREEN_EX}to{Style.RESET_ALL} {dest_file}")

        report_data.append([str(file_path), str(dest_file), extension])
    except Exception as e:
        logger.error(f"{Fore.RED}Error copying {file_path}: {e}{Style.RESET_ALL}")


# обхід каталогу
async def read_folder(source: Path, destination: Path):
    async for file_path in aiopath.AsyncPath(source).glob('**/*'):
        if await file_path.is_file():
            await copy_files(file_path, destination)


# Запис звіту у файл CSV(google help)
def write_report(report_path: Path):
    try:
        with open(report_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Source Path', 'Destination Path', 'Extension'])
            writer.writerows(report_data)          

        logger.info(f"{Fore.LIGHTBLUE_EX}Звіт збережено у файлі: {report_path}{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"{Fore.RED}Помилка при збереженні звіту: {e}{Style.RESET_ALL}")


# Додано звітування до асинхронного сортування файлів
def main():
    parser = argparse.ArgumentParser(description=f"{Fore.CYAN}Асинхроне сортування файлів та звітування{Style.RESET_ALL}")
    parser.add_argument('folder_path', type=str, nargs='?', default='start_folder',
                        help=f'{Fore.GREEN}Шлях до папки, яку потрібно обробити{Style.RESET_ALL}')
    parser.add_argument('output_folder', type=str, nargs='?', default='result_folder',
                        help=f'{Fore.LIGHTYELLOW_EX}Шлях до папки, куди потрібно скопіювати файли{Style.RESET_ALL}')
    parser.add_argument('--report', type=str, default='report.csv',
                        help=f'{Fore.MAGENTA}Назва CSV-файлу для збереження звіту{Style.RESET_ALL}')
    args = parser.parse_args()

    logger.info(f"Обробка папки: {args.folder_path}, результати: {args.output_folder}, звіт: {args.report}") # Просто інформація про роботу


    source_path = Path(args.folder_path)
    output_path = Path(args.output_folder)
    report_path = Path(args.report)

    source_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"{Fore.GREEN}...Сортування файлів розпочато...{Style.RESET_ALL}")
    asyncio.run(read_folder(source_path, output_path))
    write_report(report_path)
    logger.info(f"{Fore.GREEN}! Сортування файлів завершено !{Style.RESET_ALL}")
    logger.info(f"{Fore.CYAN}Результати збережено --> {output_path}{Style.RESET_ALL}")
    logger.info(f"{Fore.YELLOW}...Скрипт закінчив роботу...{Style.RESET_ALL}")

if __name__ == "__main__":
    generate_test_files()
    main()