# main.py


from gigachat_api import get_access_token, chat_with_gigachat, chat_with_gigachat_messages

# ALL agents which are used
from agents.moderator import run_moderator
from agents.tutor import run_tutor
from agents.examiner import run_examiner
from agents.analyser import run_analyser 
from agents.problem_solver import start_problem_solver, continue_problem_solver



#ALL utils which are used
from utils.format_exam import format_exam


#ALL memories which are used
 # Общее состояние для простейшей памяти
state = {
        "tutor_history": [],
        "last_topic": None,
        "current_test": None,   # ← здесь будет храниться тест от Examiner
        "results": [],          # ← сюда будем складывать все результаты
        "problem_solver": {   # состояние Problem Solver-а
        "active": False,
        "topic": None,
        "steps": [],
        "current_step": 0,
    },
    }

def show_progress(state):
    """
    Показывает историю результатов всех тестов
    И считает общий средний результат.
    """
    results = state.get("results", [])
    if not results:
        print("Пока нет ни одного завершённого теста.")
        return

    print("История тестов:")
    total_correct = 0
    total_questions = 0

    for i, r in enumerate(results, start=1):
        topic = r.get("topic") or "(неизвестная тема)"
        score = r.get("score", 0)
        total = r.get("total", 0)
        percent = r.get("percent", 0)

        total_correct += score
        total_questions += total

        print(f"{i}. Тема: {topic} — результат: {score}/{total} ({percent}%)")

    # --- вычисляем средний результат ---
    if total_questions > 0:
        avg_percent = int(total_correct / total_questions * 100)
        print(f"\nСредний результат: {total_correct}/{total_questions} ({avg_percent}%)")
    else:
        print("\nСредний результат: нет достаточных данных.")




if __name__ == "__main__":
    # 1. Берём токен
    token = get_access_token()
    #print("Токен получен")
    print("\n\nДобро пожаловать в Lumira!\nLumira — это умный учебный помощник, который может объяснять темы, тренировать тебя с помощью тестов, анализировать ответы и помогать решать задачи.")

    while True:

        user_text = input("\nНапиши свой запрос: ")
        
        if user_text == 'exit':
            print("Bye-bye")
            break

        # команда просмотра прогресса
        if user_text.lower() == "progress":
            show_progress(state)
            continue

            # --- Если активен Problem Solver и пользователь отвечает "да/нет" ---
        if state["problem_solver"]["active"]:
            normalized = user_text.strip().lower()
            yes_words = {"yes", "y", "да", "ага", "понял", "поняла", "понял.", "поняла."}
            no_words = {"no", "n", "нет", "неа", "не", "не понял", "не поняла"}

            if normalized in yes_words or normalized in no_words:
                answer, state["problem_solver"] = continue_problem_solver(
                    token,           
                    state["problem_solver"],
                    user_text,
                )
                print("\nОтвет модели:\n")
                print(answer)
                continue

            # если ответ не да/нет — считаем, что это новый запрос, и идём дальше к модератору


        if not user_text:
            continue  # пустой ввод, просто пропускаем
        
        # 1. Ask moderator what to do
        agent_id, change_topic = run_moderator(token, user_text)
        print('++++++',agent_id, change_topic)
        # 2. Update topic if Moderator says so
        if change_topic == 1:
            state["last_topic"] = user_text

        payload = user_text.strip()  # всё после первой цифры, без пробелов по краям

        if agent_id == 1:
            # ---- TUTOR ----
            answer, state["tutor_history"] = run_tutor(
                token,
                user_text,
                state["tutor_history"],
            )

        elif agent_id == 2:
            # ---- EXAMINER ----

            # If moderator said not to change topic, and last_topic exists,
            # we use last_topic instead of full user_text as the test theme.
            print("\nКак отвечать на тесты\nПишите только в формате:\n1a 2c 3b 4d 5a\nГде:\nчисло — номер вопроса,\nбуква — выбранный вариант ответа.")
            if state["last_topic"] is None:
                # fallback: use current message as topic
                topic = user_text
                state["last_topic"] = topic
            else:
                topic = state["last_topic"]



            raw_test = run_examiner(token, topic)

            questions_text, answers_dict, theme = format_exam(raw_test)

            # обновляем тему в состоянии по результату экзаменатора
            state["last_topic"] = theme

            # сохраняем ответы ДЛЯ анализатора
            state["current_test"] = answers_dict

            # показываем пользователю только текст вопросов
            answer = questions_text


        elif agent_id == 3:  
            # ---- Analyzer ----
            if state["current_test"] is None:
                answer = "Нет теста для проверки!"
            else:
                # run_analyser теперь возвращает 3 значения
                report_text, score, total = run_analyser(state["current_test"], user_text)

                # вычисляем процент
                percent = int(score / total * 100) if total > 0 else 0

                # сохраняем результат в память
                state["results"].append({
                    "topic": state["last_topic"],
                    "score": score,
                    "total": total,
                    "percent": percent,
                    "answers": user_text,
                })

                # тест проверен → очищаем
                state["current_test"] = None

                # пользователю показываем текст отчёта
                answer = report_text

        elif agent_id == 4:  
            # ---- PROBLEM SOLVER ----
            # стартуем новую сессию пошагового объяснения
            answer, ps_state = start_problem_solver(token, user_text)
            state["problem_solver"] = ps_state



        else:
            answer = "Неизвестный режим, модератор вернул странный код.\n"
            print(agent_id, change_topic)


        print("\nОтвет модели:\n")
        print(answer)