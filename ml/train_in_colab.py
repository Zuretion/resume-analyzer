"""
Дообучение all-MiniLM-L6-v2 на датасете resume-ats-score-v1-en.

Это не скрипт для локального запуска — скопируйте содержимое ячейками
в Google Colab (Runtime -> Change runtime type -> T4 GPU) и запускайте
по шагам. Структура соответствует этапу 1 роадмапа.
"""

# === Ячейка 1: установка зависимостей ===
# !pip install -q sentence-transformers datasets

# === Ячейка 2: импорты ===
from datasets import load_dataset
from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader

# === Ячейка 3: загрузка и подготовка данных ===
dataset = load_dataset("dev6565/resume-ats-score-v1-en")
train_data = dataset["train"] if "train" in dataset else dataset["default"]

# В датасете нет отдельных колонок resume/job_description — они упакованы
# в одну колонку text как "резюме SEP вакансия" (так делает официальный
# пример на карточке датасета). Перед использованием ОБЯЗАТЕЛЬНО
# проверьте разделитель на одной строке — он может отличаться:
print(repr(train_data[0]["text"][:500]))
SEPARATOR = " SEP "  # встретите другой разделитель — поправьте здесь


def split_text(raw_text: str) -> tuple[str, str]:
    parts = raw_text.split(SEPARATOR)
    if len(parts) != 2:
        # На случай если в тексте резюме/вакансии случайно встретится
        # похожая подстрока — не падаем молча, а говорим явно.
        raise ValueError(f"Не удалось разбить текст на 2 части: {raw_text[:200]!r}")
    return parts[0].strip(), parts[1].strip()


# ats_score лежит примерно в диапазоне 19-90 -> нормализуем в 0-1
# для CosineSimilarityLoss, который ждёт метку сходства в этом диапазоне.
def to_input_example(row):
    resume, job_description = split_text(row["text"])
    return InputExample(
        texts=[resume, job_description],
        label=min(1.0, max(0.0, row["ats_score"] / 100.0)),
    )

examples = [to_input_example(row) for row in train_data]

# Простое разбиение 90/10 на train/val
split_idx = int(len(examples) * 0.9)
train_examples, val_examples = examples[:split_idx], examples[split_idx:]

# === Ячейка 4: модель и обучение ===
model = SentenceTransformer("all-MiniLM-L6-v2")

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=32)
train_loss = losses.CosineSimilarityLoss(model)

evaluator = EmbeddingSimilarityEvaluator.from_input_examples(
    val_examples, name="resume-jd-val"
)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    evaluator=evaluator,
    epochs=4,
    warmup_steps=100,
    evaluation_steps=200,
    output_path="./resume-matcher-minilm",
)

# === Ячейка 5: сохранение и скачивание весов ===
# В Colab: заархивировать папку resume-matcher-minilm и скачать,
# либо примонтировать Google Drive и сохранить туда:
#
# from google.colab import drive
# drive.mount('/content/drive')
# !cp -r resume-matcher-minilm /content/drive/MyDrive/
#
# Скачанную папку положите в backend/ml/model/ — её подхватит
# EMBEDDING_MODEL_PATH из .env (см. app/services/embeddings.py).
"""
import shutil
from google.colab import files

# Укажите путь к вашей папке и имя будущего архива
folder_path = './resume-matcher-minilm' # замените на путь к вашей папке
output_filename = '/content//resume-matcher-minilm' # будет создан my_folder.zip

shutil.make_archive(output_filename, 'zip', folder_path)
files.download(output_filename + '.zip')
"""