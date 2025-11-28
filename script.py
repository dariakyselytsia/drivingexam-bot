import json
import time
from playwright.sync_api import sync_playwright

# Файл бази даних
DB_FILE = 'greenway_db.json'

def load_db():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def run():
    db = load_db()
    
    with sync_playwright() as p:
        # Запускаємо реальний браузер
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://green-way.com.ua/uk/login") # Приклад URL
        
        # 1. ЕТАП: Ручна авторизація
        print("🔴 БУДЬ ЛАСКА, ЗАЛОГІНЬСЯ В БРАУЗЕРІ ВРУЧНУ.")
        input("🟢 Натисни Enter тут, коли увійдеш і будеш готова почати іспит...")
        
        # Тут ми вже на сторінці, де треба тицьнути "Почати іспит"
        # page.click('selector_knopky_start') 
        
        while True:
            # 2. ЕТАП: Зчитування питання
            # page.wait_for_selector('selector_pytannia')
            question_text = "Текст питання з сайту..." # Тут буде реальний код
            
            if question_text in db:
                print(f"✅ Знаю відповідь! Це: {db[question_text]}")
                # page.click(f'text={db[question_text]}')
            else:
                print(f"❓ Нове питання: {question_text}")
                # Тут логіка показу варіантів і твого ручного вибору через input()
                user_choice = input("Твій вибір (1/2/3/4): ")
                
                # Клік по твоєму вибору
                # page.click(...)
                
                # Чекаємо підсвітки правильної відповіді
                # page.wait_for_selector('.correct-answer-class')
                
                correct_answer = "Отримуємо текст зеленої кнопки"
                db[question_text] = correct_answer
                save_db(db)
                print("💾 Збережено в базу!")
            
            # Чекаємо наступного питання
            time.sleep(2)

if __name__ == "__main__":
    run()