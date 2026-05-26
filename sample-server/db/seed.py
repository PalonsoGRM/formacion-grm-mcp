"""
Crea y puebla grm_demo.db con datos de ejemplo.
Ejecutar una vez antes de arrancar el servidor:

    python db/seed.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "grm_demo.db"


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS pedidos;
        DROP TABLE IF EXISTS clientes;

        CREATE TABLE clientes (
            id       INTEGER PRIMARY KEY,
            nombre   TEXT NOT NULL,
            ciudad   TEXT NOT NULL,
            email    TEXT NOT NULL,
            segmento TEXT NOT NULL CHECK(segmento IN ('A','B','C'))
        );

        CREATE TABLE pedidos (
            id          INTEGER PRIMARY KEY,
            cliente_id  INTEGER NOT NULL REFERENCES clientes(id),
            fecha       TEXT NOT NULL,
            importe     REAL NOT NULL,
            estado      TEXT NOT NULL CHECK(estado IN ('pendiente','enviado','entregado','cancelado'))
        );
    """)

    clientes = [
        (1,  "Transportes Romeu S.L.",    "Valencia",   "romeu@romeu.com",          "A"),
        (2,  "Logística Martínez",         "Madrid",     "martinez@logistica.es",    "A"),
        (3,  "Distribuciones García",      "Barcelona",  "garcia@distrib.es",        "B"),
        (4,  "Almacenes Pérez",            "Sevilla",    "perez@almacenes.es",       "B"),
        (5,  "Cargas Rápidas Norte S.A.",  "Bilbao",     "norte@cargas.es",          "A"),
        (6,  "Mensajería Express Sud",     "Málaga",     "sud@mensajeria.es",        "C"),
        (7,  "Frigoríficos del Ebro",      "Zaragoza",   "ebro@frigorificos.es",     "B"),
        (8,  "Paquetería Levante",         "Alicante",   "levante@paqueteria.es",    "C"),
        (9,  "Grupo Logístico Atlántico",  "A Coruña",   "atlantico@grupolog.es",    "A"),
        (10, "Suministros Centro",         "Toledo",     "centro@suministros.es",    "C"),
    ]

    pedidos = [
        (1,  1,  "2026-01-10", 12400.00, "entregado"),
        (2,  1,  "2026-02-03",  8750.50, "entregado"),
        (3,  1,  "2026-03-18", 15200.00, "enviado"),
        (4,  1,  "2026-04-22",  3100.00, "pendiente"),
        (5,  2,  "2026-01-15",  6200.00, "entregado"),
        (6,  2,  "2026-02-28",  9800.00, "cancelado"),
        (7,  2,  "2026-04-05", 11500.00, "enviado"),
        (8,  3,  "2026-01-20",  4300.00, "entregado"),
        (9,  3,  "2026-03-07",  7650.00, "entregado"),
        (10, 3,  "2026-04-30",  2200.00, "pendiente"),
        (11, 4,  "2026-02-12",  5500.00, "entregado"),
        (12, 4,  "2026-03-25",  3900.00, "cancelado"),
        (13, 5,  "2026-01-08", 22000.00, "entregado"),
        (14, 5,  "2026-02-19", 18400.00, "entregado"),
        (15, 5,  "2026-04-11", 25600.00, "enviado"),
        (16, 6,  "2026-03-02",  1200.00, "entregado"),
        (17, 6,  "2026-04-14",   850.00, "pendiente"),
        (18, 7,  "2026-01-25",  8900.00, "entregado"),
        (19, 7,  "2026-03-30",  6700.00, "enviado"),
        (20, 8,  "2026-02-06",  1450.00, "entregado"),
        (21, 8,  "2026-04-19",   980.00, "pendiente"),
        (22, 9,  "2026-01-30", 14300.00, "entregado"),
        (23, 9,  "2026-03-14", 19200.00, "enviado"),
        (24, 10, "2026-02-22",  2100.00, "entregado"),
        (25, 10, "2026-04-08",  1750.00, "cancelado"),
    ]

    cur.executemany("INSERT INTO clientes VALUES (?,?,?,?,?)", clientes)
    cur.executemany("INSERT INTO pedidos VALUES (?,?,?,?,?)", pedidos)
    conn.commit()
    conn.close()
    print(f"Base de datos creada en {DB_PATH}")
    print(f"  {len(clientes)} clientes  |  {len(pedidos)} pedidos")


if __name__ == "__main__":
    seed()
