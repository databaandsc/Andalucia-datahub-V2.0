-- ==========================================
-- CREACIÓN DEL MODELO EN ESTRELLA
-- ==========================================

-- 1. TABLA DE DIMENSIÓN: Territorio
CREATE TABLE territorio (
                            id BIGSERIAL PRIMARY KEY,
                            codigo_territorio VARCHAR (20) UNIQUE NOT NULL,
                            descripcion_territorio VARCHAR (100) NOT NULL
);

-- 2. TABLA DE DIMENSIÓN: Sector Económico
CREATE TABLE sector(
                       id BIGSERIAL PRIMARY KEY,
                       codigo_sector VARCHAR (20) UNIQUE NOT NULL,
                       descripcion_sector VARCHAR (100) NOT NULL
);

-- 3. TABLA DE HECHOS: Registro de Empleo
CREATE TABLE registro_empleos (
                                  id BIGSERIAL PRIMARY KEY,
                                  id_territorio BIGINT NOT NULL REFERENCES territorio(id),
                                  id_sector BIGINT NOT NULL REFERENCES sector(id),
                                  anio INTEGER NOT NULL,
                                  trimestre INTEGER NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
                                  puestos INTEGER NOT NULL,
                                  CONSTRAINT registro_empleos_unicos UNIQUE (id_territorio, id_sector, anio, trimestre)
);

-- 4. ÍNDICES
CREATE INDEX idx_empleos_busqueda ON registro_empleos(id_sector, anio, trimestre);
CREATE INDEX idx_empleos_temporal ON registro_empleos(anio, trimestre);