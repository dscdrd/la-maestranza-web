from db import conectar_db




# ============================================================
# SERVICIOS - LÓGICA DE NEGOCIO
# LA MAESTRANZA
# ============================================================



# ============================================================
# USUARIOS / AUTENTICACIÓN
# ============================================================

def obtener_usuario_login(correo, rol):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT *
            FROM usuarios
            WHERE correo = %s
            AND rol = %s
            AND activo = 1
        """, (
            correo,
            rol
        ))

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()

# ============================================================
# ALUMNOS
# ============================================================

def correo_usuario_existe(correo):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT id_usuario
            FROM usuarios
            WHERE correo = %s
        """, (correo,))

        usuario = cursor.fetchone()

        return usuario is not None

    finally:

        cursor.close()
        conexion.close()

def rut_alumno_existe(rut):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT id_alumno
            FROM alumnos
            WHERE rut = %s
        """, (rut,))

        alumno = cursor.fetchone()

        return alumno is not None

    finally:

        cursor.close()
        conexion.close()

def crear_alumno(
    correo,
    contrasena_hash,
    nombre,
    apellido,
    rut,
    fecha_nacimiento,
    telefono,
    contacto_emergencia,
    telefono_emergencia
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        # --------------------------------------------------
        # CREAR USUARIO
        # --------------------------------------------------

        cursor.execute("""
            INSERT INTO usuarios (
                correo,
                contrasena,
                rol
            )
            VALUES (%s, %s, 'alumno')
        """, (
            correo,
            contrasena_hash
        ))

        id_usuario = cursor.lastrowid

        # --------------------------------------------------
        # CREAR ALUMNO
        # --------------------------------------------------

        cursor.execute("""
            INSERT INTO alumnos (
                id_usuario,
                nombre,
                apellido,
                rut,
                fecha_nacimiento,
                telefono,
                contacto_emergencia,
                telefono_emergencia
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            id_usuario,
            nombre,
            apellido,
            rut,
            fecha_nacimiento,
            telefono,
            contacto_emergencia,
            telefono_emergencia
        ))

        id_alumno = cursor.lastrowid

        conexion.commit()

        return {
            "id_alumno": id_alumno,
            "id_usuario": id_usuario,
            "nombre": nombre,
            "apellido": apellido,
            "rut": rut,
            "correo": correo
        }

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def obtener_alumno_por_usuario(id_usuario):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_alumno,
                nombre,
                apellido,
                rut,
                fecha_nacimiento,
                telefono,
                contacto_emergencia,
                telefono_emergencia,
                foto_perfil
            FROM alumnos
            WHERE id_usuario = %s
        """, (id_usuario,))

        alumno = cursor.fetchone()

        # Convertir DATE de MySQL para JSON
        if alumno and alumno["fecha_nacimiento"]:
            alumno["fecha_nacimiento"] = (
                alumno["fecha_nacimiento"].strftime("%Y-%m-%d")
            )

        return alumno

    finally:

        cursor.close()
        conexion.close()


def actualizar_perfil_alumno(
    id_usuario,
    nombre,
    apellido,
    telefono,
    contacto_emergencia,
    telefono_emergencia
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE alumnos
            SET
                nombre = %s,
                apellido = %s,
                telefono = %s,
                contacto_emergencia = %s,
                telefono_emergencia = %s
            WHERE id_usuario = %s
        """, (
            nombre,
            apellido,
            telefono,
            contacto_emergencia,
            telefono_emergencia,
            id_usuario
        ))

        conexion.commit()

        return {
            "nombre": nombre,
            "apellido": apellido,
            "telefono": telefono,
            "contacto_emergencia": contacto_emergencia,
            "telefono_emergencia": telefono_emergencia
        }

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def desactivar_cuenta_alumno(id_usuario):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE usuarios
            SET activo = 0
            WHERE id_usuario = %s
            AND rol = 'alumno'
            AND activo = 1
        """, (id_usuario,))

        cuenta_desactivada = cursor.rowcount > 0

        if cuenta_desactivada:
            conexion.commit()
        else:
            conexion.rollback()

        return cuenta_desactivada

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def actualizar_foto_alumno(
    id_usuario,
    nombre_archivo
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE alumnos
            SET foto_perfil = %s
            WHERE id_usuario = %s
        """, (
            nombre_archivo,
            id_usuario
        ))

        conexion.commit()

        return True

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def eliminar_cuenta_alumno(id_usuario):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # -----------------------------------------------
        # OBTENER ALUMNO
        # -----------------------------------------------

        cursor.execute("""
            SELECT id_alumno
            FROM alumnos
            WHERE id_usuario = %s
        """, (id_usuario,))

        alumno = cursor.fetchone()

        if not alumno:
            return False

        id_alumno = alumno["id_alumno"]

        # -----------------------------------------------
        # ELIMINAR PAGOS
        # -----------------------------------------------

        cursor.execute("""
            DELETE FROM pagos
            WHERE id_alumno = %s
        """, (id_alumno,))

        # -----------------------------------------------
        # ELIMINAR RESERVAS DE CLASE
        # -----------------------------------------------

        cursor.execute("""
            DELETE r
            FROM reservas_clase r
            INNER JOIN inscripciones i
                ON r.id_inscripcion = i.id_inscripcion
            WHERE i.id_alumno = %s
        """, (id_alumno,))

        # -----------------------------------------------
        # ELIMINAR CITAS TERAPÉUTICAS
        # -----------------------------------------------

        cursor.execute("""
            DELETE FROM citas_terapeuticas
            WHERE id_alumno = %s
        """, (id_alumno,))

        # -----------------------------------------------
        # ELIMINAR INSCRIPCIONES
        # -----------------------------------------------

        cursor.execute("""
            DELETE FROM inscripciones
            WHERE id_alumno = %s
        """, (id_alumno,))

        # -----------------------------------------------
        # ELIMINAR ALUMNO
        # -----------------------------------------------

        cursor.execute("""
            DELETE FROM alumnos
            WHERE id_alumno = %s
        """, (id_alumno,))

        # -----------------------------------------------
        # ELIMINAR USUARIO
        # -----------------------------------------------

        cursor.execute("""
            DELETE FROM usuarios
            WHERE id_usuario = %s
        """, (id_usuario,))

        conexion.commit()

        return True

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()



