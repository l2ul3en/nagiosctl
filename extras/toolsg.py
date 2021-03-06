#!/usr/bin/python3
#-------------------------------------------------------------------------------
# Name:        toolsg.py
# Purpose:     Funciones para procesamiento a nivel de hostgroups.cfg 
#
# Author:      Personal
#
# Created:     13/09/2020
# Copyright:   (c) Personal 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from sys import path
path.append('../../')
import ngctl.config.constantes as cons
from ngctl.clases.Body import Body
from ngctl.clases.Hostgroup import Hostgroup
from subprocess import getoutput as geto
from copy import deepcopy as copiar #permite copiar un objeto
import logging,logging.config

logging.config.fileConfig(cons.LOG_CONF)
logger = logging.getLogger(__name__)

def aplicar_cambios(datos):
    """Guarda los cambios previo Backup."""

    with open(cons.TMP_HGR, 'w') as f:
        for i in datos:
            print(i,file=f,flush=True)
    c = geto(f'cp -f {cons.DIR}{cons.ORIG_HGR} {cons.BACK_HGR}')
    c = geto(f'cp -f {cons.TMP_HGR} {cons.DIR}{cons.ORIG_HGR}')
    logger.info(f'OK Backup!!/se aplico los cambios a {cons.ORIG_HGR}', extra=cons.EXTRA)

def cargar():
    """Devuelve una lista de objetos Hostgroup.

Lee linea a linea el archivo especificado en constantes.py cargando todo las definiciones de hostgroups.
  Lista     ->  [['hostgroup_name',['atributo valor1',...,'atributo valorN']]]"""
    lista_group = []
    hostgroup = Hostgroup()
    with open (cons.DIR + cons.ORIG_HGR,'r') as f:
        for i in f:
            i = i.strip()
            if i == '' or i.startswith(('define','#')):
                continue
            elif i.startswith('}'):
                hostgroup.ordenar(rev=False)
                if hostgroup.existe_atributo('members',log=False):
                    lista_group.append(hostgroup)
                hostgroup = Hostgroup()
            else:
                if ',' in i:
                    hostgroup.add_parametro(procesar(i,','))
                else: hostgroup.add_parametro(i.split(maxsplit=1))
    return lista_group

def procesar(cad,char):
    atr = cad.split(maxsplit=1)[0]
    lista = cad.split(maxsplit=1)[1].split(char)
    lista = [i.strip() for i in lista if i != '']
    lista.sort(key=str.lower)
    if len(lista) == 1:
        val = ''.join(lista)
    else: val = char.join(lista)
    return [atr,val]

def get_hostgroups(datos):
    """Devuelve una lista con todos los nombres de hostgroups."""
    return [x.get_name() for x in datos]

def get_hostgroup(datos,hostgroup):
    """Retorna el objeto Hostgroup."""
    for i in datos:
        if i.get_name() == hostgroup:
            logger.info(f'se obtuvo el hostgroup {hostgroup}', extra=cons.EXTRA)
            return i
    logger.error(f'no se encontro el hostgroup {hostgroup}, exit..', extra=cons.EXTRA)
    raise SystemExit(2)

def get_list_host_in_group(datos,host):
    """Devuelve un iterable con todos los objetos Hostgroup a los que pertenece el host."""
    return filter(lambda x: x.existe_elemento('members',host),datos)

def get_listado_hosts(datos,hostgroup):
    """Devuelve una lista con todos los hosts asociados a hostgroup."""
    return [x.get_valor('members') for x in datos if x.get_name() == hostgroup]

def delete_hostgroup(datos,hostgroup):
    """Elimina el grupo asociado al hostgroup inidicado."""
    i = 0
    while i < len(datos):
        while i < len(datos) and datos[i].get_name() == hostgroup:
            del datos[i]
            logger.info(f'se elimino el hostgroup {hostgroup}', extra=cons.EXTRA)
        i += 1

def show_hostgroup(datos,hostgroup):
    """Imprime por pantalla la config del hostgroup indicado."""
    for i in (x for x in datos if x.get_name() == hostgroup):
        print(i)

def copy_hostgroup(datos,old,new):
    """Realiza la copia del hostgroup old para el hostgroup new."""
    hostgroup = Hostgroup()
    for i in range(len(datos)):
        if datos[i].get_name() == old:
            hostgroup = copiar(datos[i])
            datos.append(hostgroup)
            datos[-1].add_valor('hostgroup_name',new)
            datos[-1].add_valor('alias',new)
            logger.info(f'se copio {old} a {new} en {cons.ORIG_HGR}', extra=cons.EXTRA)

def existe_hostgroup(datos,hostgroup):
    """Verifica si el hostgroup existe."""
    for x in datos:
        if x.get_name() == hostgroup:
            return True
    return False


if __name__ == '__main__':
    l = cargar()
    l.sort()
    #for i in get_hostgroups(l):
    for i in l:
        print(i.get_name())
