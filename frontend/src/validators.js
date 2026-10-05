const LOGIN_RE = /^[A-Za-z][A-Za-z0-9]{3,19}$/;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateRegistration({ username, full_name, email, password }) {
  const errors = {};

  if (!username || !username.trim()) {
    errors.username = "Логин обязателен.";
  } else if (!LOGIN_RE.test(username.trim())) {
    errors.username =
      "Только латинские буквы и цифры, первый символ — буква, длина от 4 до 20 символов.";
  }

  if (!full_name || !full_name.trim()) {
    errors.full_name = "Укажите полное имя.";
  }

  if (!email || !email.trim()) {
    errors.email = "Email обязателен.";
  } else if (!EMAIL_RE.test(email.trim())) {
    errors.email = "Некорректный формат email.";
  }

  if (!password) {
    errors.password = "Пароль обязателен.";
  } else if (password.length < 6) {
    errors.password = "Пароль должен содержать не менее 6 символов.";
  } else if (!/[A-ZА-Я]/.test(password)) {
    errors.password = "Пароль должен содержать хотя бы одну заглавную букву.";
  } else if (!/\d/.test(password)) {
    errors.password = "Пароль должен содержать хотя бы одну цифру.";
  } else if (!/[^A-Za-z0-9А-Яа-я]/.test(password)) {
    errors.password = "Пароль должен содержать хотя бы один специальный символ.";
  }

  return errors;
}
