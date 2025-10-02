import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bd_models import Candidates, Students, Votes
import config as cfg

# Настраиваем бота
bot = telebot.TeleBot(cfg.bot_token)

# Настраиваем SQLAlchemy
engine = create_engine(cfg.db_url)
SessionLocal = sessionmaker(bind=engine)


@bot.message_handler(commands=['start'])
def start_handler(message):
    with SessionLocal() as session:
        student = session.query(Students).filter_by(s_chat_id=str(message.chat.id)).first()
        if student:
            bot.reply_to(message, f"Привет, {student.s_code}!")
        else:
            bot.reply_to(
                message,
                f"Привет! Введи, пожалуйста свой свой st000000, полученный при поступлении."
            )
            bot.register_next_step_handler(message, process_student_id)


def process_student_id(message):
    student_id = message.text
    with SessionLocal() as session:
        student = session.query(Students).filter_by(s_code=student_id).first()
        if student:
            student.s_chat_id = str(message.chat.id)
            session.commit()
            bot.reply_to(message, f"✅ st найден! Привет, {student.s_code}!")
            bot.reply_to(message, f"Введи /vote, чтобы проголосовать")
        else:
            bot.reply_to(message, "❌ Студент с таким st не найден! Попробуй ещё раз.")
            bot.register_next_step_handler(message, process_student_id)


@bot.message_handler(commands=['vote'])
def vote_handler(message):
    with SessionLocal() as session:
        student = session.query(Students).filter_by(s_chat_id=str(message.chat.id)).first()
        if student:
            student_vote = session.query(Votes).filter_by(v_student_id=student.s_id)
            if student_vote.count() > 0:
                student_vote = student_vote.first()
                candidate = session.query(Candidates).filter_by(c_id=student_vote.v_candidate_id).first()
                bot.reply_to(message, f"Вы уже проголосовали за {candidate.c_name}")
            else:
                candidates = session.query(Candidates).filter_by(c_active=True).filter_by(
                    c_program_id=student.s_program_id).all()
                markup = InlineKeyboardMarkup()
                for c in candidates:
                    markup.add(InlineKeyboardButton(text=c.c_name, callback_data=f"vote_{c.c_id}"))
                    with open(f"images/{c.c_photo_path}", "rb") as photo:
                        print(c.c_name)
                        bot.send_photo(
                            message.chat.id,
                            photo,
                            caption=f"{c.c_name}\n\n{c.c_message}",
                            parse_mode='HTML'
                        )
                    # bot.send_message(message.chat.id, f"{c.c_name}\n\n{c.c_message}", parse_mode='HTML')
                bot.send_message(message.chat.id, "Выберите кандидата:", reply_markup=markup)
        else:
            bot.reply_to(message, f"Ошибка авторизации, пожалуйста, введите команду /start")


@bot.callback_query_handler(func=lambda call: call.data.startswith("vote_"))
def process_vote_callback(call):
    candidate_id = int(call.data.replace("vote_", ""))

    with SessionLocal() as session:
        student = session.query(Students).filter_by(s_chat_id=str(call.message.chat.id)).first()
        if not student:
            bot.answer_callback_query(call.id, "Ошибка авторизации. Сначала выполните /start.")
            return

        # проверка на повторное голосование
        if session.query(Votes).filter_by(v_student_id=student.s_id).count() > 0:
            bot.answer_callback_query(call.id, "Вы уже проголосовали!")
            return

        candidate = session.query(Candidates).filter_by(c_id=candidate_id).first()
        if not candidate:
            bot.answer_callback_query(call.id, "Такого кандидата нет.")
            return

        # создаём запись о голосе
        new_vote = Votes(v_candidate_id=candidate_id, v_student_id=student.s_id)
        session.add(new_vote)
        session.commit()

        bot.answer_callback_query(call.id, f"✅ Ваш голос за {candidate.c_name} учтён!")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Спасибо! Ваш голос за {candidate.c_name} учтён ✅"
        )


if __name__ == "__main__":
    print("🤖 Бот запущен и слушает сообщения...")
    bot.polling(none_stop=True)
