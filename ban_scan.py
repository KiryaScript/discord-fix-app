import os
import requests
from tqdm import tqdm

API_BASE_URL = "https://reestr.rublacklist.net/api/v3"

headers = {
    "Content-Type": "application/json"
}

def get_blocked_domains():
    url = f"{API_BASE_URL}/domains/"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении доменов: {response.status_code}")
        return []

def get_blocked_ips():
    url = f"{API_BASE_URL}/ips/"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении IP-адресов: {response.status_code}")
        return []

def save_to_file(filename, data):
    with open(filename, "w") as file:
        for item in tqdm(data, desc=f"Запись в {filename}", unit="item"):
            file.write(f"{item}\n")
    print(f"Данные успешно сохранены в файл: {filename}")

def main():
    print("Получение списка заблокированных доменов...")
    blocked_domains = get_blocked_domains()
    if blocked_domains:
        save_to_file("blocked_domains.txt", blocked_domains)
    else:
        print("Не удалось получить домены.")

    print("\nПолучение списка заблокированных IP-адресов...")
    blocked_ips = get_blocked_ips()
    if blocked_ips:
        save_to_file("blocked_ips.txt", blocked_ips)
    else:
        print("Не удалось получить IP-адреса.")

if __name__ == "__main__":
    main()
