-- Añadir restricción de unicidad a la tabla sector
ALTER TABLE sector
    ADD CONSTRAINT unq_descripcion_sector UNIQUE (descripcion_sector);

-- Añadir restricción de unicidad a la tabla territorio
ALTER TABLE territorio
    ADD CONSTRAINT unq_descripcion_territorio UNIQUE (descripcion_territorio);