def obtener_estadisticas_alumno(id_usuario):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # ==================================================
        # 1. OBTENER ALUMNO
        # ==================================================

        cursor.execute("""
            SELECT
                id_alumno,
                nombre,
                apellido
            FROM alumnos
            WHERE id_usuario = %s
        """, (id_usuario,))

        alumno = cursor.fetchone()

        if not alumno:
            return None


        id_alumno = alumno["id_alumno"]


        # ==================================================
        # 2. TALLERES Y CLASES CONTRATADAS VIGENTES
        # ==================================================

        cursor.execute("""
            SELECT
                COUNT(DISTINCT id_taller)
                    AS talleres_vigentes,

                COALESCE(
                    SUM(clases_contratadas),
                    0
                )
                    AS clases_contratadas_vigentes

            FROM inscripciones

            WHERE id_alumno = %s
            AND estado = 'activa'
            AND fecha_inicio <= CURDATE()
            AND fecha_vencimiento >= CURDATE()
        """, (id_alumno,))

        planes = cursor.fetchone()


        # ==================================================
        # 3. RESERVAS
        # ==================================================

        cursor.execute("""
            SELECT

                COUNT(*)
                    AS total_reservas,

                COALESCE(
                    SUM(
                        CASE
                            WHEN r.estado = 'cancelada'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                )
                    AS reservas_canceladas,

                COALESCE(
                    SUM(
                        CASE
                            WHEN r.estado = 'reservada'
                            AND c.estado = 'programada'
                            AND TIMESTAMP(
                                c.fecha,
                                c.hora_inicio
                            ) > NOW()
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                )
                    AS reservas_proximas

            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON i.id_inscripcion =
                    r.id_inscripcion

            INNER JOIN clases c
                ON c.id_clase =
                    r.id_clase

            WHERE i.id_alumno = %s
        """, (id_alumno,))

        reservas = cursor.fetchone()


        # ==================================================
        # 4. TALLERES MÁS RESERVADOS
        # ==================================================

        cursor.execute("""
            SELECT

                t.nombre AS taller,

                COUNT(*) AS reservas

            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON i.id_inscripcion =
                    r.id_inscripcion

            INNER JOIN clases c
                ON c.id_clase =
                    r.id_clase

            INNER JOIN talleres t
                ON t.id_taller =
                    c.id_taller

            WHERE i.id_alumno = %s

            AND r.estado = 'reservada'

            AND c.estado <> 'cancelada'

            GROUP BY
                t.id_taller,
                t.nombre

            ORDER BY
                reservas DESC,
                t.nombre
        """, (id_alumno,))

        talleres = cursor.fetchall()


        # ==================================================
        # 5. NORMALIZAR DATOS
        # ==================================================

        estadisticas = {

            "talleres_vigentes":
                int(
                    planes["talleres_vigentes"]
                    or 0
                ),

            "clases_contratadas_vigentes":
                int(
                    planes[
                        "clases_contratadas_vigentes"
                    ]
                    or 0
                ),

            "reservas_proximas":
                int(
                    reservas["reservas_proximas"]
                    or 0
                ),

            "total_reservas":
                int(
                    reservas["total_reservas"]
                    or 0
                ),

            "reservas_canceladas":
                int(
                    reservas[
                        "reservas_canceladas"
                    ]
                    or 0
                ),

            "porcentaje_asistencia":
                None,

            "porcentaje_inasistencia":
                None

        }


        talleres_formateados = [

            {
                "taller":
                    taller["taller"],

                "reservas":
                    int(
                        taller["reservas"]
                        or 0
                    )
            }

            for taller in talleres

        ]


        # ==================================================
        # 6. RESULTADO
        # ==================================================

        return {

            "alumno": {
                "id_alumno":
                    id_alumno,

                "nombre":
                    alumno["nombre"],

                "apellido":
                    alumno["apellido"]
            },

            "estadisticas":
                estadisticas,

            "mis_talleres_mas_reservados":
                talleres_formateados

        }


    finally:

        cursor.close()
        conexion.close()


