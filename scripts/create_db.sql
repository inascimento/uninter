drop table if exists setor_fact;
drop table if exists zona_dim;
drop table if exists municipio_dim;
drop table if exists bairro_dim;
drop table if exists censo_ibge_renda_pessoa;
drop table if exists censo_ibge_setores;

create table zona_dim (
	id int not null primary key,
	nome varchar(100)
);

create table municipio_dim (
	id bigint not null primary key,
	nome varchar(100)
);

create table bairro_dim (
	id bigint not null primary key,
	nome varchar(100)
);

create table setor_fact (
	id bigint not null primary key,
	zona_id int,
	municipio_id bigint,
	bairro_id bigint,
	ate_meio_salario int,
	ate_um_salario int,
	sem_salario int,
	populacao int,
	foreign key (zona_id) references zona_dim (id),
	foreign key (municipio_id) references municipio_dim (id),
	foreign key (bairro_id) references bairro_dim (id)
);

create table censo_ibge_renda_pessoa (
	cod_setor varchar(15),
	v001 varchar(10),
	v002 varchar(10),
	v010 varchar(10),
	v020 varchar(10)
);

create table censo_ibge_setores (
	cd_setor varchar(15),
	situacao  varchar(50),
	cd_sit  varchar(15),
	cd_mun  varchar(15),
	nm_mun  varchar(150),
	cd_bairro  varchar(15),
	nm_bairro  varchar(150)
);
