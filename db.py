import sqlite3
from typing import Optional, List, Dict, Any

DB_PATH = "hotel_Karin.db"


def conectar(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_db() -> None:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        documento TEXT NOT NULL,
        empresa TEXT,
        telefono TEXT,
        cuit TEXT,
        UNIQUE(TRIM(documento)),
        UNIQUE(TRIM(cuit))
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Habitaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        piso INTEGER NOT NULL,
        numero INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        capacidad INTEGER DEFAULT 2,
        estado TEXT NOT NULL DEFAULT 'DISPONIBLE'
            CHECK (estado IN ('DISPONIBLE','OCUPADA','LIMPIEZA','MANTENIMIENTO')),
        precio_base REAL,
        UNIQUE(piso, numero)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        habitacion_id INTEGER,
        fecha_desde TEXT NOT NULL,
        fecha_hasta TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'PENDIENTE'
            CHECK (estado IN ('PENDIENTE','CONFIRMADA','CANCELADA','NO_SHOW','CHECKED_IN')),
        cant_huespedes INTEGER DEFAULT 1,
        origen TEXT,
        observaciones TEXT,
        FOREIGN KEY (cliente_id) REFERENCES Clientes(id),
        FOREIGN KEY (habitacion_id) REFERENCES Habitaciones(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Estadias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habitacion_id INTEGER NOT NULL,
        cliente_id INTEGER NOT NULL,
        reserva_id INTEGER,
        fecha_desde TEXT NOT NULL,
        fecha_hasta TEXT,
        FOREIGN KEY (habitacion_id) REFERENCES Habitaciones(id),
        FOREIGN KEY (cliente_id) REFERENCES Clientes(id),
        FOREIGN KEY (reserva_id) REFERENCES Reservas(id)
    );
    """)

    conn.commit()
    conn.close()


def _fetchall_dict(cur: sqlite3.Cursor) -> List[Dict[str, Any]]:
    return [dict(r) for r in cur.fetchall()]


def _fetchone_dict(cur: sqlite3.Cursor) -> Optional[Dict[str, Any]]:
    row = cur.fetchone()
    return dict(row) if row else None
