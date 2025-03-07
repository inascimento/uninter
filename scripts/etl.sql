insert into zona_dim
select distinct cast(cd_sit as int), situacao from censo_ibge_setores
where cd_setor like '2927408%';

insert into municipio_dim
select distinct cast(cd_mun as int), nm_mun from censo_ibge_setores
where cd_setor like '2927408%';

insert into bairro_dim
select distinct cast(cd_bairro as int), nm_bairro from censo_ibge_setores
where cd_setor like '2927408%' and cd_bairro != '.';

insert into setor_fact
select cast(pe.cod_setor as int) id,
       cast(se.cd_sit as int) zona_id,
       cast(se.cd_mun as int) municipio_id,
       cast((case when se.cd_bairro != '.' then se.cd_bairro end) as int) bairro_id,
       cast((case when pe.v001 != 'X' then pe.v001 else '0' end) as int) ate_meio_salario,
       cast((case when pe.v002 != 'X' then pe.v002 else '0' end) as int) ate_um_salario,
       cast((case when pe.v010 != 'X' then pe.v010 else '0' end) as int) sem_salario,
       cast((case when pe.v020 != 'X' then pe.v020 else '0' end) as int) populacao
  from censo_ibge_renda_pessoa pe
 inner join censo_ibge_setores se
    on se.cd_setor = cast(pe.cod_setor as int)
 where pe.cod_setor like '2927408%';
