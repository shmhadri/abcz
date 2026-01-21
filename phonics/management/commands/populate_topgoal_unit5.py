from django.core.management.base import BaseCommand
from phonics.models import TopGoalUnit, TopGoalVocabulary, TopGoalSentence, TopGoalQuiz

class Command(BaseCommand):
    help = 'Populates the database with Top Goal 6 Unit 1 (Unit 5) content'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating Top Goal content...')

        # 1. Create Unit
        unit, created = TopGoalUnit.objects.get_or_create(
            title="Let's watch a movie!",
            grade="Top Goal 6",
            unit_number=1,  # User calls it Unit 1, but book says Unit 5. We use 1 for their context.
            defaults={
                'description': 'Types of stories, genres, and movie preferences.'
            }
        )
        if created:
            self.stdout.write(f'Created Unit: {unit}')
        else:
            self.stdout.write(f'Found Unit: {unit}')

        # 2. Vocabulary (Genres)
        genres = [
            # Word, Arabic, Emoji
            ("Fairy tale", "حكاية خيالية", "🏰"),
            ("Animation", "رسوم متحركة", "🦁"),
            ("Western", "غربي", "🤠"),
            ("Mystery", "غموض", "🕵️"),
            ("Comedy", "كوميديا", "😂"),
            ("Cartoon", "كرتون/رسوم", "🐢"),
            ("Documentary", "وثائقي", "🌍"),
            ("Drama", "دراما", "🎭"),
            ("Horror", "رعب", "😱"),
            ("Sci-fi", "خيال علمي", "👽"),
            ("Show / Play", "مسرحية", "🎬"),  # "Show" in book context or "Play"
            ("Musical", "موسيقي", "🎵"),
            ("Thriller", "إثارة", "😨"),
        ]

        # Clear existing vocab for this unit to avoid duplicates if re-run
        TopGoalVocabulary.objects.filter(unit=unit).delete()
        
        for i, (word, arabic, emoji) in enumerate(genres):
            TopGoalVocabulary.objects.create(
                unit=unit,
                word=word,
                arabic_meaning=arabic,
                emoji=emoji,
                order=i+1
            )
        self.stdout.write(f'Added {len(genres)} vocabulary items.')

        # 3. Sentences
        sentences_data = [
            ("Sci-fi is my favorite genre as it always fascinated me.", "الخيال العلمي هو النوع المفضل لدي، لأنه دائمًا ما يفتنني."),
            ("Documentaries and comedy are my next favorite.", "الوثائقيات والكوميديا هي المفضلة التالية لدي."),
            ("People sing in musicals.", "يغني الناس في المسرحيات الموسيقية."),
            ("I often watch thriller movies.", "أنا أشاهد أفلام الإثارة في كثير من الأحيان."),
            ("The plot of the story is good.", "حبكة القصة جيدة."),
            ("I prefer to read mystery stories.", "أنا أفضل قراءة قصص الغموض."),
            ("I usually watch documentaries.", "عادة ما أشاهد الوثائقيات."),
            ("Sci-fi is my favorite genre.", "الخيال العلمي هو النوع المفضل لدي."),
            ("They were watching a comedy.", "كانوا يشاهدون كوميديا."),
            ("They were enjoying the animation.", "كانوا يستمتعون بالرسوم المتحركة."),
            ("They were watching a drama.", "كانوا يشاهدون دراما."),
            ("I don't like western movies.", "أنا لا أحب الأفلام الغربية."),
            ("Cartoon use animated drawings.", "تستخدم الرسوم المتحركة رسومات متحركة."),
            ("I like horror movies the most.", "أحب أفلام الرعب أكثر شيء."),
            ("They were watching a play.", "كانوا يشاهدون مسرحية."),
            ("He was reading a fairy tale.", "كان يقرأ حكاية خيالية."),
        ]

        TopGoalSentence.objects.filter(unit=unit).delete()
        for i, (eng, ar) in enumerate(sentences_data):
            TopGoalSentence.objects.create(
                unit=unit,
                english_text=eng,
                arabic_translation=ar,
                order=i+1
            )
        self.stdout.write(f'Added {len(sentences_data)} sentences.')

        # 4. Quizzes
        quizzes_data = [
            {
                "q": "What kind of story has detectives and a twist in the plot?",
                "type": "mcq",
                "options": ["Mystery", "Comedy", "Musical"],
                "correct": "Mystery",
                "expl": "Mystery stories involve solving a crime or puzzle."
            },
            {
                "q": "What kind of story makes us laugh a lot?",
                "type": "mcq",
                "options": ["Horror", "Comedy", "Thriller"],
                "correct": "Comedy",
                "expl": "Comedy is designed to be funny."
            },
            {
                "q": "What kind of story has astronauts in space?",
                "type": "mcq",
                "options": ["Sci-fi", "Western", "Fairy tale"],
                "correct": "Sci-fi",
                "expl": "Science fiction often deals with future science and space travel."
            },
            {
                "q": "What kind of story has pictures drawn by hand or computer?",
                "type": "mcq",
                "options": ["Animation", "Documentary", "Drama"],
                "correct": "Animation",
                "expl": "Animation uses drawn or computer-generated images."
            },
            {
                "q": "A musical is a story where people...",
                "type": "mcq",
                "options": ["Fight", "Sing", "Sleep"],
                "correct": "Sing",
                "expl": "Musicals feature characters singing songs."
            }
        ]

        TopGoalQuiz.objects.filter(unit=unit).delete()
        for i, quiz in enumerate(quizzes_data):
            TopGoalQuiz.objects.create(
                unit=unit,
                question_text=quiz["q"],
                question_type=quiz["type"],
                options=quiz["options"],
                correct_answer=quiz["correct"],
                explanation_ar=quiz["expl"],
                order=i+1
            )
        self.stdout.write(f'Added {len(quizzes_data)} quizzes.')

        self.stdout.write(self.style.SUCCESS('Successfully populated Top Goal Unit 1 (Unit 5) content!'))
