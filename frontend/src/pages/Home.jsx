import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="page page-home">
      <h1>Облачное файловое хранилище</h1>
      <p>
        Простое веб-приложение для хранения ваших файлов в облаке — загружайте, храните,
        переименовывайте и делитесь файлами по специальной ссылке, как в Google Drive,
        Яндекс.Диске или Dropbox.
      </p>
      <ul className="feature-list">
        <li>Личное файловое хранилище для каждого пользователя</li>
        <li>Загрузка файлов с комментарием</li>
        <li>Переименование, удаление, скачивание файлов</li>
        <li>Обезличенная специальная ссылка для доступа к файлу без входа в систему</li>
        <li>Административная панель управления пользователями</li>
      </ul>

      {!user && (
        <div className="home-cta">
          <Link to="/register" className="btn btn-primary">
            Зарегистрироваться
          </Link>
          <Link to="/login" className="btn btn-secondary">
            Войти
          </Link>
        </div>
      )}
      {user && (
        <div className="home-cta">
          <Link to="/storage" className="btn btn-primary">
            Перейти в моё хранилище
          </Link>
        </div>
      )}
    </div>
  );
}