def obtener_estadisticas_alumno(id_usuario):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # ==================================================
        # 1. OBTENER ALUMNO
        # ==================================================

        cursor.execute("""
            SELECT
                id_alumno,
                nombre,
                apellido
            FROM alumnos
            WHERE id_usuario = %s
        """, (id_usuario,))

        alumno = cursor.fetchone()

        if not alumno:
            return None


        id_alumno = alumno["id_alumno"]


        # ==================================================
        # 2. TALLERES Y CLASES CONTRATADAS VIGENTES
        # ==================================================

        cursor.execute("""
            SELECT
                COUNT(DISTINCT id_taller)
                    AS talleres_vigentes,

                COALESCE(
                    SUM(clases_contratadas),
                    0
                )
                    AS clases_contratadas_vigentes

            FROM inscripciones

            WHERE id_alumno = %s
            AND estado = 'activa'
            AND fecha_inicio <= CURDATE()
            AND fecha_vencimiento >= CURDATE()
        """, (id_alumno,))

        planes = cursor.fetchone()


        # ==================================================
        # 3. RESERVAS
        # ==================================================

        cursor.execute("""
            SELECT

                COUNT(*)
                    AS total_reservas,

                COALESCE(
                    SUM(
                        CASE
                            WHEN r.estado = 'cancelada'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                )
                    AS reservas_canceladas,

                COALESCE(
                    SUM(
                        CASE
                            WHEN r.estado = 'reservada'
                            AND c.estado = 'programada'
                            AND TIMESTAMP(
                                c.fecha,
                                c.hora_inicio
                            ) > NOW()
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                )
                    AS reservas_proximas

            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON i.id_inscripcion = r.id_inscripcion

            INNER JOIN clases c
                ON c.id_clase = r.id_clase

            WHERE i.id_alumno = %s
        """, (id_alumno,))

        reservas = cursor.fetchone()


        # ==================================================
        # 4. ASISTENCIA DEL ALUMNO
        # ==================================================

        cursor.execute("""
            SELECT

                COUNT(*) AS total_asistencias,

                COALESCE(
                    SUM(
                        CASE
                            WHEN a.estado = 'presente'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS presentes,

                COALESCE(
                    SUM(
                        CASE
                            WHEN a.estado = 'ausente'
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS ausentes

            FROM asistencias a

            INNER JOIN reservas_clase r
                ON r.id_reserva = a.id_reserva

            INNER JOIN inscripciones i
                ON i.id_inscripcion = r.id_inscripcion

            WHERE i.id_alumno = %s
        """, (id_alumno,))

        asistencia = cursor.fetchone()


        total_asistencias = int(
            asistencia["total_asistencias"] or 0
        )

        presentes = int(
            asistencia["presentes"] or 0
        )

        ausentes = int(
            asistencia["ausentes"] or 0
        )


        if total_asistencias > 0:

            porcentaje_asistencia = round(
                (presentes / total_asistencias) * 100,
                2
            )

            porcentaje_inasistencia = round(
                (ausentes / total_asistencias) * 100,
                2
            )

        else:

            porcentaje_asistencia = 0
            porcentaje_inasistencia = 0


        # ==================================================
        # 5. TALLERES MÁS RESERVADOS
        # ==================================================

        cursor.execute("""
            SELECT

                t.nombre AS taller,

                COUNT(*) AS reservas

            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON i.id_inscripcion = r.id_inscripcion

            INNER JOIN clases c
                ON c.id_clase = r.id_clase

            INNER JOIN talleres t
                ON t.id_taller = c.id_taller

            WHERE i.id_alumno = %s
            AND r.estado = 'reservada'
            AND c.estado <> 'cancelada'

            GROUP BY
                t.id_taller,
                t.nombre

            ORDER BY
                reservas DESC,
                t.nombre
        """, (id_alumno,))

        talleres = cursor.fetchall()


        # ==================================================
        # 6. NORMALIZAR TALLERES
        # ==================================================

        talleres_formateados = [

            {
                "taller":
                    taller["taller"],

                "reservas":
                    int(
                        taller["reservas"] or 0
                    )
            }

            for taller in talleres

        ]


        # ==================================================
        # 7. RESPUESTA
        # ==================================================

        return {

            "alumno": {

                "id_alumno":
                    id_alumno,

                "nombre":
                    alumno["nombre"],

                "apellido":
                    alumno["apellido"]
            },


            "estadisticas": {

                "talleres_vigentes":
                    int(
                        planes["talleres_vigentes"]
                        or 0
                    ),

                "clases_contratadas_vigentes":
                    int(
                        planes[
                            "clases_contratadas_vigentes"
                        ]
                        or 0
                    ),

                "reservas_proximas":
                    int(
                        reservas["reservas_proximas"]
                        or 0
                    ),

                "total_reservas":
                    int(
                        reservas["total_reservas"]
                        or 0
                    ),

                "reservas_canceladas":
                    int(
                        reservas["reservas_canceladas"]
                        or 0
                    ),

                "asistencias_registradas":
                    total_asistencias,

                "presentes":
                    presentes,

                "ausentes":
                    ausentes,

                "porcentaje_asistencia":
                    porcentaje_asistencia,

                "porcentaje_inasistencia":
                    porcentaje_inasistencia

            },


            "mis_talleres_mas_reservados":
                talleres_formateados

        }


    finally:

        cursor.close()
        conexion.close()

# ------------------------------------------------------------
# PROFESORES
# ------------------------------------------------------------
def obtener_profesor_por_usuario(id_usuario):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_profesor,
                id_usuario,
                nombre,
                apellido,
                rut,
                telefono,
                especialidad,
                foto_perfil
            FROM profesores
            WHERE id_usuario = %s
        """, (id_usuario,))

        profesor = cursor.fetchone()

        return profesor

    finally:

        cursor.close()
        conexion.close()


def actualizar_perfil_profesor(
    id_usuario,
    nombre,
    apellido,
    telefono,
    especialidad
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE profesores
            SET
                nombre = %s,
                apellido = %s,
                telefono = %s,
                especialidad = %s
            WHERE id_usuario = %s
        """, (
            nombre,
            apellido,
            telefono,
            especialidad,
            id_usuario
        ))

        conexion.commit()

        return {
            "nombre": nombre,
            "apellido": apellido,
            "telefono": telefono,
            "especialidad": especialidad
        }

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def actualizar_foto_profesor(
    id_usuario,
    nombre_archivo
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE profesores
            SET foto_perfil = %s
            WHERE id_usuario = %s
        """, (
            nombre_archivo,
            id_usuario
        ))

        conexion.commit()

        return True

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()



# ------------------------------------------------------------
# TALLERES
# ------------------------------------------------------------

def obtener_taller_por_id(id_taller):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_taller,
                nombre,
                descripcion,
                horario,
                cupo_maximo,
                imagen,
                estado
            FROM talleres
            WHERE id_taller = %s
        """, (id_taller,))

        taller = cursor.fetchone() #Se espera obtener solo un taller.S

        return taller

    finally:

        cursor.close()
        conexion.close()



