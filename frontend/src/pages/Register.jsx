import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { validateRegistration } from "../validators";

const initialForm = { username: "", full_name: "", email: "", password: "" };

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError("");
    const clientErrors = validateRegistration(form);
    setErrors(clientErrors);
    if (Object.keys(clientErrors).length > 0) return;

    setSubmitting(true);
    try {
      await register(form);
      navigate("/storage");
    } catch (err) {
      setServerError(err.message);
      if (err.details) setErrors(err.details);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page page-form">
      <h1>Регистрация</h1>
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="username">Логин</label>
          <input id="username" name="username" value={form.username} onChange={handleChange} />
          {errors.username && <div className="field-error">{errors.username}</div>}
        </div>

        <div className="form-field">
          <label htmlFor="full_name">Полное имя</label>
          <input id="full_name" name="full_name" value={form.full_name} onChange={handleChange} />
          {errors.full_name && <div className="field-error">{errors.full_name}</div>}
        </div>

        <div className="form-field">
          <label htmlFor="email">Email</label>
          <input id="email" name="email" type="email" value={form.email} onChange={handleChange} />
          {errors.email && <div className="field-error">{errors.email}</div>}
        </div>

        <div className="form-field">
          <label htmlFor="password">Пароль</label>
          <input
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
          />
          {errors.password && <div className="field-error">{errors.password}</div>}
          <div className="field-hint">
            Не менее 6 символов, минимум одна заглавная буква, цифра и спецсимвол.
          </div>
        </div>

        {serverError && <div className="form-error">{serverError}</div>}

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Отправка…" : "Зарегистрироваться"}
        </button>
      </form>
      <p>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </div>
  );
}
