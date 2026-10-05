import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
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

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("ru-RU");
}

export default function Storage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const targetUserId = searchParams.get("user");
  const isViewingOther = user?.is_admin && targetUserId && Number(targetUserId) !== user.id;

  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [uploadComment, setUploadComment] = useState("");
  const [uploading, setUploading] = useState(false);
  const [renamingId, setRenamingId] = useState(null);
  const [renameValue, setRenameValue] = useState("");
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [commentValue, setCommentValue] = useState("");
  const [copiedId, setCopiedId] = useState(null);
  const fileInputRef = useRef(null);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const list = await api.fileList(isViewingOther ? targetUserId : null);
      setFiles(list);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetUserId]);

  const handleUpload = async (e) => {
    e.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Выберите файл для загрузки.");
      return;
    }
    setUploading(true);
    setError("");
    try {
      const created = await api.fileUpload(
        file,
        uploadComment,
        isViewingOther ? targetUserId : null
      );
      setFiles((prev) => [created, ...prev]);
      setUploadComment("");
      fileInputRef.current.value = "";
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (f) => {
    if (!window.confirm(`Удалить файл «${f.original_name}»?`)) return;
    try {
      await api.fileDelete(f.id);
      setFiles((prev) => prev.filter((x) => x.id !== f.id));
    } catch (err) {
      setError(err.message);
    }
  };

  const startRename = (f) => {
    setRenamingId(f.id);
    setRenameValue(f.original_name);
  };

  const submitRename = async (f) => {
    try {
      const updated = await api.fileRename(f.id, renameValue.trim());
      setFiles((prev) => prev.map((x) => (x.id === f.id ? updated : x)));
      setRenamingId(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const startComment = (f) => {
    setEditingCommentId(f.id);
    setCommentValue(f.comment || "");
  };

  const submitComment = async (f) => {
    try {
      const updated = await api.fileComment(f.id, commentValue);
      setFiles((prev) => prev.map((x) => (x.id === f.id ? updated : x)));
      setEditingCommentId(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCopyLink = async (f) => {
    const link = api.filePublicUrl(f.link_token);
    try {
      await navigator.clipboard.writeText(link);
    } catch {
      window.prompt("Скопируйте ссылку:", link);
    }
    setCopiedId(f.id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  return (
    <div className="page page-storage">
      <h1>{isViewingOther ? `Хранилище пользователя #${targetUserId}` : "Моё файловое хранилище"}</h1>

      <form className="upload-form" onSubmit={handleUpload}>
        <input ref={fileInputRef} type="file" />
        <input
          type="text"
          placeholder="Комментарий к файлу (необязательно)"
          value={uploadComment}
          onChange={(e) => setUploadComment(e.target.value)}
        />
        <button type="submit" className="btn btn-primary" disabled={uploading}>
          {uploading ? "Загрузка…" : "Загрузить файл"}
        </button>
      </form>

      {error && <div className="form-error">{error}</div>}

      {loading ? (
        <p>Загрузка…</p>
      ) : files.length === 0 ? (
        <p>В хранилище пока нет файлов.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Имя файла</th>
              <th>Комментарий</th>
              <th>Размер</th>
              <th>Загружен</th>
              <th>Скачан</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {files.map((f) => (
              <tr key={f.id}>
                <td>
                  {renamingId === f.id ? (
                    <form
                      className="inline-edit"
                      onSubmit={(e) => {
                        e.preventDefault();
                        submitRename(f);
                      }}
                    >
                      <input
                        autoFocus
                        value={renameValue}
                        onChange={(e) => setRenameValue(e.target.value)}
                        onKeyDown={(e) => e.key === "Escape" && setRenamingId(null)}
                      />
                      <button type="submit" className="btn btn-sm" title="Сохранить (Enter)">
                        ✓
                      </button>
                      <button type="button" className="btn btn-sm" title="Отмена (Esc)" onClick={() => setRenamingId(null)}>
                        ✕
                      </button>
                    </form>
                  ) : (
                    <>
                      {f.original_name}{" "}
                      <button className="link-btn" onClick={() => startRename(f)} title="Переименовать">
                        ✏️
                      </button>
                    </>
                  )}
                </td>
                <td>
                  {editingCommentId === f.id ? (
                    <form
                      className="inline-edit"
                      onSubmit={(e) => {
                        e.preventDefault();
                        submitComment(f);
                      }}
                    >
                      <input
                        autoFocus
                        value={commentValue}
                        onChange={(e) => setCommentValue(e.target.value)}
                        onKeyDown={(e) => e.key === "Escape" && setEditingCommentId(null)}
                      />
                      <button type="submit" className="btn btn-sm" title="Сохранить (Enter)">
                        ✓
                      </button>
                      <button type="button" className="btn btn-sm" title="Отмена (Esc)" onClick={() => setEditingCommentId(null)}>
                        ✕
                      </button>
                    </form>
                  ) : (
                    <>
                      {f.comment || <span className="muted">—</span>}{" "}
                      <button className="link-btn" onClick={() => startComment(f)} title="Изменить комментарий">
                        ✏️
                      </button>
                    </>
                  )}
                </td>
                <td>{formatSize(f.size)}</td>
                <td>{formatDate(f.uploaded_at)}</td>
                <td>{formatDate(f.last_downloaded_at)}</td>
                <td className="actions-cell">
                  <a className="btn btn-sm" href={api.fileDownloadUrl(f.id)} target="_blank" rel="noreferrer">
                    Скачать
                  </a>
                  <button className="btn btn-sm" onClick={() => handleCopyLink(f)}>
                    {copiedId === f.id ? "Скопировано!" : "Спец. ссылка"}
                  </button>
                  <button className="btn btn-sm btn-danger" onClick={() => handleDelete(f)}>
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