def obtener_talleres():

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_taller,
                nombre,
                descripcion,
                horario,
                cupo_maximo,
                imagen,
                estado
            FROM talleres
            ORDER BY nombre
        """)

        talleres = cursor.fetchall()

        return talleres

    finally:

        cursor.close()
        conexion.close()


def crear_taller(nombre, descripcion, horario, cupo_maximo, imagen):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            INSERT INTO talleres (
                nombre,
                descripcion,
                horario,
                cupo_maximo,
                imagen,
                estado
            )
            VALUES (%s, %s, %s, %s, %s, 'activo')
        """, (
            nombre,
            descripcion,
            horario,
            cupo_maximo,
            imagen
        ))

        conexion.commit()

        id_taller = cursor.lastrowid

        return {
            "id_taller": id_taller,
            "nombre": nombre,
            "descripcion": descripcion,
            "horario": horario,
            "cupo_maximo": cupo_maximo,
            "imagen": imagen,
            "estado": "activo"
        }

    except:

        conexion.rollback() #Si MySQL falla, el servicio deshace la operación y luego vuelve a lanzar el error.
        raise

    finally:

        cursor.close()
        conexion.close()


def actualizar_taller(
    id_taller,
    nombre,
    descripcion,
    horario,
    cupo_maximo,
    imagen
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE talleres
            SET
                nombre = %s,
                descripcion = %s,
                horario = %s,
                cupo_maximo = %s,
                imagen = %s
            WHERE id_taller = %s
        """, (
            nombre,
            descripcion,
            horario,
            cupo_maximo,
            imagen,
            id_taller
        ))

        conexion.commit()

        return {
            "id_taller": id_taller,
            "nombre": nombre,
            "descripcion": descripcion,
            "horario": horario,
            "cupo_maximo": cupo_maximo,
            "imagen": imagen
        }

    except:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def eliminar_taller(id_taller):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            DELETE FROM talleres
            WHERE id_taller = %s
        """, (id_taller,))

        conexion.commit()

        return True

    except:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def obtener_talleres_profesor(id_profesor):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre,
                t.descripcion,
                t.horario,
                t.cupo_maximo,
                t.imagen,
                t.estado
            FROM talleres t

            INNER JOIN taller_profesor tp
                ON t.id_taller = tp.id_taller

            WHERE tp.id_profesor = %s

            ORDER BY t.nombre
        """, (id_profesor,))

        talleres = cursor.fetchall()

        return talleres

    finally:

        cursor.close()
        conexion.close()


def profesor_tiene_taller(id_profesor, id_taller):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            SELECT 1
            FROM taller_profesor
            WHERE id_profesor = %s
            AND id_taller = %s
        """, (
            id_profesor,
            id_taller
        ))

        taller_asignado = cursor.fetchone()

        return taller_asignado is not None

    finally:

        cursor.close()
        conexion.close()

#PERMITE MOSTRAR LOS TALLERES EN TALLERES_DISPONIBLED.HTML <-- RUTA FINAL 
def obtener_talleres_activos():

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre,
                t.descripcion,
                t.horario,
                t.cupo_maximo,
                t.imagen,

                GROUP_CONCAT(
                    CONCAT(
                        p.nombre,
                        ' ',
                        p.apellido
                    )
                    SEPARATOR ', '
                ) AS profesor

            FROM talleres t

            LEFT JOIN taller_profesor tp
                ON t.id_taller = tp.id_taller

            LEFT JOIN profesores p
                ON tp.id_profesor = p.id_profesor

            WHERE t.estado = 'activo'

            GROUP BY
                t.id_taller,
                t.nombre,
                t.descripcion,
                t.horario,
                t.cupo_maximo,
                t.imagen

            ORDER BY t.nombre
        """)

        return cursor.fetchall()

    finally:

        cursor.close()
        conexion.close()


def obtener_taller_activo_por_id(id_taller):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_taller,
                nombre,
                descripcion,
                horario,
                cupo_maximo
            FROM talleres
            WHERE id_taller = %s
            AND estado = 'activo'
        """, (id_taller,))

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()
# ------------------------------------------------------------
# CLASES
# ------------------------------------------------------------
def obtener_clases_profesor(id_profesor):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                c.id_clase,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.cupo_maximo,
                c.estado,
                t.id_taller,
                t.nombre AS taller,

                (
                    SELECT COUNT(*)
                    FROM reservas_clase r
                    WHERE r.id_clase = c.id_clase
                    AND r.estado = 'reservada'
                ) AS reservados

            FROM clases c

            INNER JOIN talleres t
                ON c.id_taller = t.id_taller

            WHERE EXISTS (
                SELECT 1
                FROM taller_profesor tp
                WHERE tp.id_taller = t.id_taller
                AND tp.id_profesor = %s
            )

            ORDER BY
                CASE
                    WHEN c.fecha = CURDATE() THEN 0
                    WHEN c.fecha > CURDATE() THEN 1
                    ELSE 2
                END,

                CASE
                    WHEN c.fecha >= CURDATE()
                    THEN c.fecha
                END ASC,

                CASE
                    WHEN c.fecha < CURDATE()
                    THEN c.fecha
                END DESC,

                c.hora_inicio ASC

        """, (id_profesor,))

        clases = cursor.fetchall()

        # --------------------------------------------------
        # CONVERTIR DATOS MYSQL PARA JSON
        # --------------------------------------------------

        for clase in clases:

            # Fecha
            if clase["fecha"] is not None:
                clase["fecha"] = str(clase["fecha"])

            # Hora de inicio
            if clase["hora_inicio"] is not None:
                clase["hora_inicio"] = str(
                    clase["hora_inicio"]
                )

            # Hora de término
            if clase["hora_fin"] is not None:
                clase["hora_fin"] = str(
                    clase["hora_fin"]
                )

        return clases

    finally:

        cursor.close()
        conexion.close()




def crear_clase(
    id_taller,
    fecha,
    hora_inicio,
    hora_fin,
    cupo_maximo
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            INSERT INTO clases (
                id_taller,
                fecha,
                hora_inicio,
                hora_fin,
                cupo_maximo,
                estado
            )
            VALUES (%s, %s, %s, %s, %s, 'programada')
        """, (
            id_taller,
            fecha,
            hora_inicio,
            hora_fin,
            cupo_maximo
        ))

        conexion.commit()

        id_clase = cursor.lastrowid

        return {
            "id_clase": id_clase,
            "id_taller": id_taller,
            "fecha": fecha,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "cupo_maximo": cupo_maximo,
            "estado": "programada"
        }

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()

