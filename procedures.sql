CREATE OR REPLACE FUNCTION update_row(p_table_name TEXT, p_column_name TEXT, p_new_value TEXT, p_condition TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('UPDATE %I SET %I = %L WHERE %s', p_table_name, p_column_name, p_new_value, p_condition);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_row(p_table_name TEXT, p_condition TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('DELETE FROM %I WHERE %s', p_table_name, p_condition);
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
    EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO %I', client_email);
    EXECUTE format('GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO %I', client_email);
    EXECUTE format('GRANT USAGE, CREATE ON SCHEMA public TO %I', client_email);
    
    -- Создание таблицы rental_history_<email> и копирование данных
    PERFORM create_rental_history_table(client_email);
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

CREATE OR REPLACE FUNCTION create_rental_history_table(user_email TEXT)
RETURNS VOID AS $$
DECLARE
table_name TEXT;
BEGIN
-- Создание имени таблицы, используя email пользователя
table_name := 'rental_history_' || user_email;

-- Динамическое создание таблицы
EXECUTE format('
CREATE TABLE %I (
rental_id SERIAL PRIMARY KEY,
client_id INT NOT NULL,
game_id INT NOT NULL,
start_date DATE NOT NULL,
end_date DATE NOT NULL,
discount NUMERIC(5, 2),
total_price NUMERIC(10, 2)
)', table_name);

-- Предоставление прав пользователю на созданную таблицу
EXECUTE format('
GRANT ALL PRIVILEGES ON TABLE %I TO %I', table_name, user_email);

-- Копирование данных из таблицы rentals в новую таблицу
EXECUTE format('
INSERT INTO %I (rental_id, client_id, game_id, start_date, end_date, discount, total_price)
SELECT rental_id, client_id, game_id, start_date, end_date, discount, total_price
FROM rentals
WHERE client_id = (SELECT client_id FROM clients WHERE email = %L)', table_name, user_email);

END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_rental_history()
RETURNS TRIGGER AS $$
DECLARE
table_name TEXT;
BEGIN
-- Создание имени таблицы для истории аренды, используя email клиента
SELECT 'rental_history_' || email INTO table_name
FROM clients
WHERE client_id = NEW.client_id;

RAISE NOTICE 'Имя таблицы: %', table_name;

-- Вставка данных в таблицу истории аренды
    EXECUTE format('
    INSERT INTO %I (rental_id, client_id, game_id, start_date, end_date, discount, total_price)
    VALUES (%L, %L, %L, %L, %L, %L, %L)', 
    table_name, NEW.rental_id, NEW.client_id, NEW.game_id, NEW.start_date, NEW.end_date, NEW.discount, NEW.total_price);

RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_rental_history
AFTER INSERT ON rentals
FOR EACH ROW
EXECUTE FUNCTION update_rental_history();

CREATE OR REPLACE FUNCTION delete_rental_history_table()
RETURNS TRIGGER AS $$
DECLARE
table_name TEXT;
BEGIN
-- Создание имени таблицы, используя email клиента
table_name := 'rental_history_' || OLD.email;

-- Динамическое удаление таблицы клиента
EXECUTE format('DROP TABLE IF EXISTS %I', table_name);

RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_delete_rental_history
AFTER DELETE ON Clients
FOR EACH ROW EXECUTE FUNCTION delete_rental_history_table();