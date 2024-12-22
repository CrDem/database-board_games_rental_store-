-- Таблица Клиенты
CREATE TABLE Clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15)
);

-- Таблица Игры
CREATE TABLE Games (
    game_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    genre VARCHAR(100),
    description TEXT,
    rental_price NUMERIC(10, 2) NOT NULL CHECK (rental_price > 0)
);

-- Таблица Аренды
CREATE TABLE Rentals (
    rental_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES Clients(client_id) ON DELETE CASCADE,
    game_id INT NOT NULL REFERENCES Games(game_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    discount NUMERIC(5, 2), -- рассчитывается триггером
    total_price NUMERIC(10, 2), -- рассчитывается триггером
    CHECK (end_date > start_date)
);

-- Таблица Скидки
CREATE TABLE Discounts (
    client_id INT PRIMARY KEY REFERENCES Clients(client_id) ON DELETE CASCADE,
    total_rentals INT DEFAULT 0,
    total_spent NUMERIC(10, 2) DEFAULT 0,
    current_discount NUMERIC(5, 2) DEFAULT 0 CHECK (current_discount >= 0 AND current_discount <= 100)
);

-- Триггер для расчета скидки и итоговой стоимости аренды
CREATE OR REPLACE FUNCTION calculate_rental_values()
RETURNS TRIGGER AS $$
BEGIN
    -- Получение текущей скидки клиента из таблицы Discounts
    SELECT current_discount INTO NEW.discount
    FROM Discounts
    WHERE client_id = NEW.client_id;

    -- Расчет итоговой стоимости аренды с учетом скидки
    NEW.total_price := (SELECT rental_price FROM Games WHERE game_id = NEW.game_id) * 
                        (1 - COALESCE(NEW.discount, 0) / 100);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calculate_rental_values
BEFORE INSERT OR UPDATE ON Rentals
FOR EACH ROW EXECUTE FUNCTION calculate_rental_values();

-- Триггер для обновления данных о скидках в таблице Discounts
CREATE OR REPLACE FUNCTION update_discount()
RETURNS TRIGGER AS $$
BEGIN
    -- Обновление общего количества аренд и суммы затрат
    UPDATE Discounts
    SET total_rentals = total_rentals + 1,
        total_spent = total_spent + NEW.total_price
    WHERE client_id = NEW.client_id;

    -- Пересчет текущей скидки в зависимости от суммы затрат или количества аренд
    UPDATE Discounts
    SET current_discount = CASE
        WHEN total_rentals >= 10 THEN 20
        WHEN total_rentals >= 5 THEN 10
        WHEN total_spent >= 100 THEN 5
        ELSE 0
    END
    WHERE client_id = NEW.client_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_discount
AFTER INSERT ON Rentals
FOR EACH ROW EXECUTE FUNCTION update_discount();

CREATE OR REPLACE FUNCTION insert_discount_for_new_client()
RETURNS TRIGGER AS $$
BEGIN
    -- Вставка строки в таблицу Discounts для нового клиента
    INSERT INTO Discounts (client_id, total_rentals, total_spent, current_discount)
    VALUES (NEW.client_id, 0, 0, 0);  -- Изначально total_rentals = 0, total_spent = 0, current_discount = 0
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_discount_after_client
AFTER INSERT ON Clients
FOR EACH ROW
EXECUTE FUNCTION insert_discount_for_new_client();

CREATE OR REPLACE FUNCTION delete_client_user(client_email TEXT)
RETURNS VOID AS $$
BEGIN
    -- Удаление прав пользователя на последовательности
    EXECUTE format('REVOKE ALL PRIVILEGES ON SEQUENCE clients_client_id_seq FROM %I;', client_email);
    EXECUTE format('REVOKE ALL PRIVILEGES ON SEQUENCE games_game_id_seq FROM %I;', client_email);
    EXECUTE format('REVOKE ALL PRIVILEGES ON SEQUENCE rentals_rental_id_seq FROM %I;', client_email);

    -- Удаление прав пользователя на таблицы
    EXECUTE format('REVOKE ALL PRIVILEGES ON TABLE clients FROM %I;', client_email);
    EXECUTE format('REVOKE ALL PRIVILEGES ON TABLE games FROM %I;', client_email);
    EXECUTE format('REVOKE ALL PRIVILEGES ON TABLE rentals FROM %I;', client_email);
    EXECUTE format('REVOKE ALL PRIVILEGES ON TABLE discounts FROM %I;', client_email);

    -- Удаление пользователя базы данных
    EXECUTE format('DROP USER IF EXISTS %I;', client_email);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_client_user(client_email TEXT)
RETURNS VOID AS $$
DECLARE
    obj RECORD;
BEGIN
    -- Удаление прав пользователя на все таблицы, исключая некоторые
    FOR obj IN 
        SELECT c.relname
        FROM pg_catalog.pg_class c
        JOIN pg_catalog.pg_roles r ON r.rolname = client_email
        WHERE c.relkind = 'r'  -- только таблицы
        AND c.relname != 'sql_features'  -- исключаем таблицу sql_features
        AND c.relname != 'sql_implementation_info'
        AND c.relname != 'sql_sizing'
        AND has_table_privilege(r.rolname, c.oid, 'SELECT') -- проверка прав на таблицы
    LOOP
        EXECUTE format('REVOKE ALL PRIVILEGES ON TABLE %I FROM %I;', obj.relname, client_email);
    END LOOP;

    -- Удаление прав пользователя на все последовательности
    FOR obj IN 
        SELECT s.relname
        FROM pg_catalog.pg_class s
        JOIN pg_catalog.pg_roles r ON r.rolname = client_email
        WHERE s.relkind = 'S'  -- только последовательности
        AND has_sequence_privilege(r.rolname, s.oid, 'USAGE') -- проверка прав на последовательности
    LOOP
        EXECUTE format('REVOKE ALL PRIVILEGES ON SEQUENCE %I FROM %I;', obj.relname, client_email);
    END LOOP;

    -- Удаление пользователя базы данных
    EXECUTE format('DROP USER IF EXISTS %I;', client_email);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION on_delete_client()
RETURNS TRIGGER AS $$ 
BEGIN 
    PERFORM delete_client_user(OLD.email); 
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_on_delete_client
AFTER DELETE ON Clients
FOR EACH ROW
EXECUTE FUNCTION on_delete_client();

-- Создание индекса по текстовому полю "title" в таблице Games
CREATE INDEX idx_game_title ON Games(title);

GRANT USAGE, CREATE ON SCHEMA public TO PUBLIC