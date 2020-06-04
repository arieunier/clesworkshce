use public;
create table public.time_travel(
        Id varchar(32) not null primary key,
        CurrentTime varchar(20) not null,
        DestinationTime varchar(20) not null);       