from typing import Optional, List, Dict, Any
from backend.db import conectar, _fetchall_dict, _fetchone_dict


def agregar_cliente(nombre: str, documento: str,
                    empresa: Optional[str] = None,
                    telefono: Optional[str] = None,
                    cuit: Optional[str] = None) -> int:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Clientes (nombre, documento, empresa, telefono, cuit)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre.strip(), documento.strip(), empresa, telefono, cuit))

    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def buscar_cliente_por_nombre(nombre: str) -> List[Dict[str, Any]]:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM Clientes
        WHERE LOWER(TRIM(nombre)) LIKE LOWER(TRIM(?))
        ORDER BY nombre
    """, (f"%{nombre.strip()}%",))

    res = _fetchall_dict(cur)
    conn.close()
    return res


def buscar_cliente_por_documento(documento: str) -> Optional[Dict[str, Any]]:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM Clientes
        WHERE TRIM(documento) = TRIM(?)
    """, (documento.strip(),))

    res = _fetchone_dict(cur)
    conn.close()
    return res


def buscar_cliente_por_cuit(cuit: str) -> Optional[Dict[str, Any]]:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM Clientes
        WHERE TRIM(cuit) = TRIM(?)
    """, (cuit.strip(),))

    res = _fetchone_dict(cur)
    conn.close()
    return res


def historial_cliente(cliente_id: int) -> Dict[str, Any]:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT e.*, h.numero, h.piso, h.tipo
        FROM Estadias e
        JOIN Habitaciones h ON h.id = e.habitacion_id
        WHERE e.cliente_id = ?
    """, (cliente_id,))
    estadias = _fetchall_dict(cur)

    cur.execute("""
        SELECT r.*, h.numero, h.piso, h.tipo
        FROM Reservas r
        LEFT JOIN Habitaciones h ON h.id = r.habitacion_id
        WHERE r.cliente_id = ?
    """, (cliente_id,))
    reservas = _fetchall_dict(cur)

    conn.close()
    return {"estadias": estadias, "reservas": reservas}
