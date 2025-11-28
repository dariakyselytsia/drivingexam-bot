import json
import time
import os
from playwright.sync_api import sync_playwright

# --- НАЛАШТУВАННЯ ---
DB_FILE = 'greenway_db.json'
URL_LOGIN = "https://green-way.com.ua/uk"
# URL_EXAM = "https://green-way.com.ua/uk/test-pdd/exam" # Для іспиту
URL_EXAM = "https://green-way.com.ua/uk/test-pdd/twenty-questions" # Для навчання (20 питань)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def run():
    db = load_db()
    
    with sync_playwright() as p:
        print("🚀 Запускаю браузер...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 1. Логін
        page.goto(URL_LOGIN)
        print("\n" + "="*60)
        print("🛑 ЕТАП 1: АВТОРИЗАЦІЯ")
        print("Увійди в акаунт. Коли будеш готова, повернись сюди.")
        print("="*60)
        input("👉 Натисни ENTER тут, коли залогінилась...")

        # 2. Старт тесту
        print(f"🔄 Переходжу до тесту...")
        page.goto(URL_EXAM)

        while True:
            try:
                # 3. Чекаємо завантаження питання
                try:
                    page.wait_for_selector('.text_question', state='visible', timeout=10000)
                except:
                    print("⏳ Чекаю питання...")
                    continue

                # Пауза, щоб JS довантажив текст
                time.sleep(0.5)
                
                # Зчитуємо текст
                question_el = page.query_selector('.text_question')
                question_text = question_el.inner_text().strip().replace('\n', ' ')
                
                if not question_text:
                    time.sleep(0.5)
                    continue

                # Варіанти відповідей
                options = page.query_selector_all('.answers li')
                if not options:
                    print("⚠️ Нема варіантів. Можливо, кінець тесту?")
                    time.sleep(2)
                    continue

                print(f"\n❓ Питання: {question_text[:100]}...")

                # --- АВТОМАТИЧНИЙ КЛІК ---
                if question_text in db:
                    correct_answer_text = db[question_text]
                    print(f"✅ ЗНАЮ: {correct_answer_text}")
                    
                    found = False
                    for opt in options:
                        if correct_answer_text == opt.inner_text().strip():
                            opt.click()
                            found = True
                            break
                    
                    if found:
                        # Чекаємо зміни питання, щоб не клікати те саме
                        try:
                            page.wait_for_function(
                                f"document.querySelector('.text_question').innerText.trim() !== {json.dumps(question_text)}",
                                timeout=5000
                            )
                        except:
                            pass
                        continue
                    else:
                        print("⚠ Текст відповіді в базі не співпадає з кнопками. Переходжу на ручний режим.")

                # --- РУЧНИЙ ВИБІР (НАВЧАННЯ) ---
                if question_text not in db:
                    print("🆕 Нове! Введи номер варіанту (1, 2, 3...):")
                    for idx, opt in enumerate(options, 1):
                        print(f"   [{idx}] {opt.inner_text().strip()}")
                    
                    while True:
                        try:
                            choice = int(input("👉 Твій вибір: ")) - 1
                            if 0 <= choice < len(options):
                                break
                        except ValueError:
                            pass
                    
                    # Запам'ятовуємо текст, який ти вибрала
                    selected_option = options[choice]
                    user_selected_text = selected_option.inner_text().strip()
                    
                    # Клікаємо!
                    selected_option.click()
                    
                    # --- МОМЕНТ ІСТИНИ: ШУКАЄМО .right_answer ---
                    try:
                        # Шукаємо елемент, який став зеленим (клас right_answer)
                        # Timeout короткий (1с), бо сайт швидко перемикає
                        correct_el = page.wait_for_selector('.answers li.right_answer', timeout=1500)
                        
                        if correct_el:
                            real_correct_text = correct_el.inner_text().strip()
                            db[question_text] = real_correct_text
                            save_db(db)
                            print(f"💾 Збережено правильну відповідь: {real_correct_text}")
                        else:
                            # Якщо клас не з'явився (дивна поведінка), зберігаємо твій вибір
                            raise Exception("Клас не знайдено")
                            
                    except Exception as e:
                        print(f"⚡ Сайт перемкнув дуже швидко. Вважаю твою відповідь ({user_selected_text}) правильною.")
                        db[question_text] = user_selected_text
                        save_db(db)

            except Exception as e:
                print(f"⚠ Помилка циклу: {e}")
                time.sleep(2)

if __name__ == "__main__":
    run()