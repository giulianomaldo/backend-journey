from typing import Optional
from backend.db import conectar


def crear_reserva(
    cliente_id: int,
    fecha_desde: str,
    fecha_hasta: str,
    habitacion_id: Optional[int] = None,
    estado: str = "PENDIENTE",
    cant_huespedes: int = 1,
    origen: Optional[str] = None,
    observaciones: Optional[str] = None
) -> int:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Reservas (
            cliente_id, habitacion_id,
            fecha_desde, fecha_hasta,
            estado, cant_huespedes,
            origen, observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cliente_id, habitacion_id,
        fecha_desde, fecha_hasta,
        estado, cant_huespedes,
        origen, observaciones
    ))

    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def cambiar_estado_reserva(reserva_id: int, estado: str) -> None:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        UPDATE Reservas
        SET estado = ?
        WHERE id = ?
    """, (estado, reserva_id))

    conn.commit()
    conn.close()


def check_in_desde_reserva(
    reserva_id: int,
    habitacion_id: Optional[int] = None
) -> int:
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, cliente_id, habitacion_id,
               fecha_desde, fecha_hasta, estado
        FROM Reservas
        WHERE id = ?
    """, (reserva_id,))

    r = cur.fetchone()
    if not r:
        conn.close()
        raise ValueError("Reserva inexistente.")

    if r["estado"] in ("CANCELADA", "NO_SHOW"):
        conn.close()
        raise ValueError(
            f"No se puede hacer check-in: reserva en estado {r['estado']}."
        )

    hab_id = habitacion_id if habitacion_id is not None else r["habitacion_id"]
    if hab_id is None:
        conn.close()
        raise ValueError(
            "La reserva no tiene habitación asignada."
        )

    cur.execute("""
        INSERT INTO Estadias (
            habitacion_id, cliente_id,
            reserva_id, fecha_desde, fecha_hasta
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        hab_id, r["cliente_id"],
        r["id"], r["fecha_desde"], r["fecha_hasta"]
    ))

    estadia_id = cur.lastrowid

    cur.execute("""
        UPDATE Reservas
        SET estado = 'CHECKED_IN',
            habitacion_id = ?
        WHERE id = ?
    """, (hab_id, reserva_id))

    cur.execute("""
        UPDATE Habitaciones
        SET estado = 'OCUPADA'
        WHERE id = ?
    """, (hab_id,))

    conn.commit()
    conn.close()
    return estadia_id