def actualizar_clase(
    id_clase,
    fecha,
    hora_inicio,
    hora_fin,
    cupo_maximo
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE clases
            SET
                fecha = %s,
                hora_inicio = %s,
                hora_fin = %s,
                cupo_maximo = %s
            WHERE id_clase = %s
        """, (
            fecha,
            hora_inicio,
            hora_fin,
            cupo_maximo,
            id_clase
        ))

        conexion.commit()

        return {
            "id_clase": id_clase,
            "fecha": fecha,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "cupo_maximo": cupo_maximo
        }

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def cancelar_clase(id_clase):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE clases
            SET estado = 'cancelada'
            WHERE id_clase = %s
        """, (id_clase,))

        cursor.execute("""
            UPDATE reservas_clase
            SET
                estado = 'cancelada',
                fecha_cancelacion = NOW()
            WHERE id_clase = %s
            AND estado = 'reservada'
        """, (id_clase,))

        reservas_canceladas = cursor.rowcount

        conexion.commit()

        return {
            "id_clase": id_clase,
            "estado": "cancelada",
            "reservas_canceladas": reservas_canceladas
        }

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def eliminar_clase(id_clase):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            DELETE FROM clases
            WHERE id_clase = %s
        """, (id_clase,))

        conexion.commit()

        return True

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()

def obtener_clase_disponible_taller(
    id_clase,
    id_taller
):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_clase,
                id_taller,
                fecha,
                hora_inicio,
                cupo_maximo,
                estado

            FROM clases

            WHERE id_clase = %s
            AND id_taller = %s
            AND estado = 'programada'
            AND TIMESTAMP(
                fecha,
                hora_inicio
            ) > NOW()
        """, (
            id_clase,
            id_taller
        ))

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()


# ------------------------------------------------------------
# RESERVAS
# ------------------------------------------------------------
def obtener_reserva_previa_clase(
    id_usuario,
    id_clase
):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.estado

            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON r.id_inscripcion = i.id_inscripcion

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            WHERE a.id_usuario = %s
            AND r.id_clase = %s
            AND r.estado IN (
                'reservada',
                'cancelada'
            )

            ORDER BY r.id_reserva DESC

            LIMIT 1
        """, (
            id_usuario,
            id_clase
        ))

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()

def contar_reservas_activas_clase(id_clase):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                COUNT(*) AS total

            FROM reservas_clase

            WHERE id_clase = %s
            AND estado = 'reservada'
        """, (
            id_clase,
        ))

        resultado = cursor.fetchone()

        return resultado["total"]

    finally:

        cursor.close()
        conexion.close()

def crear_reserva_clase(
    id_inscripcion,
    id_clase
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            INSERT INTO reservas_clase (
                id_inscripcion,
                id_clase,
                estado,
                consume_clase
            )
            VALUES (
                %s,
                %s,
                'reservada',
                1
            )
        """, (
            id_inscripcion,
            id_clase
        ))

        conexion.commit()

        return cursor.lastrowid

    except:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def obtener_reserva_alumno(
    id_reserva,
    id_usuario
):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.id_inscripcion,
                r.id_clase,
                r.estado,
                i.id_taller

            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON r.id_inscripcion = i.id_inscripcion

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            WHERE r.id_reserva = %s
            AND a.id_usuario = %s
        """, (
            id_reserva,
            id_usuario
        ))

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()


