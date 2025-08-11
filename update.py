from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from collections import OrderedDict

REPO_URL = "https://github.com/KiryaScript/discord-fix-app/graphs/traffic"

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def wait_for_login(driver):
    print("Ожидаю, что вы уже авторизованы и находитесь на странице трафика.")
    try:
        # Проверяем, что мы на странице трафика и нужный блок загружен
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#traffic-visitors-graph"))
        )
        print("На странице трафика.")
    except Exception as e:
        print("Не удалось обнаружить страницу трафика.")
        raise e

def parse_graph_data(driver, graph_selector, max_views, max_uniques):
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, graph_selector)))
        time.sleep(2)
    except Exception as e:
        print(f"График {graph_selector} не прогрузился: {e}")
        return []

    views_data = []
    try:
        total_dots = driver.find_elements(By.CSS_SELECTOR, f"{graph_selector} svg.viz g.dots.totals circle")
        unique_dots = driver.find_elements(By.CSS_SELECTOR, f"{graph_selector} svg.viz g.dots.uniques circle")
        x_axis_ticks = driver.find_elements(By.CSS_SELECTOR, f"{graph_selector} svg.viz g.x.axis g.tick text")

        dates = [tick.text for tick in x_axis_ticks]
        if len(total_dots) != len(unique_dots) or len(total_dots) != len(dates):
            print("Несовпадение размеров данных.")
            return []

        daily_data = OrderedDict()
        for i, (total_dot, unique_dot) in enumerate(zip(total_dots, unique_dots)):
            date = dates[i]
            total_y = float(total_dot.get_attribute("cy"))
            unique_y = float(unique_dot.get_attribute("cy"))

            total_count = round((193.5 - total_y) / 193.5 * max_views)
            unique_count = round((193.5 - unique_y) / 193.5 * max_uniques)

            daily_data[date] = {
                "timestamp": date.replace("/", "-"),
                "count": max(0, total_count),
                "uniques": max(0, unique_count)
            }

        views_data = list(daily_data.values())
        print(f"Спарсил {len(views_data)} дней из {graph_selector}.")
        return views_data
    except Exception as e:
        print(f"Ошибка парсинга графика {graph_selector}: {e}")
        return []

def parse_summary_stats(driver, label):
    try:
        selector = f".Box:has(.js-traffic-total.{label})"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"{selector} .js-traffic-total.{label}"))
        )
        total = int(driver.find_element(By.CSS_SELECTOR, f"{selector} .js-traffic-total.{label}").text.replace(",", ""))
        uniques = int(driver.find_element(By.CSS_SELECTOR, f"{selector} .js-traffic-uniques.uniques").text.replace(",", ""))
        return total, uniques
    except Exception as e:
        print(f"Ошибка парсинга stats для {label}: {e}")
        return 0, 0

def parse_table_data(driver, heading_text, title_col):
    data = []
    try:
        print(f"Ищем блок с заголовком: {heading_text}")
        block = driver.find_element(By.XPATH, f"//h3[contains(text(), '{heading_text}')]/ancestor::div[contains(@class, 'Box')]")
        tables = block.find_elements(By.TAG_NAME, "table")
        if not tables:
            print(f"Таблица не найдена для {heading_text}")
            return []
        table = tables[0]
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                data.append({
                    title_col: cols[0].text.strip(),
                    "count": int(cols[1].text.replace(",", "")),
                    "uniques": int(cols[2].text.replace(",", ""))
                })
        print(f"Спарсено {len(data)} строк из {heading_text}")
    except Exception as e:
        print(f"Ошибка при парсинге таблицы '{heading_text}': {e}")
    return data

def scrape_traffic_data(driver):
    print("Начинаю парсинг...")

    clones_data = parse_graph_data(driver, "div#traffic-clones-graph", max_views=20, max_uniques=10)
    clones_total, clones_uniques = parse_summary_stats(driver, "clones")

    views_data = parse_graph_data(driver, "div#traffic-visitors-graph", max_views=100, max_uniques=15)
    views_total, views_uniques = parse_summary_stats(driver, "visits")

    referrers = parse_table_data(driver, "Referring sites", "referrer")
    paths = parse_table_data(driver, "Popular content", "path")

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
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Сохранено в {filename}")

def main():
    driver = setup_driver()
    try:
        wait_for_login(driver)
        traffic_data = scrape_traffic_data(driver)
        if traffic_data:
            save_to_json(traffic_data)
        else:
            print("Ничего не спарсилось.")
    except Exception as e:
        print(f"Ошибка выполнения: {e}")
    finally:
        driver.quit()
        print("Браузер закрыт.")

if __name__ == "__main__":
    main()
