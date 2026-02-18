from typing import Optional, List, Dict, Any
from backend.db import conectar, _fetchall_dict


def agregar_habitacion(
    piso: int,
    numero: int,
    tipo: str,
    capacidad: int = 2,
    precio_base: Optional[float] = None
) -> int:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Habitaciones (piso, numero, tipo, capacidad, precio_base)
        VALUES (?, ?, ?, ?, ?)
    """, (piso, numero, tipo.strip(), capacidad, precio_base))

    conn.commit()
    hid = cur.lastrowid
    conn.close()
    return hid


def set_estado_habitacion(habitacion_id: int, estado: str) -> None:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        UPDATE Habitaciones
        SET estado = ?
        WHERE id = ?
    """, (estado, habitacion_id))

    conn.commit()
    conn.close()


def listar_habitaciones() -> List[Dict[str, Any]]:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, piso, numero, tipo, capacidad, estado, precio_base
        FROM Habitaciones
        ORDER BY piso, numero
    """)

    res = _fetchall_dict(cur)
    conn.close()
    return res


def habitaciones_disponibles_simple(
    fecha_desde: str,
    fecha_hasta: str,
    incluir_tipo: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = conectar()
    cur = conn.cursor()

    tipo_filter = ""
    params: List[Any] = [fecha_hasta, fecha_desde, fecha_hasta, fecha_desde]

    if incluir_tipo:
        tipo_filter = " AND h.tipo = ?"
        params.append(incluir_tipo.strip())

    cur.execute(f"""
        SELECT h.id, h.piso, h.numero, h.tipo,
               h.capacidad, h.estado, h.precio_base
        FROM Habitaciones h
        WHERE h.estado IN ('DISPONIBLE','LIMPIEZA')
          {tipo_filter}
          AND h.id NOT IN (
              SELECT e.habitacion_id
              FROM Estadias e
              WHERE e.fecha_desde < ?
                AND ? < COALESCE(e.fecha_hasta, '9999-12-31')
          )
          AND h.id NOT IN (
              SELECT r.habitacion_id
              FROM Reservas r
              WHERE r.habitacion_id IS NOT NULL
                AND r.estado IN ('PENDIENTE','CONFIRMADA')
                AND r.fecha_desde < ?
                AND ? < r.fecha_hasta
          )
        ORDER BY h.piso, h.numero
    """, tuple(params))

    res = _fetchall_dict(cur)
    conn.close()
    return res