def cancelar_reserva_alumno(id_reserva):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            UPDATE reservas_clase r

            INNER JOIN clases c
                ON c.id_clase = r.id_clase

            SET
                r.estado = 'cancelada',
                r.fecha_cancelacion = NOW(),

                r.consume_clase = CASE

                    WHEN TIMESTAMP(
                        c.fecha,
                        c.hora_inicio
                    ) >= DATE_ADD(
                        NOW(),
                        INTERVAL 2 HOUR
                    )

                    THEN 0

                    ELSE 1

                END

            WHERE r.id_reserva = %s
            AND r.estado = 'reservada'
        """, (
            id_reserva,
        ))

        conexion.commit()

        return cursor.rowcount > 0

    except:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def obtener_clases_inscripcion_alumno(
    id_inscripcion,
    id_usuario
):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # ==================================================
        # 1. VALIDAR INSCRIPCIÓN DEL ALUMNO
        # ==================================================

        cursor.execute("""
            SELECT
                i.id_inscripcion,
                i.id_taller,
                i.estado,
                i.clases_contratadas,
                t.nombre AS taller

            FROM inscripciones i

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            INNER JOIN talleres t
                ON i.id_taller = t.id_taller

            WHERE i.id_inscripcion = %s
            AND a.id_usuario = %s
            AND i.estado = 'activa'
        """, (
            id_inscripcion,
            id_usuario
        ))

        inscripcion = cursor.fetchone()

        if not inscripcion:
            return None


        id_taller = inscripcion["id_taller"]


        # ==================================================
        # 2. CONTAR CLASES UTILIZADAS
        # ==================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS usadas
            FROM reservas_clase
            WHERE id_inscripcion = %s
            AND consume_clase = 1
        """, (
            id_inscripcion,
        ))

        resultado = cursor.fetchone()

        clases_usadas = int(
            resultado["usadas"] or 0
        )


        # ==================================================
        # 3. CALCULAR CLASES DISPONIBLES
        # ==================================================

        clases_contratadas = int(
            inscripcion["clases_contratadas"] or 0
        )

        clases_disponibles = (
            clases_contratadas - clases_usadas
        )


        # ==================================================
        # 4. OBTENER CLASES FUTURAS DEL TALLER
        # ==================================================

        cursor.execute("""
            SELECT
                c.id_clase,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.cupo_maximo,
                c.estado,

                (
                    SELECT COUNT(*)
                    FROM reservas_clase r
                    WHERE r.id_clase = c.id_clase
                    AND r.estado = 'reservada'
                ) AS reservados,

                (
                    SELECT r2.id_reserva
                    FROM reservas_clase r2
                    WHERE r2.id_clase = c.id_clase
                    AND r2.id_inscripcion = %s
                    AND r2.estado = 'reservada'
                    LIMIT 1
                ) AS mi_reserva

            FROM clases c

            WHERE c.id_taller = %s
            AND c.estado = 'programada'
            AND TIMESTAMP(
                c.fecha,
                c.hora_inicio
            ) > NOW()

            ORDER BY
                c.fecha,
                c.hora_inicio
        """, (
            id_inscripcion,
            id_taller
        ))

        clases = cursor.fetchall()


        # ==================================================
        # 5. DEVOLVER RESULTADO
        # ==================================================

        return {
            "inscripcion": inscripcion,
            "clases": clases,
            "clases_usadas": clases_usadas,
            "clases_disponibles": clases_disponibles
        }


    finally:

        cursor.close()
        conexion.close()
# ============================================================
# ASISTENCIAS
# ============================================================

def obtener_reserva_profesor(id_reserva, id_profesor):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                r.id_reserva,
                r.id_clase,
                r.estado AS estado_reserva

            FROM reservas_clase r

            INNER JOIN clases c
                ON r.id_clase = c.id_clase

            INNER JOIN taller_profesor tp
                ON c.id_taller = tp.id_taller

            WHERE r.id_reserva = %s
            AND tp.id_profesor = %s
        """, (
            id_reserva,
            id_profesor
        ))

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()

def registrar_asistencia_reserva(
    id_reserva,
    id_profesor,
    estado_asistencia
):

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:

        cursor.execute("""
            INSERT INTO asistencias (
                id_reserva,
                id_profesor,
                estado
            )
            VALUES (%s, %s, %s)

            ON DUPLICATE KEY UPDATE
                id_profesor = VALUES(id_profesor),
                estado = VALUES(estado),
                fecha_registro = CURRENT_TIMESTAMP
        """, (
            id_reserva,
            id_profesor,
            estado_asistencia
        ))

        conexion.commit()

        return True

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()



def obtener_plan_taller(id_taller, id_plan):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre AS taller,
                t.horario,
                p.id_plan,
                p.nombre AS plan,
                p.tipo,
                p.cantidad_clases,
                p.precio

            FROM planes p

            INNER JOIN talleres t
                ON p.id_taller = t.id_taller

            WHERE p.id_plan = %s
            AND t.id_taller = %s
        """, (
            id_plan,
            id_taller
        ))

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()


# ============================================================
# ALUMNOS POR CLASE
# ============================================================

def obtener_alumnos_clase(id_clase):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                r.id_reserva,
                a.id_alumno,
                a.nombre,
                a.apellido,
                a.rut,
                r.estado AS estado_reserva,
                r.fecha_reserva,
                r.fecha_cancelacion,
                asi.estado AS asistencia

            FROM reservas_clase r

            INNER JOIN inscripciones i
                ON r.id_inscripcion = i.id_inscripcion

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            LEFT JOIN asistencias asi
                ON asi.id_reserva = r.id_reserva

            WHERE r.id_clase = %s

            ORDER BY
                a.apellido,
                a.nombre
        """, (id_clase,))

        return cursor.fetchall()

    finally:

        cursor.close()
        conexion.close()

# ============================================================
# PLANES
# ============================================================

def obtener_planes_taller(id_taller):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id_plan,
                nombre,
                tipo,
                cantidad_clases,
                precio
            FROM planes
            WHERE id_taller = %s
            ORDER BY cantidad_clases
        """, (id_taller,))

        return cursor.fetchall()

    finally:

        cursor.close()
        conexion.close()


# ============================================================
# INSCRIPCIONES / TALLERES DEL ALUMNO
# ============================================================

