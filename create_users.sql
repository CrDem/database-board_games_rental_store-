-- shopkeeper: админ магазина, продавец
CREATE USER shopkeeper WITH PASSWORD 'shopkeeper_password';

GRANT CONNECT ON DATABASE rental_store TO shopkeeper;

GRANT INSERT, DELETE, UPDATE, SELECT, TRUNCATE ON ALL TABLES IN SCHEMA public TO shopkeeper;

DO $$ 
DECLARE
    tbl RECORD;
BEGIN
    -- Цикл по всем таблицам в схеме public
    FOR tbl IN 
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    LOOP
        -- Динамически изменяем владельца каждой таблицы
        EXECUTE format('ALTER TABLE %I OWNER TO shopkeeper', tbl.table_name);
    END LOOP;
END $$;

DO $$ 
DECLARE
    seq RECORD;
BEGIN
    -- Цикл для каждой последовательности в схеме public
    FOR seq IN 
        SELECT sequence_name 
        FROM information_schema.sequences 
        WHERE sequence_schema = 'public'
    LOOP
        -- Динамически изменяем владельца последовательности
        EXECUTE format('ALTER SEQUENCE %I OWNER TO shopkeeper', seq.sequence_name);
    END LOOP;
END $$;


GRANT EXECUTE ON FUNCTION add_client TO shopkeeper;
GRANT EXECUTE ON FUNCTION update_row TO shopkeeper;
GRANT EXECUTE ON FUNCTION delete_row TO shopkeeper;
GRANT EXECUTE ON FUNCTION clear_table TO shopkeeper;
GRANT EXECUTE ON FUNCTION clear_all_tables TO shopkeeper;

GRANT EXECUTE ON FUNCTION add_client_and_user(TEXT, TEXT, TEXT, TEXT) TO shopkeeper;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO shopkeeper;
ALTER USER shopkeeper WITH CREATEROLE;

-- клиенты создаются продавцом
