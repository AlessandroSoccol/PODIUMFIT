import sqlite3
from datetime import datetime, timezone


class UsuarioRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _conectar(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def obtener_por_username(self, username: str) -> sqlite3.Row | None:
        with self._conectar() as conn:
            cur = conn.execute(
                "SELECT id, username, email, first_name, password, is_active "
                "FROM auth_user WHERE username = ?",
                (username,),
            )
            return cur.fetchone()

    def existe_username(self, username: str) -> bool:
        with self._conectar() as conn:
            cur = conn.execute(
                "SELECT 1 FROM auth_user WHERE username = ? LIMIT 1", (username,)
            )
            return cur.fetchone() is not None

    def crear(self, *, username: str, email: str, first_name: str, password_hash: str) -> int:
        ahora = datetime.now(timezone.utc).isoformat(sep=" ")
        with self._conectar() as conn:
            cur = conn.execute(
                """
                INSERT INTO auth_user
                    (password, last_login, is_superuser, username, first_name,
                     last_name, email, is_staff, is_active, date_joined)
                VALUES (?, NULL, 0, ?, ?, '', ?, 0, 1, ?)
                """,
                (password_hash, username, first_name, email, ahora),
            )
            conn.commit()
            return cur.lastrowid

    def actualizar_last_login(self, user_id: int) -> None:
        ahora = datetime.now(timezone.utc).isoformat(sep=" ")
        with self._conectar() as conn:
            conn.execute(
                "UPDATE auth_user SET last_login = ? WHERE id = ?", (ahora, user_id)
            )
            conn.commit()