def obtener_talleres_activos_alumno(id_usuario):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre AS taller,
                t.horario,

                COUNT(i.id_inscripcion) AS total_inscripciones,

                SUM(i.clases_contratadas) AS clases_contratadas,

                SUM(i.precio_acordado) AS total_pagado,

                MIN(i.fecha_inicio) AS fecha_inicio,

                MAX(i.fecha_vencimiento) AS fecha_vencimiento

            FROM inscripciones i

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            INNER JOIN talleres t
                ON i.id_taller = t.id_taller

            WHERE a.id_usuario = %s
            AND i.estado = 'activa'

            GROUP BY
                t.id_taller,
                t.nombre,
                t.horario

            ORDER BY t.nombre
        """, (
            id_usuario,
        ))

        return cursor.fetchall()

    finally:

        cursor.close()
        conexion.close()


def obtener_resumen_taller_alumno(id_usuario, id_taller):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                t.id_taller,
                t.nombre AS taller,
                t.horario,

                SUM(i.clases_contratadas) AS clases_contratadas,

                (
                    SELECT COUNT(*)
                    FROM reservas_clase r

                    INNER JOIN inscripciones i2
                        ON r.id_inscripcion = i2.id_inscripcion

                    INNER JOIN alumnos a2
                        ON i2.id_alumno = a2.id_alumno

                    WHERE a2.id_usuario = %s
                    AND i2.id_taller = t.id_taller
                    AND i2.estado = 'activa'
                    AND r.consume_clase = 1
                ) AS clases_usadas

            FROM talleres t

            INNER JOIN inscripciones i
                ON t.id_taller = i.id_taller

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            WHERE a.id_usuario = %s
            AND t.id_taller = %s
            AND i.estado = 'activa'

            GROUP BY
                t.id_taller,
                t.nombre,
                t.horario
        """, (
            id_usuario,
            id_usuario,
            id_taller
        ))

        resumen = cursor.fetchone()

        if resumen:

            resumen["clases_contratadas"] = (
                resumen["clases_contratadas"] or 0
            )

            resumen["clases_usadas"] = (
                resumen["clases_usadas"] or 0
            )

            resumen["clases_disponibles"] = max(
                0,
                resumen["clases_contratadas"]
                - resumen["clases_usadas"]
            )

        return resumen

    finally:

        cursor.close()
        conexion.close()


def obtener_clases_disponibles_taller_alumno(
    id_usuario,
    id_taller
):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                c.id_clase,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.cupo_maximo,
                c.estado,

                (
                    SELECT COUNT(*)
                    FROM reservas_clase r
                    WHERE r.id_clase = c.id_clase
                    AND r.estado = 'reservada'
                ) AS reservados,

                (
                    SELECT r2.id_reserva
                    FROM reservas_clase r2

                    INNER JOIN inscripciones i2
                        ON r2.id_inscripcion = i2.id_inscripcion

                    INNER JOIN alumnos a2
                        ON i2.id_alumno = a2.id_alumno

                    WHERE r2.id_clase = c.id_clase
                    AND a2.id_usuario = %s
                    AND i2.id_taller = %s
                    AND r2.estado = 'reservada'

                    LIMIT 1
                ) AS mi_reserva,

                (
                    SELECT COUNT(*)
                    FROM reservas_clase r3

                    INNER JOIN inscripciones i3
                        ON r3.id_inscripcion = i3.id_inscripcion

                    INNER JOIN alumnos a3
                        ON i3.id_alumno = a3.id_alumno

                    WHERE r3.id_clase = c.id_clase
                    AND a3.id_usuario = %s
                    AND i3.id_taller = %s
                    AND r3.estado = 'cancelada'
                ) AS reserva_cancelada

            FROM clases c

            WHERE c.id_taller = %s
            AND c.estado = 'programada'
            AND TIMESTAMP(
                c.fecha,
                c.hora_inicio
            ) > NOW()

            ORDER BY
                c.fecha,
                c.hora_inicio
        """, (
            id_usuario,
            id_taller,
            id_usuario,
            id_taller,
            id_taller
        ))

        clases = cursor.fetchall()

        # Convertir fecha y horas a texto
        # para mantener compatibilidad con las plantillas.
        for clase in clases:

            if clase["fecha"] is not None:
                clase["fecha"] = str(
                    clase["fecha"]
                )

            if clase["hora_inicio"] is not None:
                clase["hora_inicio"] = str(
                    clase["hora_inicio"]
                )

            if clase["hora_fin"] is not None:
                clase["hora_fin"] = str(
                    clase["hora_fin"]
                )

        return clases

    finally:

        cursor.close()
        conexion.close()

def obtener_inscripcion_con_saldo(id_usuario, id_taller):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                i.id_inscripcion,
                i.clases_contratadas,

                (
                    SELECT COUNT(*)
                    FROM reservas_clase r
                    WHERE r.id_inscripcion = i.id_inscripcion
                    AND r.consume_clase = 1
                ) AS clases_usadas

            FROM inscripciones i

            INNER JOIN alumnos a
                ON i.id_alumno = a.id_alumno

            WHERE a.id_usuario = %s
            AND i.id_taller = %s
            AND i.estado = 'activa'

            HAVING
                clases_contratadas > clases_usadas

            ORDER BY
                i.fecha_vencimiento ASC,
                i.id_inscripcion ASC

            LIMIT 1
        """, (
            id_usuario,
            id_taller
        ))

        return cursor.fetchone()

    finally:

        cursor.close()
        conexion.close()


