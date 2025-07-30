import os

# Получаем текущую директорию
current_dir = os.getcwd()

# Проходим по всем файлам в текущей папке
for filename in os.listdir(current_dir):
    if filename.endswith(".bat"):
        # Получаем имя файла без расширения
        name_without_ext = os.path.splitext(filename)[0]
        
        # Заменяем пробелы на _ и убираем скобки
        clean_name = name_without_ext.replace(" ", "_").replace("(", "").replace(")", "")
        
        # Читаем содержимое файла
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Заменяем DiscordFix на очищенное имя файла
        new_content = content.replace("DiscordFix", clean_name)
        
        # Записываем изменённое содержимое обратно в файл
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(new_content)
            
        print(f"Обработал файл {filename}: заменил 'DiscordFix' на '{clean_name}'")