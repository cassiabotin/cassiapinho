create table cliente(
	id_cliente int primary key auto_increment,
    cpf varchar(15) not null,
    nome varchar (40) not null,
    telefone int not null,
    email varchar (30) not null,
    endereco varchar (50)
);
create table funcionarios(
    id_funcionario int primary key auto_increment,
    nome varchar (40) not null,
    email varchar (30) not null,
	endereco varchar (50) not null,
    telefone int not null
);

alter table funcionarios
add column 
cargo varchar(20);

create table processos(
    n_processo int primary key unique,
    data date not null,
    status varchar (18) not null,
    nome varchar(40) not null
);
create table audiencias (
    id_audiencia int primary key,
    id_cliente int not null,
    id_funcionario int not null,
    n_processo int not null unique,
    foreign key(id_cliente) references cliente(id_cliente),
    foreign key(id_funcionario) references funcionarios(id_funcionario),
    foreign key(n_processo) references processos(n_processo)
);
create table pagamentos (
    id_pagamento int primary key auto_increment,
    data_vencimento date not null,
    data_pagamento date not null,
    valor_total float not null,
    parcelamentos varchar(28) not null,
    id_cliente int not null,
    id_audiencia int, 
    foreign key(id_cliente) references cliente(id_cliente),
    foreign key(id_audiencia) references audiencias(id_audiencia)
    );