def procesar_inscripcion_taller(
    id_usuario,
    id_taller,
    id_plan
):

    conexion = conectar_db()

    cursor = conexion.cursor(
        dictionary=True,
        buffered=True
    )

    try:

        # ==================================================
        # 1. OBTENER ALUMNO
        # ==================================================

        cursor.execute("""
            SELECT
                id_alumno
            FROM alumnos
            WHERE id_usuario = %s
        """, (
            id_usuario,
        ))

        alumno = cursor.fetchone()

        if not alumno:

            return {
                "resultado": "alumno_no_encontrado"
            }


        id_alumno = alumno["id_alumno"]


        # ==================================================
        # 2. OBTENER PLAN
        # ==================================================

        cursor.execute("""
            SELECT
                id_plan,
                id_taller,
                tipo,
                cantidad_clases,
                precio
            FROM planes
            WHERE id_plan = %s
            AND id_taller = %s
        """, (
            id_plan,
            id_taller
        ))

        plan = cursor.fetchone()

        if not plan:

            return {
                "resultado": "plan_no_valido"
            }


        # ==================================================
        # 3. BUSCAR INSCRIPCIÓN DEL MISMO TIPO
        # ==================================================

        cursor.execute("""
            SELECT
                i.id_inscripcion,
                i.clases_contratadas,
                i.precio_acordado

            FROM inscripciones i

            INNER JOIN planes p
                ON i.id_plan = p.id_plan

            WHERE i.id_alumno = %s
            AND i.id_taller = %s
            AND i.estado = 'activa'
            AND p.tipo = %s

            ORDER BY i.id_inscripcion ASC

            LIMIT 1
        """, (
            id_alumno,
            id_taller,
            plan["tipo"]
        ))

        inscripcion_existente = cursor.fetchone()


        # ==================================================
        # 4. MENSUALIDAD YA ACTIVA
        # ==================================================

        if (
            plan["tipo"] == "mensual"
            and inscripcion_existente
        ):

            return {
                "resultado": "mensual_existente"
            }


        # ==================================================
        # 5. ACUMULAR CLASE SUELTA
        # ==================================================

        if (
            plan["tipo"] == "suelta"
            and inscripcion_existente
        ):

            cursor.execute("""
                UPDATE inscripciones

                SET
                    clases_contratadas =
                        clases_contratadas + %s,

                    precio_acordado =
                        precio_acordado + %s,

                    fecha_vencimiento =
                        DATE_ADD(
                            CURDATE(),
                            INTERVAL 1 MONTH
                        )

                WHERE id_inscripcion = %s
            """, (
                plan["cantidad_clases"],
                plan["precio"],
                inscripcion_existente[
                    "id_inscripcion"
                ]
            ))

            conexion.commit()

            return {
                "resultado": "clase_agregada",
                "tipo": plan["tipo"]
            }


        # ==================================================
        # 6. CREAR NUEVA INSCRIPCIÓN
        # ==================================================

        cursor.execute("""
            INSERT INTO inscripciones (
                id_alumno,
                id_taller,
                fecha_inscripcion,
                estado,
                id_plan,
                fecha_inicio,
                fecha_vencimiento,
                clases_contratadas,
                precio_acordado
            )

            VALUES (
                %s,
                %s,
                CURDATE(),
                'activa',
                %s,
                CURDATE(),
                DATE_ADD(
                    CURDATE(),
                    INTERVAL 1 MONTH
                ),
                %s,
                %s
            )
        """, (
            id_alumno,
            id_taller,
            id_plan,
            plan["cantidad_clases"],
            plan["precio"]
        ))

        conexion.commit()


        return {
            "resultado": "inscripcion_creada",
            "tipo": plan["tipo"]
        }


    except Exception:

        conexion.rollback()

        raise


    finally:

        cursor.close()
        conexion.close()



def obtener_clases_taller_api(id_taller):

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        # ==================================================
        # 1. VERIFICAR TALLER
        # ==================================================

        cursor.execute("""
            SELECT
                id_taller,
                nombre
            FROM talleres
            WHERE id_taller = %s
        """, (id_taller,))

        taller = cursor.fetchone()

        if not taller:
            return None


        # ==================================================
        # 2. OBTENER CLASES FUTURAS PROGRAMADAS
        # ==================================================

        cursor.execute("""
            SELECT
                c.id_clase,
                c.fecha,
                c.hora_inicio,
                c.hora_fin,
                c.cupo_maximo,
                c.estado,

                (
                    SELECT COUNT(*)
                    FROM reservas_clase r
                    WHERE r.id_clase = c.id_clase
                    AND r.estado = 'reservada'
                ) AS alumnos_reservados

            FROM clases c

            WHERE c.id_taller = %s
            AND c.estado = 'programada'
            AND TIMESTAMP(
                c.fecha,
                c.hora_inicio
            ) > NOW()

            ORDER BY
                c.fecha,
                c.hora_inicio
        """, (id_taller,))

        clases = cursor.fetchall()


        # ==================================================
        # 3. FORMATEAR PARA JSON
        # ==================================================

        for clase in clases:

            if clase["fecha"] is not None:
                clase["fecha"] = str(
                    clase["fecha"]
                )

            if clase["hora_inicio"] is not None:
                clase["hora_inicio"] = str(
                    clase["hora_inicio"]
                )

            if clase["hora_fin"] is not None:
                clase["hora_fin"] = str(
                    clase["hora_fin"]
                )


        return {
            "taller": {
                "id_taller": taller["id_taller"],
                "nombre": taller["nombre"]
            },

            "total_clases": len(clases),

            "clases": clases
        }


    finally:

        cursor.close()
        conexion.close()



# ============================================================
#   ESTADÍSTICAS
# ============================================================


