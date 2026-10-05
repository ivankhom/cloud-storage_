import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import { useAuth } from "../AuthContext";

function formatSize(bytes) {
  if (!bytes) return "0 Б";
  const units = ["Б", "КБ", "МБ", "ГБ"];
  let i = 0;
  let value = bytes;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export default function Admin() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const list = await api.userList();
      setUsers(list);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (u) => {
    if (!window.confirm(`Удалить пользователя «${u.username}»? Это действие необратимо.`)) return;
    try {
      await api.userDelete(u.id);
      setUsers((prev) => prev.filter((x) => x.id !== u.id));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleToggleAdmin = async (u) => {
    try {
      const updated = await api.userSetAdmin(u.id, !u.is_admin);
      setUsers((prev) => prev.map((x) => (x.id === u.id ? updated : x)));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page page-admin">
      <h1>Администрирование пользователей</h1>
      {error && <div className="form-error">{error}</div>}
      {loading ? (
        <p>Загрузка…</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Логин</th>
              <th>Полное имя</th>
              <th>Email</th>
              <th>Администратор</th>
              <th>Файлов</th>
              <th>Размер</th>
              <th>Хранилище</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.username}</td>
                <td>{u.full_name}</td>
                <td>{u.email}</td>
                <td>
                  <label className="switch" title="Признак администратора">
                    <input
                      type="checkbox"
                      checked={u.is_admin}
                      disabled={u.id === currentUser.id}
                      onChange={() => handleToggleAdmin(u)}
                    />
                    <span>{u.is_admin ? "да" : "нет"}</span>
                  </label>
                </td>
                <td>{u.files_count}</td>
                <td>{formatSize(u.files_size)}</td>
                <td>
                  <Link to={`/storage?user=${u.id}`}>Открыть хранилище</Link>
                </td>
                <td>
                  <button
                    className="btn btn-danger btn-sm"
                    disabled={u.id === currentUser.id}
                    onClick={() => handleDelete(u)}
                    title={u.id === currentUser.id ? "Нельзя удалить самого себя" : "Удалить пользователя"}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
