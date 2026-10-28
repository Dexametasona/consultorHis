import os
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# Carpeta donde se guardará la base de datos
FOLDER_ROUTE = Path(os.environ['LOCALAPPDATA'])/'Consultor-His'
FOLDER_ROUTE.mkdir(parents=True, exist_ok=True)

DB_ROUTE = FOLDER_ROUTE / "consultor.db"

@contextmanager
def getConnection():
    connect = sqlite3.connect(DB_ROUTE)
    connect.execute("PRAGMA foreign_keys = ON")
    try:
        with connect:
            yield connect
    finally:
        connect.close()
    return connect


def createTable():
    with getConnection() as connect:
        connect.execute("""
            CREATE TABLE IF NOT EXISTS query (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                file_origin TEXT NOT NULL,
                DNIamount INTEGER NOT NULL DEFAULT 0,
                successAmount INTEGER NOT NULL DEFAULT 0,
                errorAmount INTEGER NOT NULL DEFAULT 0
            )
        """)

        connect.execute("""
            CREATE TABLE IF NOT EXISTS patient (
                dni TEXT PRIMARY KEY,
                patient TEXT,
                birthdate TEXT
            )
        """)

        connect.execute("""
            CREATE TABLE IF NOT EXISTS vaccines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER NOT NULL,
                dni TEXT NOT NULL,
                cpms TEXT NOT NULL,
                lab TEXT,
                date TEXT,
                FOREIGN KEY (query_id)
                    REFERENCES query(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (dni)
                    REFERENCES patient(dni)
            )
        """)
        
        connect.execute("""
            CREATE TABLE IF NOT EXISTS query_patients (
                query_id INTEGER NOT NULL,
                dni TEXT NOT NULL,
                PRIMARY KEY (query_id, dni),
                FOREIGN KEY (query_id) 
                    REFERENCES query(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (dni) REFERENCES patient(dni)
            )
        """)
    
def createQuery(originFile, DNIamount ):
    beginDate = datetime.now().isoformat(timespec="seconds")

    with getConnection() as connection:
        cursor = connection.execute("""
            INSERT INTO query (
                date,
                file_origin,
                DNIamount
            )
            VALUES (?, ?, ?)
        """, (
            beginDate,
            str(originFile),
            DNIamount
        ))

        return cursor.lastrowid
    
def save_patient(dni, patient, birthdate):
    with getConnection() as connection:
        connection.execute("""
            INSERT INTO patient (
                dni,
                patient,
                birthdate
            )
            VALUES (?, ?, ?)
            ON CONFLICT(dni) DO UPDATE SET
                patient = excluded.patient,
                birthdate = excluded.birthdate
        """, (
            dni,
            patient,
            birthdate
        ))
        
def save_vaccine(query_id, dni, vaccines):
    if not vaccines:
        return

    logs = [
        (
            query_id,
            dni,
            vaccine["cpms"],
            vaccine.get("lab"),
            vaccine.get("date")
        )
        for vaccine in vaccines
    ]

    with getConnection() as connection:
        connection.executemany("""
            INSERT INTO vaccines (
                query_id,
                dni,
                cpms,
                lab,
                date
            )
            VALUES (?, ?, ?, ?, ?)
        """, logs)
        
def updateQuery(query_id, successAmount, errorsAmount):

    with getConnection() as connection:
        connection.execute("""
            UPDATE query
            SET successAmount = ?,
                errorAmount = ?
            WHERE id = ?
        """, (
            successAmount,
            errorsAmount,
            query_id
        ))

def getQueryList():
    with getConnection() as connection:
        cursor = connection.execute("""
            SELECT
                id,
                date,
                file_origin,
                DNIamount,
                successAmount,
                errorAmount
            FROM query
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def search_vaccines(query_id, cpms):
    cpms = cpms.strip()

    if not cpms:
        return []

    with getConnection() as connection:
        cursor = connection.execute("""
            SELECT
                v.dni,
                p.patient,
                p.birthdate,
                v.cpms,
                v.lab,
                v.date
            FROM vaccines AS v
            LEFT JOIN patient AS p
                ON p.dni = v.dni
            WHERE v.query_id = ?
              AND v.cpms LIKE ?
            ORDER BY v.dni
        """, (query_id, f"%{cpms}%"))

        return cursor.fetchall()

def delete_query(queryId):
    with getConnection() as connect:
        connect.execute(
            "DELETE FROM vaccines WHERE query_id = ?",
            (queryId,)
        )

        cursor = connect.execute(
            "DELETE FROM query WHERE id = ?",
            (queryId,)
        )

        return cursor.rowcount > 0
    

def save_patientByQuery(queryId, dni):
    with getConnection() as connection:
        connection.execute("""
            INSERT OR IGNORE INTO query_patients (
                query_id, dni
            )
            VALUES (?, ?)
        """, (queryId, dni))


def getPatientsAndVaccinesByQuery(queryId, cpms):
    if not cpms:
        return []
    
    placeholders = ", ".join("?" for _ in cpms)
    
    with getConnection() as connection:
        cursor = connection.execute(f"""
            SELECT
                p.dni,
                p.patient,
                p.birthdate,
                v.cpms,
                v.lab,
                v.date
            FROM query_patients q
            JOIN patient p
                ON p.dni = q.dni
            LEFT JOIN vaccines v
                ON v.query_id = q.query_id
                AND v.dni = q.dni
                AND v.cpms IN({placeholders})
            WHERE q.query_id = ?
            ORDER BY p.patient
        """, (*cpms, queryId))

        return cursor.fetchall()
