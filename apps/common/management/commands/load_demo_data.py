"""Management command to load demonstration users and flow data"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.users.models import Role, UserRole
from apps.flows.models import (
    Flow,
    FlowStep,
    Task,
    Quiz,
    QuizQuestion,
    QuizAnswer,
)
from apps.guides.models import Article


class Command(BaseCommand):
    help = 'Создает демонстрационные данные: пользователей и тестовый поток'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Создание демонстрационных данных...'))
        with transaction.atomic():
            self.create_users()
            self.create_demo_flow()
        self.stdout.write(self.style.SUCCESS('🎉 Демонстрационные данные успешно созданы'))

    def create_users(self):
        User = get_user_model()
        roles = {r.name: r for r in Role.objects.all()}

        # Используем email как основу для telegram_id, чтобы обеспечить уникальность
        users_data = [
            {'email': 'buddy@example.com', 'name': 'Buddy User', 'password': 'buddy123', 'role': 'buddy'},
            {'email': 'user@example.com', 'name': 'Demo User', 'password': 'user123', 'role': 'user'},
            {'email': 'moderator@example.com', 'name': 'Moderator User', 'password': 'moderator123', 'role': 'moderator'},
        ]

        created_count = 0
        for user_data in users_data:
            # Генерируем telegram_id из email, чтобы избежать дубликатов
            telegram_id = f"demo_{user_data['email'].split('@')[0]}"
            
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'email': user_data['email'],
                    'name': user_data['name'],
                }
            )

            if created:
                user.set_password(user_data['password'])
                user.save()
                created_count += 1
                self.stdout.write(f"✅ Пользователь {user.name} ({user.email}) создан.")

            # Назначаем роль
            role_name = user_data['role']
            if role_name in roles:
                UserRole.objects.get_or_create(user=user, role=roles[role_name])
            else:
                self.stdout.write(self.style.WARNING(f"Роль '{role_name}' не найдена."))

        self.stdout.write(f'📊 Создано пользователей: {created_count}')

    def create_demo_flow(self):
        flow, created = Flow.objects.get_or_create(
            title='Сначала было Figma',
            defaults={'description': 'Тестовый обучающий флоу для новичков-дизайнеров'}
        )
        if created:
            self.stdout.write(f'✅ Создан поток: {flow.title}')

        steps = [
            {
                'title': 'Принятие Figma как новой религии',
                'description': 'Ты — новый дизайнер. Figma — твой храм, автолэйаут — мантра, а компоненты — твои боевые товарищи.',
                'instruction': 'Найди в нашем Figma-файле "Твой первый макет" текстовый фрейм с надписью «🔥 Это не кнопка, а...». Внутри спрятано кодовое слово.',
                'code_word': 'пельмень',
                'quiz': [
                    {
                        'question': 'Что делать, если компоненты в Figma разъехались?',
                        'answers': [
                            ('Плакать', False, 'Слёзы — не автофиксация.'),
                            ('Перезагрузить Mac', False, 'Ты в дизайне, а не в техподдержке.'),
                            ('Настроить автолэйаут', True, 'Это и есть путь к просветлению.'),
                            ('Призвать проджекта', False, 'Он не UX-экзорцист.'),
                            ('Сменить профессию', False, 'Не беги от проблемы — беги к автолэйауту!'),
                        ],
                    },
                    {
                        'question': 'Чем отличается Frame от Group?',
                        'answers': [
                            ('Frame платный, Group бесплатный', False, 'Всё бесплатное в Figma — до лимита.'),
                            ('Frame — это как div, Group — как span', True, 'Почти фронтенд, только красиво.'),
                            ('Frame мигает при клике', False, 'Это баг, а не фича.'),
                            ('Group удаляется вместе с VPN', False, 'VPN тут вообще при чём?'),
                            ('Group делает кофе', False, 'Увы.'),
                        ],
                    },
                ],
            },
            {
                'title': 'Да кто все эти люди в Slack?',
                'description': 'Slack — не мессенджер, а корпоративный сериал.',
                'instruction': 'Найди в канале #design-humor мем с котом, стоящим перед монитором с подписью "Когда опять правки от клиента". В Alt-тексте мемчика скрыто кодовое слово.',
                'code_word': 'дедлайн',
                'quiz': [
                    {
                        'question': 'Что означает «+1» в Slack?',
                        'answers': [
                            ('Хочу быть частью этого', True, 'Так мы говорим «я тоже».'),
                            ('Пригласить друга', False, 'Это не онлайн-игра.'),
                            ('Это голосование', False, 'Почти, но не формально.'),
                            ('Тебя лайкнули', False, 'Для этого есть emoji.'),
                            ('Ошибка HR', False, 'HR тут вообще не причём.'),
                        ],
                    },
                    {
                        'question': 'Зачем добавлять 🧵 (тред)?',
                        'answers': [
                            ('Чтобы показать, что ты умный', False, 'Ум показан делами.'),
                            ('Чтобы не захламлять канал', True, 'Истинное предназначение.'),
                            ('Чтобы спрятать пассивную агрессию', False, 'Но удобно.'),
                            ('Так говорят старшие дизайнеры', False, 'И ты говори! Но с умом.'),
                            ('Это модно', False, 'Не всё модное — полезно.'),
                        ],
                    },
                ],
            },
            {
                'title': 'Файлообмен и поиски «последняя_версия_финал_v3(копия)_правки»',
                'description': 'Google Drive и Notion — это цифровой шкаф с миллионом ящиков.',
                'instruction': 'В Notion-доке "Инструкция по загрузке макетов" найди сноску с надписью "P.S. Мы вас предупредили". Рядом будет кодовое слово.',
                'code_word': 'референс',
                'quiz': [
                    {
                        'question': 'Как понять, что это финальная версия файла?',
                        'answers': [
                            ('Там написано «финал»', False, 'Обманчиво.'),
                            ('Это самая верхняя версия', False, 'Там может быть черновик.'),
                            ('Файл залит в общий чат', True, 'Скорее всего — это он.'),
                            ('Ты так чувствуешь', False, 'Интуиция — не папка.'),
                            ('Указал артдир', False, 'А он сам в Notion верит?'),
                        ],
                    },
                    {
                        'question': 'Где хранить актуальные референсы?',
                        'answers': [
                            ('В Telegram', False, 'Улетит вместе с телефоном.'),
                            ('В голове', False, 'Недостаточно оперативки.'),
                            ('В Notion или Drive', True, 'Только с понятным названием.'),
                            ('В чатике', False, 'Потеряется под гифками.'),
                            ('В Figma-файле', False, 'Там — макеты, а не музей.'),
                        ],
                    },
                ],
            },
        ]

        for order, step_data in enumerate(steps, start=1):
            step, created_step = FlowStep.objects.get_or_create(
                flow=flow,
                order=order,
                defaults={
                    'title': step_data['title'],
                    'description': step_data['description'],
                },
            )
            if created_step:
                self.stdout.write(f'  • Этап {order} создан')

            Article.objects.get_or_create(
                flow_step=step,
                defaults={
                    'title': step_data['title'],
                    'content': step_data['description'],
                    'is_published': True,
                },
            )

            task, _ = Task.objects.get_or_create(
                flow_step=step,
                defaults={
                    'title': step_data['title'],
                    'description': step_data['description'],
                    'instruction': step_data['instruction'],
                    'code_word': step_data['code_word'],
                },
            )

            quiz, _ = Quiz.objects.get_or_create(
                flow_step=step,
                defaults={'title': f'Квиз: {step_data["title"]}'},
            )

            for q_order, q in enumerate(step_data['quiz'], start=1):
                question, _ = QuizQuestion.objects.get_or_create(
                    quiz=quiz,
                    order=q_order,
                    defaults={'question': q['question']},
                )
                for a_order, (text, correct, expl) in enumerate(q['answers'], start=1):
                    QuizAnswer.objects.get_or_create(
                        question=question,
                        order=a_order,
                        defaults={
                            'answer_text': text,
                            'is_correct': correct,
                            'explanation': expl,
                        },
                    )

        self.stdout.write('📚 Поток и этапы готовы')
