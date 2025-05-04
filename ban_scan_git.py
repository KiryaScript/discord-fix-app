import requests

def get_blocked_domains():
    url = "https://reestr.rublacklist.net/api/v3/domains/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении доменов: {response.status_code}")
        return []

def get_blocked_ips():
    url = "https://reestr.rublacklist.net/api/v3/ips/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении IP-адресов: {response.status_code}")
        return []

def save_to_file(filename, data):
    with open(filename, 'w') as f:
        for item in data:
            f.write(f"{item}\n")

blocked_domains = get_blocked_domains()
blocked_ips = get_blocked_ips()

if blocked_domains:
    save_to_file("blocked_domains.txt", blocked_domains)
else:
    print("Не удалось получить домены.")

if blocked_ips:
    save_to_file("blocked_ips.txt", blocked_ips)
else:
    print("Не удалось получить IP-адреса.")

print("Файлы обновлены!")
