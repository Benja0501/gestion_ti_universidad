-- db/init.sql
CREATE TABLE IF NOT EXISTS equipos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    ubicacion VARCHAR(100),
    fecha_compra DATE NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'OPERATIVO'
);
