import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">☁️ Облачное хранилище</Link>
      </div>
      <div className="navbar-links">
        {user && (
          <Link to="/storage" title="Моё файловое хранилище">
            Моё хранилище
          </Link>
        )}
        {user && user.is_admin && <Link to="/admin">Администрирование</Link>}

        {!user && (
          <>
            <Link to="/login">Вход</Link>
            <Link to="/register" className="navbar-cta">
              Регистрация
            </Link>
          </>
        )}
        {user && (
          <span className="navbar-user">
            {user.full_name || user.username}
            {user.is_admin && <span className="badge">admin</span>}
            <button className="link-btn" onClick={handleLogout}>
              Выход
            </button>
          </span>
        )}
      </div>
    </nav>
  );
}
