INSERT INTO Clients (name, email, phone)
VALUES
('Антон Иванов', 'anton.ivanov@example.com', '89031234567'),
('Мария Петрова', 'maria.petrova@example.com', '89039876543'),
('Олег Смирнов', 'oleg.smirnov@example.com', '89035554433'),
('Екатерина Соколова', 'ekaterina.sokolova@example.com', '89037778899'),
('Дмитрий Кузнецов', 'dmitry.kuznetsov@example.com', '89034445566');

INSERT INTO Games (title, genre, description, rental_price)
VALUES
('Мафия', 'Психологическая', 'Классическая психологическая игра', 300.00),
('Монополия', 'Экономическая', 'Игра о торговле и недвижимости', 500.00),
('Уно', 'Карточная', 'Весёлая игра для всей семьи', 150.00),
('Дженга', 'На ловкость', 'Строим башню и не даём ей упасть', 200.00),
('Имаджинариум', 'Творческая', 'Игра на воображение и ассоциации', 400.00),
('Каркассон', 'Стратегическая', 'Создайте свой средневековый город', 350.00);

INSERT INTO Discounts (client_id, total_rentals, total_spent, current_discount)
VALUES
(1, 3, 1050.00, 5), -- Антон Иванов
(2, 2, 800.00, 5),  -- Мария Петрова
(3, 5, 1750.00, 10), -- Олег Смирнов
(4, 7, 2800.00, 15), -- Екатерина Соколова
(5, 1, 500.00, 0);  -- Дмитрий Кузнецов

INSERT INTO Rentals (client_id, game_id, start_date, end_date)
VALUES
(1, 1, '2024-01-01', '2024-01-03'), -- Антон берет "Мафию"
(1, 2, '2024-01-05', '2024-01-07'), -- Антон берет "Монополию"
(2, 3, '2024-01-10', '2024-01-12'), -- Мария берет "Уно"
(3, 4, '2024-01-15', '2024-01-17'), -- Олег берет "Дженгу"
(3, 5, '2024-01-20', '2024-01-22'), -- Олег берет "Имаджинариум"
(4, 6, '2024-01-25', '2024-01-28'), -- Екатерина берет "Каркассон"
(5, 2, '2024-01-29', '2024-02-01'); -- Дмитрий берет "Монополию"