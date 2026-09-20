from pathlib import Path
import os

from dotenv import load_dotenv
from db import conectar_db

from datetime import date, timedelta


def comprobar_conexion():
    # Lee el .env ubicado junto a este archivo.
    ruta_env = Path(__file__).resolve().parent / ".env"
    load_dotenv(ruta_env, override=False)

    # Muestra el destino, sin exponer usuario ni contraseña.
    print("Host:", os.getenv("DB_HOST"))
    print("Puerto:", os.getenv("DB_PORT", "3306"))
    print("Base de origen configurada:", os.getenv("DB_NAME"))

    if os.getenv("DB_NAME") != "la_maestranza":
        raise RuntimeError(
            "Esta comprobación espera la base local la_maestranza. "
            "Revisa la configuración antes de continuar."
        )

    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        conexion.start_transaction(readonly=True)
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                DATABASE() AS base_actual,
                @@hostname AS servidor,
                VERSION() AS version_mysql
        """)

        informacion = cursor.fetchone()

        print("\nConexión establecida:")
        for campo, valor in informacion.items():
            print(f"  {campo}: {valor}")

        cursor.execute("""
            SELECT
                'alumnos' AS entidad,
                (SELECT COUNT(*)
                 FROM la_maestranza.alumnos) AS origen,
                (SELECT COUNT(*)
                 FROM la_maestranza_dw.dim_alumno) AS dw

            UNION ALL

            SELECT
                'talleres',
                (SELECT COUNT(*)
                 FROM la_maestranza.talleres),
                (SELECT COUNT(*)
                 FROM la_maestranza_dw.dim_taller)

            UNION ALL

            SELECT
                'reservas',
                (SELECT COUNT(*)
                 FROM la_maestranza.reservas_clase),
                (SELECT COUNT(*)
                 FROM la_maestranza_dw.fact_reservas)
        """)

        print("\nCantidades actuales:")
        for fila in cursor.fetchall():
            print(
                f"  {fila['entidad']}: "
                f"origen={fila['origen']}, DW={fila['dw']}"
            )

        print("\nComprobación terminada. No se modificaron datos.")

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None:
            if conexion.is_connected():
                conexion.rollback()
                conexion.close()



def sincronizar_dimensiones(id_ejecucion):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        conexion.start_transaction()
        cursor = conexion.cursor(dictionary=True)

        # Extraer los alumnos del origen.
        cursor.execute("""
            SELECT id_alumno, nombre, apellido
            FROM la_maestranza.alumnos
        """)
        alumnos = cursor.fetchall()

        # Extraer los talleres del origen.
        cursor.execute("""
            SELECT id_taller, nombre
            FROM la_maestranza.talleres
        """)
        talleres = cursor.fetchall()

        # Insertar alumnos nuevos o actualizar sus nombres.
        sql_alumnos = """
            INSERT INTO la_maestranza_dw.dim_alumno (
                id_alumno_origen,
                nombre,
                apellido
            )
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nombre = %s,
                apellido = %s
        """

        for alumno in alumnos:
            cursor.execute(
                sql_alumnos,
                (
                    alumno["id_alumno"],
                    alumno["nombre"],
                    alumno["apellido"],
                    alumno["nombre"],
                    alumno["apellido"],
                ),
            )

        # Insertar talleres nuevos o actualizar sus nombres.
        sql_talleres = """
            INSERT INTO la_maestranza_dw.dim_taller (
                id_taller_origen,
                nombre
            )
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                nombre = %s
        """

        for taller in talleres:
            cursor.execute(
                sql_talleres,
                (
                    taller["id_taller"],
                    taller["nombre"],
                    taller["nombre"],
                ),
            )

        # Guardar las cantidades de esta etapa.
        guardar_metricas(
            cursor,
            id_ejecucion,
            alumnos_procesados=len(alumnos),
            talleres_procesados=len(talleres),
        )

        # Confirmar las dimensiones y sus cantidades juntas.
        conexion.commit()

        print("\nDimensiones sincronizadas:")
        print(f"  Alumnos procesados: {len(alumnos)}")
        print(f"  Talleres procesados: {len(talleres)}")
        print("  Cambios confirmados en la_maestranza_dw.")

    except Exception:
        if conexion is not None and conexion.is_connected():
            conexion.rollback()

        print("\nLa sincronización falló; se revirtieron sus cambios.")
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()

def sincronizar_calendario(id_ejecucion):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        conexion.start_transaction()
        cursor = conexion.cursor(dictionary=True)

        # Obtener el rango de fechas necesario desde el origen.
        cursor.execute("""
            SELECT
                MIN(fecha) AS fecha_minima,
                MAX(fecha) AS fecha_maxima
            FROM (
                SELECT DATE(fecha_reserva) AS fecha
                FROM la_maestranza.reservas_clase

                UNION ALL

                SELECT fecha
                FROM la_maestranza.clases

                UNION ALL

                SELECT DATE(fecha_cancelacion)
                FROM la_maestranza.reservas_clase
                WHERE fecha_cancelacion IS NOT NULL
            ) AS fechas_origen
        """)

        rango = cursor.fetchone()

        if rango["fecha_minima"] is None:
            guardar_metricas(
                cursor,
                id_ejecucion,
                fechas_agregadas=0,
            )
            conexion.commit()
            print("\nCalendario: no hay fechas en el origen.")
            return

        inicio = date(rango["fecha_minima"].year, 1, 1)
        fin = date(rango["fecha_maxima"].year, 12, 31)

        cursor.execute("""
            SELECT fecha
            FROM la_maestranza_dw.dim_fecha
            WHERE fecha BETWEEN %s AND %s
        """, (inicio, fin))

        existentes = {
            fila["fecha"]
            for fila in cursor.fetchall()
        }

        nuevas_fechas = []
        fecha = inicio

        while fecha <= fin:
            if fecha not in existentes:
                nuevas_fechas.append((
                    fecha.year * 10000 + fecha.month * 100 + fecha.day,
                    fecha,
                    fecha.year,
                    fecha.month,
                    (fecha.month - 1) // 3 + 1,
                    fecha.day,
                    fecha.isoweekday(),
                ))

            if fecha == fin:
                break

            fecha += timedelta(days=1)

        if nuevas_fechas:
            cursor.executemany("""
                INSERT INTO la_maestranza_dw.dim_fecha (
                    fecha_key,
                    fecha,
                    anio,
                    mes,
                    trimestre,
                    dia_mes,
                    dia_semana
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, nuevas_fechas)

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM la_maestranza_dw.dim_fecha
            WHERE fecha BETWEEN %s AND %s
        """, (inicio, fin))

        total = cursor.fetchone()["total"]
        esperado = (fin - inicio).days + 1

        if total != esperado:
            raise RuntimeError(
                f"Calendario incompleto: {total} fechas; "
                f"se esperaban {esperado}."
            )

        

        guardar_metricas(
            cursor,
            id_ejecucion,
            fechas_agregadas=len(nuevas_fechas),
        )

        conexion.commit()

        print("\nCalendario sincronizado:")
        print(f"  Período cubierto: {inicio} a {fin}")
        print(f"  Fechas agregadas: {len(nuevas_fechas)}")
        print(f"  Fechas verificadas en el período: {total}")

    except Exception:
        if conexion is not None and conexion.is_connected():
            conexion.rollback()

        print("\nFalló el calendario; se revirtieron sus cambios.")
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()


def sincronizar_reservas(id_ejecucion):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        conexion.start_transaction(
            isolation_level="REPEATABLE READ",
            consistent_snapshot=True,
        )
        cursor = conexion.cursor(dictionary=True)

        # LEFT JOIN permite detectar relaciones faltantes
        # en lugar de excluir silenciosamente esas reservas.
        cursor.execute("""
            SELECT
                r.id_reserva AS id_reserva_origen,
                da.alumno_key,
                dt.taller_key,
                CAST(
                    DATE_FORMAT(r.fecha_reserva, '%Y%m%d')
                    AS UNSIGNED
                ) AS fecha_reserva_key,
                CAST(
                    DATE_FORMAT(c.fecha, '%Y%m%d')
                    AS UNSIGNED
                ) AS fecha_clase_key,
                CAST(
                    DATE_FORMAT(r.fecha_cancelacion, '%Y%m%d')
                    AS UNSIGNED
                ) AS fecha_cancelacion_key,
                r.id_clase AS id_clase_origen,
                r.id_inscripcion AS id_inscripcion_origen,
                r.estado AS estado_reserva,
                r.consume_clase,
                1 AS cantidad_reservas,
                i.id_taller AS taller_inscripcion,
                c.id_taller AS taller_clase
            FROM la_maestranza.reservas_clase AS r
            LEFT JOIN la_maestranza.inscripciones AS i
                ON i.id_inscripcion = r.id_inscripcion
            LEFT JOIN la_maestranza.clases AS c
                ON c.id_clase = r.id_clase
            LEFT JOIN la_maestranza_dw.dim_alumno AS da
                ON da.id_alumno_origen = i.id_alumno
            LEFT JOIN la_maestranza_dw.dim_taller AS dt
                ON dt.id_taller_origen = c.id_taller
        """)

        reservas = cursor.fetchall()

        campos = (
            "alumno_key",
            "taller_key",
            "fecha_reserva_key",
            "fecha_clase_key",
            "fecha_cancelacion_key",
            "id_clase_origen",
            "id_inscripcion_origen",
            "estado_reserva",
            "consume_clase",
            "cantidad_reservas",
        )

        columnas = ", ".join(campos)

        cursor.execute(f"""
            SELECT id_reserva_origen, {columnas}
            FROM la_maestranza_dw.fact_reservas
        """)

        existentes = {
            fila["id_reserva_origen"]: fila
            for fila in cursor.fetchall()
        }

        # Los nombres de columnas proceden de la lista fija anterior.
        marcadores = ", ".join(["%s"] * (len(campos) + 1))
        asignaciones = ", ".join(
            f"{campo} = %s" for campo in campos
        )

        sql_insertar = f"""
            INSERT INTO la_maestranza_dw.fact_reservas (
                id_reserva_origen,
                {columnas},
                fecha_actualizacion_dw
            )
            VALUES ({marcadores}, CURRENT_TIMESTAMP)
        """

        sql_actualizar = f"""
            UPDATE la_maestranza_dw.fact_reservas
            SET
                {asignaciones},
                fecha_actualizacion_dw = CURRENT_TIMESTAMP
            WHERE id_reserva_origen = %s
        """

        nuevas = 0
        actualizadas = 0
        sin_cambios = 0

        for reserva in reservas:
            id_reserva = reserva["id_reserva_origen"]

            # Solo la fecha de cancelación puede estar vacía.
            faltantes = [
                campo
                for campo in campos
                if campo != "fecha_cancelacion_key"
                and reserva[campo] is None
            ]

            if faltantes:
                raise RuntimeError(
                    f"Reserva {id_reserva}: faltan datos en "
                    f"{', '.join(faltantes)}. "
                    "Revisa el origen y las dimensiones."
                )

            if (
                reserva["taller_inscripcion"]
                != reserva["taller_clase"]
            ):
                raise RuntimeError(
                    f"Reserva {id_reserva}: el taller de la "
                    "inscripción no coincide con el de la clase."
                )

            valores = tuple(reserva[campo] for campo in campos)
            anterior = existentes.get(id_reserva)

            if anterior is None:
                cursor.execute(
                    sql_insertar,
                    (id_reserva,) + valores,
                )
                nuevas += 1

            elif any(
                reserva[campo] != anterior[campo]
                for campo in campos
            ):
                cursor.execute(
                    sql_actualizar,
                    valores + (id_reserva,),
                )
                actualizadas += 1

            else:
                sin_cambios += 1

        # Verificar los valores cargados antes de confirmar.
        cursor.execute(f"""
            SELECT id_reserva_origen, {columnas}
            FROM la_maestranza_dw.fact_reservas
        """)

        resultado_dw = {
            fila["id_reserva_origen"]: fila
            for fila in cursor.fetchall()
        }

        for reserva in reservas:
            id_reserva = reserva["id_reserva_origen"]
            cargada = resultado_dw.get(id_reserva)

            if cargada is None or any(
                cargada[campo] != reserva[campo]
                for campo in campos
            ):
                raise RuntimeError(
                    f"No se pudo validar la reserva {id_reserva}."
                )

        ids_origen = {
            reserva["id_reserva_origen"]
            for reserva in reservas
        }

        solo_en_dw = set(resultado_dw) - ids_origen

        # Obtener la última observación de cada reserva.
        cursor.execute("""
            SELECT
                h.id_reserva_origen,
                h.estado_nuevo
            FROM la_maestranza_dw.historial_estado_reserva AS h
            INNER JOIN (
                SELECT
                    id_reserva_origen,
                    MAX(id_historial) AS ultimo_id
                FROM la_maestranza_dw.historial_estado_reserva
                GROUP BY id_reserva_origen
            ) AS ultima
                ON ultima.ultimo_id = h.id_historial
        """)

        ultimos_estados = {
            fila["id_reserva_origen"]: fila["estado_nuevo"]
            for fila in cursor.fetchall()
        }

        observaciones_iniciales = 0
        cambios_estado = 0

        for reserva in reservas:
            id_reserva = reserva["id_reserva_origen"]
            estado_actual = reserva["estado_reserva"]

            if id_reserva not in ultimos_estados:
                # Primera observación: no inventar un estado anterior.
                estado_anterior = None
                observaciones_iniciales += 1

            else:
                estado_anterior = ultimos_estados[id_reserva]

                # Si el estado observado no cambió, no duplicar historial.
                if estado_anterior == estado_actual:
                    continue

                cambios_estado += 1

            cursor.execute("""
                INSERT INTO la_maestranza_dw.historial_estado_reserva (
                    id_reserva_origen,
                    estado_anterior,
                    estado_nuevo,
                    fecha_deteccion
                )
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP(6))
            """, (
                id_reserva,
                estado_anterior,
                estado_actual,
            ))

        guardar_metricas(
            cursor,
            id_ejecucion,
            reservas_nuevas=nuevas,
            reservas_actualizadas=actualizadas,
            reservas_sin_cambios=sin_cambios,
            reservas_verificadas=len(reservas),
            reservas_solo_dw=len(solo_en_dw),
            observaciones_iniciales=observaciones_iniciales,
            cambios_estado=cambios_estado,
        )

        conexion.commit()

        

        print("\nReservas sincronizadas:")
        print(f"  Nuevas: {nuevas}")
        print(f"  Actualizadas: {actualizadas}")
        print(f"  Sin cambios: {sin_cambios}")
        print(f"  Reservas del origen verificadas: {len(reservas)}")
        print(f"  Conservadas sin registro en origen: {len(solo_en_dw)}")
        print("\nHistorial de estados:")
        print(f"  Primeras observaciones: {observaciones_iniciales}")
        print(f"  Cambios de estado registrados: {cambios_estado}")

    except Exception:
        if conexion is not None and conexion.is_connected():
            conexion.rollback()

        print("\nFalló la carga de reservas; se revirtieron sus cambios.")
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()

def registrar_ejecucion(
    id_ejecucion=None,
    estado="en_proceso",
    mensaje_error=None,
):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        if id_ejecucion is None:
            cursor.execute("""
                INSERT INTO la_maestranza_dw.etl_ejecuciones (
                    estado
                )
                VALUES ('en_proceso')
            """)

            id_ejecucion = cursor.lastrowid

        else:
            if estado not in ("exitosa", "fallida"):
                raise ValueError("Estado final de ejecución no válido.")

            cursor.execute("""
                UPDATE la_maestranza_dw.etl_ejecuciones
                SET
                    estado = %s,
                    fecha_fin = CURRENT_TIMESTAMP(6),
                    mensaje_error = %s
                WHERE id_ejecucion = %s
                AND estado = 'en_proceso'
            """, (
                estado,
                mensaje_error,
                id_ejecucion,
            ))

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "No se pudo cerrar la ejecución en la bitácora."
                )

        conexion.commit()
        return id_ejecucion

    except Exception:
        if conexion is not None and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()


def guardar_metricas(cursor, id_ejecucion, **metricas):
    permitidas = {
        "alumnos_procesados",
        "talleres_procesados",
        "fechas_agregadas",
        "reservas_nuevas",
        "reservas_actualizadas",
        "reservas_sin_cambios",
        "reservas_verificadas",
        "reservas_solo_dw",
        "observaciones_iniciales",
        "cambios_estado",
    }

    if not metricas or not set(metricas).issubset(permitidas):
        raise ValueError("Métricas de ejecución no válidas.")

    if any(
        type(valor) is not int or valor < 0
        for valor in metricas.values()
    ):
        raise ValueError("Las cantidades deben ser enteros no negativos.")

    asignaciones = ", ".join(
        f"{campo} = %s" for campo in metricas
    )

    cursor.execute(
        f"""
            UPDATE la_maestranza_dw.etl_ejecuciones
            SET {asignaciones}
            WHERE id_ejecucion = %s
            AND estado = 'en_proceso'
        """,
        tuple(metricas.values()) + (id_ejecucion,),
    )

    if cursor.rowcount != 1:
        raise RuntimeError(
            "No se pudieron registrar las métricas de la etapa."
        )



if __name__ == "__main__":
    id_ejecucion = None
    etapa = "comprobación de conexión"

    try:
        # Verificar la configuración antes de escribir.
        comprobar_conexion()

        etapa = "inicio de bitácora"
        id_ejecucion = registrar_ejecucion()
        print(f"\nEjecución ETL #{id_ejecucion} iniciada.")

        etapa = "dimensiones"
        sincronizar_dimensiones(id_ejecucion)

        etapa = "calendario"
        sincronizar_calendario(id_ejecucion)

        etapa = "reservas e historial"
        sincronizar_reservas(id_ejecucion)

        etapa = "cierre de bitácora"
        registrar_ejecucion(
            id_ejecucion=id_ejecucion,
            estado="exitosa",
        )

        print(f"\nEjecución ETL #{id_ejecucion} finalizada con éxito.")

    except Exception as error:
        # Registrar un resumen sin copiar posibles credenciales
        # contenidas en mensajes externos.
        resumen = (
            f"Etapa: {etapa}. "
            f"Tipo de error: {type(error).__name__}."
        )

        codigo = getattr(error, "errno", None)
        if isinstance(codigo, int):
            resumen += f" Código MySQL: {codigo}."

        print(f"\nERROR: {resumen}")

        if id_ejecucion is not None:
            try:
                registrar_ejecucion(
                    id_ejecucion=id_ejecucion,
                    estado="fallida",
                    mensaje_error=resumen,
                )
            except Exception:
                print(
                    "No se pudo guardar el resultado final en la bitácora. "
                    "Revisa el registro de esta ejecución."
                )

        raise SystemExit(1)