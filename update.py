from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from collections import OrderedDict

# Настройки
REPO_URL = "https://github.com/KiryaScript/discord-fix-app/graphs/traffic"

def setup_driver():
    """Настраиваем Selenium WebDriver, чтобы не наебнулся."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def wait_for_login(driver):
    """Ждём, пока ты, бля, залогинишься."""
    print("Залогинься в GitHub и пиздец, перейди на страницу трафика. Даю 3 минуты.")
    driver.get("https://github.com/login")
    
    try:
        WebDriverWait(driver, 180).until(EC.url_contains("/graphs/traffic"))
        print("Красавчик, ты на странице трафика!")
    except:
        print("Не успел за 3 минуты, пиздец тебе!")
        raise

def parse_graph_data(driver, graph_selector, max_views, max_uniques):
    """Парсим данные из SVG-графика, чтобы не обосраться."""
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, graph_selector)))
        time.sleep(3)  # Ждём, пока JS не дохуя прогрузится
    except:
        print(f"График {graph_selector} не прогрузился, пиздец!")
        raise

    views_data = []
    try:
        print(f"Ищу данные в графике {graph_selector}...")
        total_dots = driver.find_elements(By.CSS_SELECTOR, f"{graph_selector} svg.viz g.dots.totals circle")
        unique_dots = driver.find_elements(By.CSS_SELECTOR, f"{graph_selector} svg.viz g.dots.uniques circle")
        x_axis_ticks = driver.find_elements(By.CSS_SELECTOR, f"{graph_selector} svg.viz g.x.axis g.tick text")
        
        dates = [tick.text for tick in x_axis_ticks]
        if len(total_dots) != len(unique_dots) or len(total_dots) != len(dates):
            print(f"Несовпадение: {len(total_dots)} точек, {len(unique_dots)} уникальных, {len(dates)} дат, пиздец!")
            return []

        daily_data = OrderedDict()
        for i, (total_dot, unique_dot) in enumerate(zip(total_dots, unique_dots)):
            date = dates[i]  # Формат MM/DD
            total_y = float(total_dot.get_attribute("cy"))
            unique_y = float(unique_dot.get_attribute("cy"))
            
            # Линейная интерполяция для просмотров (0 внизу, max_views вверху)
            total_count = round((193.5 - total_y) / 193.5 * max_views)
            # Линейная интерполяция для уникальных (0 внизу, max_uniques вверху)
            unique_count = round((193.5 - unique_y) / 193.5 * max_uniques)
            
            daily_data[date] = {
                "timestamp": date.replace("/", "-"),  # MM-DD
                "count": max(0, total_count),  # Убираем отрицательные значения
                "uniques": max(0, unique_count)
            }
        
        views_data = list(daily_data.values())
        print(f"Спарсил {len(views_data)} дней из графика {graph_selector}.")
        return views_data
    except Exception as e:
        print(f"Ошибка при парсинге графика {graph_selector}: {e}")
        return []

def parse_summary_stats(driver, stats_selector):
    """Парсим общие stats из графика."""
    try:
        total = int(driver.find_element(By.CSS_SELECTOR, f"{stats_selector} .js-traffic-total").text.replace(",", ""))
        uniques = int(driver.find_element(By.CSS_SELECTOR, f"{stats_selector} .js-traffic-uniques").text.replace(",", ""))
        return total, uniques
    except Exception as e:
        print(f"Ошибка при парсинге stats {stats_selector}: {e}")
        return 0, 0

def parse_table_data(driver, table_id, title_col):
    """Парсим таблицы рефереров или путей."""
    data = []
    try:
        print(f"Ищу таблицу {table_id}...")
        table = driver.find_element(By.CSS_SELECTOR, f"#{table_id} table.capped-list")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                data.append({
                    title_col: cols[0].text.strip(),
                    "count": int(cols[1].text.replace(",", "")),
                    "uniques": int(cols[2].text.replace(",", ""))
                })
        print(f"Спарсил {len(data)} строк из таблицы {table_id}.")
    except Exception as e:
        print(f"Ошибка при парсинге таблицы {table_id}: {e}")
    return data

def scrape_traffic_data(driver):
    """Сдираем все данные с трафика, чтобы не обосраться."""
    print("Начинаю парсить трафик, держись за жопу...")

    # Парсим клоны
    clones_data = parse_graph_data(driver, "traffic-clones-graph", max_views=20, max_uniques=10)
    clones_total, clones_uniques = parse_summary_stats(driver, ".traffic-clones-graph .traffic-graph-stats")

    # Парсим посетителей
    views_data = parse_graph_data(driver, "traffic-visitors-graph", max_views=100, max_uniques=15)
    views_total, views_uniques = parse_summary_stats(driver, ".traffic-visitors-graph .traffic-graph-stats")

    # Парсим рефереры
    referrers = parse_table_data(driver, "top-domains", "referrer")

    # Парсим популярные пути
    paths = parse_table_data(driver, "header-802b6a03-5499-42fd-bd8e-d2c541858528", "path")

    # Формируем JSON
    traffic_data = {
        "clones": {
            "total": clones_total,
            "uniques": clones_uniques,
            "daily": clones_data
        },
        "views": {
            "total": views_total,
            "uniques": views_uniques,
            "daily": views_data
        },
        "referrers": referrers,
        "paths": paths
    }
    
    return traffic_data

def save_to_json(data, filename="stats.json"):
    """Сохраняем в JSON, чтобы всё заебись было."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Сохранил в {filename}, пиздец как круто!")

def main():
    driver = setup_driver()
    try:
        wait_for_login(driver)
        traffic_data = scrape_traffic_data(driver)
        if traffic_data:
            save_to_json(traffic_data)
        else:
            print("Нихуя не спарсил, пиздец!")
    except Exception as e:
        print(f"Всё нахуй сломалось: {e}")
    finally:
        driver.quit()
        print("Браузер закрыт, пиздец всему.")

if __name__ == "__main__":
    main()