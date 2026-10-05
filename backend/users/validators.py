import re

LOGIN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{3,19}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PASSWORD_UPPER_RE = re.compile(r"[A-ZА-Я]")
PASSWORD_DIGIT_RE = re.compile(r"\d")
PASSWORD_SPECIAL_RE = re.compile(r"[^A-Za-z0-9А-Яа-я]")


def validate_registration(data):
    """
    Проверяет данные регистрации.
    Возвращает словарь {field: "сообщение об ошибке"} — пустой, если всё ок.
    """
    errors = {}

    login = (data.get("username") or "").strip()
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not login:
        errors["username"] = "Логин обязателен."
    elif not LOGIN_RE.match(login):
        errors["username"] = (
            "Логин должен состоять только из латинских букв и цифр, "
            "начинаться с буквы, длина от 4 до 20 символов."
        )

    if not full_name:
        errors["full_name"] = "Укажите полное имя."

    if not email:
        errors["email"] = "Email обязателен."
    elif not EMAIL_RE.match(email):
        errors["email"] = "Некорректный формат email."

    if not password:
        errors["password"] = "Пароль обязателен."
    elif len(password) < 6:
        errors["password"] = "Пароль должен содержать не менее 6 символов."
    elif not PASSWORD_UPPER_RE.search(password):
        errors["password"] = "Пароль должен содержать хотя бы одну заглавную букву."
    elif not PASSWORD_DIGIT_RE.search(password):
        errors["password"] = "Пароль должен содержать хотя бы одну цифру."
    elif not PASSWORD_SPECIAL_RE.search(password):
        errors["password"] = "Пароль должен содержать хотя бы один специальный символ."

    return errors
