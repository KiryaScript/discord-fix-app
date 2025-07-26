from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime

# Настройки
REPO_URL = "https://github.com/KiryaScript/discord-fix-app/graphs/traffic"

def setup_driver():
    """Настраиваем Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def wait_for_login(driver):
    """Ждём, пока ты залогинишься."""
    print("Залогинься в GitHub, бля, и перейди на страницу трафика. У тебя 3 минуты.")
    driver.get("https://github.com/login")
    
    try:
        WebDriverWait(driver, 180).until(EC.url_contains("/graphs/traffic"))
        print("Заебись, ты на странице трафика!")
    except:
        print("Не дошёл до страницы трафика за 3 минуты, пиздец!")
        raise

def scrape_traffic_data(driver):
    """Сдираем данные трафика."""
    print("Начинаю сдирать данные, держись...")
    
    # Ждём загрузки страницы
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "viz")))
        time.sleep(2)  # Даём JavaScript прогрузиться
    except:
        print("SVG-график не прогрузился, пиздец!")
        raise

    # Парсим график просмотров и уникальных
    views_data = []
    try:
        print("Ищу график просмотров...")
        total_dots = driver.find_elements(By.CSS_SELECTOR, "svg.viz g.dots.totals circle")
        unique_dots = driver.find_elements(By.CSS_SELECTOR, "svg.viz g.dots.uniques circle")
        x_axis_ticks = driver.find_elements(By.CSS_SELECTOR, "svg.viz g.x.axis g.tick text")
        
        dates = [tick.text for tick in x_axis_ticks]
        if len(total_dots) != len(unique_dots) or len(total_dots) != len(dates):
            print("Данные по датам/точкам не совпадают, пиздец!")
            return None

        for i, (total_dot, unique_dot) in enumerate(zip(total_dots, unique_dots)):
            total_y = float(total_dot.get_attribute("cy"))
            unique_y = float(unique_dot.get_attribute("cy"))
            
            # Предполагаем, что ось Y для просмотров: 0 внизу (y=193.5), 30 вверху (y=12.5625)
            total_count = round((193.5 - total_y) / (193.5 - 12.5625) * 30)
            # Для уникальных: 0 внизу (y=193.5), 15 вверху (y=23.20588235294118)
            unique_count = round((193.5 - unique_y) / (193.5 - 23.20588235294118) * 15)
            
            views_data.append({
                "timestamp": f"2025-{dates[i]}",  # Формат как в твоём сайте
                "count": total_count,
                "uniques": unique_count
            })
        print(f"Нашёл {len(views_data)} дней в графике.")
    except Exception as e:
        print(f"Ошибка при парсинге графика: {e}")
        views_data = []

    # Рефереры
    referrers = []
    try:
        print("Ищу рефереры...")
        referrer_elements = driver.find_elements(By.CSS_SELECTOR, "table.referrer-table tbody tr")
        for ref in referrer_elements:
            cols = ref.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                referrers.append({
                    "referrer": cols[0].text,
                    "count": int(cols[1].text.replace(",", "")),
                    "uniques": int(cols[2].text.replace(",", ""))
                })
        print(f"Нашёл {len(referrers)} рефереров.")
    except:
        print("Не нашёл рефереров, пиздец.")

    # Популярные пути
    paths = []
    try:
        print("Ищу популярные пути...")
        path_elements = driver.find_elements(By.CSS_SELECTOR, "table.popular-content-table tbody tr")
        for path in path_elements:
            cols = path.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                paths.append({
                    "path": cols[0].text,
                    "count": int(cols[1].text.replace(",", "")),
                    "uniques": int(cols[2].text.replace(",", ""))
                })
        print(f"Нашёл {len(paths)} путей.")
    except:
        print("Не нашёл популярных путей, пиздец.")

    # Формируем JSON
    traffic_data = {
        "views": {
            "total": sum(d["count"] for d in views_data) if views_data else 0,
            "uniques": sum(d["uniques"] for d in views_data) if views_data else 0,
            "daily": views_data
        },
        "referrers": referrers,
        "paths": paths,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    return traffic_data

def save_to_json(data, filename="traffic_stats.json"):
    """Сохраняем в JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Данные сохранены в {filename}, заебись!")

def main():
    driver = setup_driver()
    try:
        wait_for_login(driver)
        traffic_data = scrape_traffic_data(driver)
        if traffic_data:
            save_to_json(traffic_data)
        else:
            print("Ничего не спарсил, пиздец!")
    except Exception as e:
        print(f"Всё нахуй сломалось: {e}")
    finally:
        driver.quit()
        print("Браузер закрыт, всё пиздец.")

if __name__ == "__main__":
    main()