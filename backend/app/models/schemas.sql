-- define your schemas in from NEON here....
-- this file is not actually being run anywhere in the codebase, but it is a good place to define your schemas
-- for mainly clarity on where the tables are at, for frontend and PM/TL purposes


-- i'm just gonna write down some siggestions here

-- not really the most revelant for MVP0, but build this out just for future purposes
-- for now the only hotel that should be in here is Sally's one (i forgot the name mb)
create table if not exists hotels(
  id serial primary key,
  name text not null,
  timezone text default 'Europe/Dublin'
);


-- each hotel has several different 'room types'
CREATE TABLE room_types(
  id            SERIAL PRIMARY KEY,
  hotel_id      INT REFERENCES hotels(id), -- FK
  code          TEXT NOT NULL,         -- e.g., "DLX-QUEEN"
  name          TEXT NOT NULL,         -- "Deluxe Queen"
  capacity      INT,                   -- optional, for features later
  UNIQUE(hotel_id, code) -- composite unique index
);


-- daily summary of what the hotel's state is
-- normalized daily hotel-wide & room-type specific facts
CREATE TABLE inventory_daily(
  date          DATE,
  hotel_id      INT REFERENCES hotels(id),
  room_type_id  INT REFERENCES room_types(id),
  rooms_total   INT,
  rooms_out     INT DEFAULT 0,
  PRIMARY KEY(date, hotel_id, room_type_id)
);


CREATE TABLE bookings_daily(
  date          DATE,
  hotel_id      INT REFERENCES hotels(id),
  room_type_id  INT REFERENCES room_types(id),
  rooms_sold    INT,
  adr           NUMERIC,               -- average daily rate realized
  pickup_24h    INT,                   -- bookings added in last 24h (pace)
  PRIMARY KEY(date, hotel_id, room_type_id)
);


-- should be able to get this from guestLine BMS API
CREATE TABLE rates_daily(
  date          DATE,
  hotel_id      INT REFERENCES hotels(id),
  room_type_id  INT REFERENCES room_types(id),
  published_rate NUMERIC,              -- current live price
  PRIMARY KEY(date, hotel_id, room_type_id)
);


-- events & impact score (based on the Impact Score doc -> a single numeric column)
CREATE TABLE events_daily(
  date          DATE,
  hotel_id      INT REFERENCES hotels(id),
  impact_score  NUMERIC,               -- from ml/features/event_impact.py
  source_json   JSONB,                 -- optional: details per source
  PRIMARY KEY(date, hotel_id)
);


CREATE TABLE predictions(
  created_at    TIMESTAMPTZ DEFAULT now(),
  date          DATE,
  hotel_id      INT,
  room_type_id  INT,
  price_rec     NUMERIC,
  price_min     NUMERIC,
  price_max     NUMERIC,
  drivers       JSONB,                 -- top 3 drivers (strings) -> displayed on the frontend nicely for the RMs
  input_json    JSONB                  -- features row logged for audit
  -- OPTIONAL llm summary: what we were talking about last track session? 
);


