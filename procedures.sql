CREATE OR REPLACE FUNCTION update_row(p_table_name TEXT, p_column_name TEXT, p_new_value TEXT, p_condition TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('UPDATE %I SET %I = %L WHERE %s', p_table_name, p_column_name, p_new_value, p_condition);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_row(p_table_name TEXT, p_condition TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('DELETE FROM %I WHERE %s CASCADE', p_table_name, p_condition);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_client_and_user(
    client_name TEXT,
    client_email TEXT,
    client_phone TEXT,
    client_password TEXT
)
RETURNS VOID AS $$
BEGIN
    -- Добавление клиента в таблицу Clients
    INSERT INTO Clients (name, email, phone)
    VALUES (client_name, client_email, client_phone);

    -- Динамическое создание пользователя базы данных
    EXECUTE format('CREATE USER %I WITH PASSWORD %L', client_email, client_password);

    -- Предоставление минимальных привилегий новому пользователю
    EXECUTE format('GRANT CONNECT ON DATABASE rental_store TO %I', client_email);
    EXECUTE format('GRANT SELECT ON ALL TABLES IN SCHEMA public TO %I', client_email);
    EXECUTE format('GRANT INSERT ON rentals TO %I', client_email);
    EXECUTE format('GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO %I', client_email);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION clear_table(table_name TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('TRUNCATE TABLE %I RESTART IDENTITY CASCADE', table_name);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION clear_all_tables()
RETURNS VOID AS $$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    LOOP
        EXECUTE format('TRUNCATE TABLE %I RESTART IDENTITY CASCADE', tbl.table_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;