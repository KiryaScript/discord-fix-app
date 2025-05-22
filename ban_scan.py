import os
import requests
from tqdm import tqdm

API_BASE_URL = "https://reestr.rublacklist.net/api/v3"
HEADERS = {"Content-Type": "application/json"}

def get_blocked_list(endpoint: str) -> list:
    """Получает данные с API и возвращает список"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}/", headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка при получении {endpoint}: {e}")
        return []

def save_to_file(filename: str, data: list):
    """Сохраняет данные в файл построчно"""
    with open(filename, "w", encoding="utf-8") as f:
        for item in tqdm(data, desc=f"Запись в {filename}", unit="item"):
            f.write(f"{item}\n")
    print(f"✅ Сохранено: {filename}")

def main():
    print("📥 Получение заблокированных доменов...")
    domains = get_blocked_list("domains")
    if domains:
        save_to_file("blocked_domains.txt", domains)
    else:
        print("❌ Не удалось получить домены.")

    print("\n📥 Получение заблокированных IP-адресов...")
    ips = get_blocked_list("ips")
    if ips:
        save_to_file("blocked_ips.txt", ips)
    else:
        print("❌ Не удалось получить IP-адреса.")

if __name__ == "__main__":
    main()
