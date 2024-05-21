create table Airline
(
    Airline_Name   varchar(255) not null
        primary key,
    Aircraft_Count int          null
);

create table Airplane_Model
(
    IATA_Code      char(3)      null,
    Model_ID       varchar(255) not null
        primary key,
    seats_qty      int          null,
    crew_seats_qty int          null
);

create table Aircraft
(
    Aircraft_ID       varchar(255) not null
        primary key,
    Airline_Name      varchar(255) null,
    Model_ID          varchar(255) null,
    Manufactured_Date date         null,
    constraint Aircraft_ibfk_1
        foreign key (Airline_Name) references Airline (Airline_Name),
    constraint Aircraft_ibfk_2
        foreign key (Model_ID) references Airplane_Model (Model_ID)
);

create index Airline_Name
    on Aircraft (Airline_Name);

create index Model_ID
    on Aircraft (Model_ID);

create table Airport
(
    Airport_Code char(3)   not null
        primary key,
    Airport_Name char(255) null,
    Country      char(3)   null,
    Runway_Count int       null,
    Timezone     char(3)   null
);

create table Flight
(
    Flight_ID           varchar(255) not null
        primary key,
    Flight_Status       char(10)     null,
    Aircraft_ID         varchar(255) null,
    Destination_airport char(3)      null,
    Departure_airport   char(3)      null,
    Departure_Time      datetime     null,
    Arrival_Time        datetime     null,
    constraint Flight_ibfk_1
        foreign key (Aircraft_ID) references Aircraft (Aircraft_ID),
    constraint Flight_ibfk_2
        foreign key (Destination_airport) references Airport (Airport_Code),
    constraint Flight_ibfk_3
        foreign key (Departure_airport) references Airport (Airport_Code)
);

create index Aircraft_ID
    on Flight (Aircraft_ID);

create index Departure_airport
    on Flight (Departure_airport);

create index Destination_airport
    on Flight (Destination_airport);

create table People
(
    First_Name  varchar(255) null,
    Last_Name   varchar(255) null,
    DOB         date         null,
    Citizenship char(3)      not null,
    Passport_No varchar(255) not null,
    primary key (Passport_No, Citizenship)
);

create table Staff
(
    Passport_No  varchar(255) not null,
    Citizenship  char(3)      not null,
    Staff_ID     int          null,
    Airline_Name varchar(255) null,
    primary key (Passport_No, Citizenship),
    constraint Staff_ibfk_1
        foreign key (Passport_No, Citizenship) references People (Passport_No, Citizenship),
    constraint Staff_ibfk_2
        foreign key (Airline_Name) references Airline (Airline_Name)
);

create index Airline_Name
    on Staff (Airline_Name);

create table Ticket
(
    Passport_No varchar(255) not null,
    Citizenship char(3)      not null,
    Seat_No     varchar(255) not null,
    Flight_ID   varchar(255) not null,
    primary key (Passport_No, Citizenship, Seat_No, Flight_ID),
    constraint Ticket_ibfk_1
        foreign key (Passport_No, Citizenship) references People (Passport_No, Citizenship),
    constraint Ticket_ibfk_2
        foreign key (Flight_ID) references Flight (Flight_ID)
);

create index Flight_ID
    on Ticket (Flight_ID);