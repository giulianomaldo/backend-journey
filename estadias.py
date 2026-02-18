from typing import List, Dict, Any
from backend.db import conectar, _fetchall_dict


def check_out(estadia_id: int, fecha_hasta: str) -> None:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT habitacion_id
        FROM Estadias
        WHERE id = ?
    """, (estadia_id,))

    e = cur.fetchone()
    if not e:
        conn.close()
        raise ValueError("Estadía inexistente.")

    cur.execute("""
        UPDATE Estadias
        SET fecha_hasta = ?
        WHERE id = ?
    """, (fecha_hasta, estadia_id))

    cur.execute("""
        UPDATE Habitaciones
        SET estado = 'LIMPIEZA'
        WHERE id = ?
    """, (e["habitacion_id"],))

    conn.commit()
    conn.close()


def ocupacion_hoy(fecha_hoy: str) -> List[Dict[str, Any]]:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT e.id AS estadia_id,
               e.fecha_desde, e.fecha_hasta,
               c.id AS cliente_id,
               c.nombre, c.documento, c.telefono,
               h.id AS habitacion_id,
               h.piso, h.numero, h.tipo
        FROM Estadias e
        JOIN Clientes c ON c.id = e.cliente_id
        JOIN Habitaciones h ON h.id = e.habitacion_id
        WHERE e.fecha_desde <= ?
          AND (e.fecha_hasta IS NULL OR ? < e.fecha_hasta)
        ORDER BY h.piso, h.numero
    """, (fecha_hoy, fecha_hoy))

    res = _fetchall_dict(cur)
    conn.close()
    return res


def checkouts_del_dia(fecha_hoy: str) -> List[Dict[str, Any]]:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT e.id AS estadia_id,
               e.fecha_desde, e.fecha_hasta,
               c.nombre, c.documento, c.telefono,
               h.piso, h.numero, h.tipo
        FROM Estadias e
        JOIN Clientes c ON c.id = e.cliente_id
        JOIN Habitaciones h ON h.id = e.habitacion_id
        WHERE e.fecha_hasta = ?
        ORDER BY h.piso, h.numero
    """, (fecha_hoy,))

    res = _fetchall_dict(cur)
    conn.close()
    return res
