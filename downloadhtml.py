import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

# Функция для скачивания HTML страницы
def download_github_page(url, output_file="github_traffic.html"):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Открываем браузер на весь экран

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Открываю GitHub. Введи логин и пароль, потом нажми Enter в консоли.")
        driver.get("https://github.com/login")
        
        input("Нажми Enter после авторизации...")

        print(f"Перехожу на {url}")
        driver.get(url)
        time.sleep(5)  # Ждем прогрузки страницы (увеличь, если контент долго грузится)

        html_content = driver.page_source
        
        # Сохраняем в файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML успешно сохранен в {output_file}")
        
        driver.quit()
        
    except Exception as e:
        print(f"Похер, ошибка: {e}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    try:
        target_url = "https://github.com/KiryaScript/discord-fix-app/graphs/traffic"
        download_github_page(target_url)
    except Exception as e:
        print(f"Что-то пошло по пиздецу: {e}")