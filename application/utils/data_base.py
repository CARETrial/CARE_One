#!/usr/bin/env python

#    Copyright (C) 2021 CARE Trial
#    Email: CARE Trial <care.trial.2019@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
##############################################################################

"""
Database util module. 
- Helper functions for database related tasks
"""

# =============================================================================
# Standard library imports
# =============================================================================
import logging
import json
import os

#==============================================================================
# Third-party imports
#==============================================================================
from PyQt5.QtSql import  QSqlQuery

#==============================================================================
# Local application imports
#==============================================================================
from .calculations import _calcQuartiles


#==============================================================================
# Setup Logging
#==============================================================================
# Get the logger specified in the file
logger = logging.getLogger(__name__)
base_path = os.path.abspath(os.path.dirname(__file__))

def save_db_hour(db, P, Q, Ers, Rrs, b_count, b_type, PEEP, PIP, TV, DP, AImag, b_num_all, b_len, p_no, date, hour, debug):

    # Calculate quartiles    
    dObj = _calcQuartiles(Ers, Rrs, PEEP, PIP, TV, DP)

    # Encoding python object to json
    p = json.dumps(P)
    q = json.dumps(Q)
    Ers_raw = json.dumps(Ers)
    Rrs_raw = json.dumps(Rrs)
    PEEP_raw = json.dumps(PEEP)
    PIP_raw = json.dumps(PIP)
    TV_raw = json.dumps(TV)
    DP_raw = json.dumps(DP)
    AM_raw = json.dumps(AImag)
    b_type_encoded = json.dumps(b_type)
    b_num_all = json.dumps(b_num_all)
    b_len = json.dumps(b_len)
    debug = json.dumps(debug)

    Norm_cnt = b_type.count('Normal')
    Asyn_cnt = b_type.count('Asyn')
    AI_index = round(Asyn_cnt/(Asyn_cnt+Norm_cnt)*100,2)

    query = QSqlQuery(db)
    query.prepare(f"""INSERT INTO results (p_no, date, hour, p, q, b_count, b_type, b_num_all, b_len, debug,
                    Ers_raw, Rrs_raw, PEEP_raw, PIP_raw, TV_raw, DP_raw, AM_raw,
                    Ers_q5,  Rrs_q5,  PEEP_q5,  PIP_q5,  TV_q5,  DP_q5,
                    Ers_q25, Rrs_q25, PEEP_q25, PIP_q25, TV_q25, DP_q25,
                    Ers_q50, Rrs_q50, PEEP_q50, PIP_q50, TV_q50, DP_q50,
                    Ers_q75, Rrs_q75, PEEP_q75, PIP_q75, TV_q75, DP_q75,
                    Ers_q95, Rrs_q95, PEEP_q95, PIP_q95, TV_q95, DP_q95,
                    Ers_min, Rrs_min, PEEP_min, PIP_min, TV_min, DP_min,
                    Ers_max, Rrs_max, PEEP_max, PIP_max, TV_max, DP_max,
                    AI_Norm_cnt, AI_Asyn_cnt, AI_Index) 
                    VALUES (:p_no, :date, :hour, :p, :q, :b_count, :b_type, :b_num_all, :b_len, :debug,
                    :Ers_raw, :Rrs_raw, :PEEP_raw, :PIP_raw, :TV_raw, :DP_raw, :AM_raw,
                    :Ers_q5,  :Rrs_q5,  :PEEP_q5,  :PIP_q5,  :TV_q5,  :DP_q5,
                    :Ers_q25, :Rrs_q25, :PEEP_q25, :PIP_q25, :TV_q25, :DP_q25,
                    :Ers_q50, :Rrs_q50, :PEEP_q50, :PIP_q50, :TV_q50, :DP_q50,
                    :Ers_q75, :Rrs_q75, :PEEP_q75, :PIP_q75, :TV_q75, :DP_q75,
                    :Ers_q95, :Rrs_q95, :PEEP_q95, :PIP_q95, :TV_q95, :DP_q95,
                    :Ers_min, :Rrs_min, :PEEP_min, :PIP_min, :TV_min, :DP_min,
                    :Ers_max, :Rrs_max, :PEEP_max, :PIP_max, :TV_max, :DP_max,
                    :AI_Norm_cnt, :AI_Asyn_cnt, :AI_Index)""")
    query.bindValue(":p_no", p_no)
    query.bindValue(":date", date)
    query.bindValue(":hour", hour)
    query.bindValue(":p", p)
    query.bindValue(":q", q)
    query.bindValue(":b_count", b_count)
    query.bindValue(":b_type", b_type_encoded)
    query.bindValue(":Ers_raw", Ers_raw)
    query.bindValue(":Rrs_raw", Rrs_raw)
    query.bindValue(":PEEP_raw", PEEP_raw)
    query.bindValue(":PIP_raw", PIP_raw)
    query.bindValue(":TV_raw", TV_raw)
    query.bindValue(":DP_raw", DP_raw)
    query.bindValue(":AM_raw", AM_raw)
    query.bindValue(":b_num_all", b_num_all)
    query.bindValue(":b_len", b_len)
    query.bindValue(":debug", debug)
    
    query.bindValue(":Ers_q5", float(dObj['Ers']['q5']))
    query.bindValue(":Rrs_q5", float(dObj['Rrs']['q5']))
    query.bindValue(":PEEP_q5", float(dObj['PEEP']['q5']))
    query.bindValue(":PIP_q5", float(dObj['PIP']['q5']))
    query.bindValue(":TV_q5", float(dObj['TV']['q5']))
    query.bindValue(":DP_q5", float(dObj['DP']['q5']))

    query.bindValue(":Ers_q25", float(dObj['Ers']['q25']))
    query.bindValue(":Rrs_q25", float(dObj['Rrs']['q25']))
    query.bindValue(":PEEP_q25", float(dObj['PEEP']['q25']))
    query.bindValue(":PIP_q25", float(dObj['PIP']['q25']))
    query.bindValue(":TV_q25", float(dObj['TV']['q25']))
    query.bindValue(":DP_q25", float(dObj['DP']['q25']))
    
    query.bindValue(":Ers_q50", float(dObj['Ers']['q50']))
    query.bindValue(":Rrs_q50", float(dObj['Rrs']['q50']))
    query.bindValue(":PEEP_q50", float(dObj['PEEP']['q50']))
    query.bindValue(":PIP_q50", float(dObj['PIP']['q50']))
    query.bindValue(":TV_q50", float(dObj['TV']['q50']))
    query.bindValue(":DP_q50", float(dObj['DP']['q50']))
    
    query.bindValue(":Ers_q75", float(dObj['Ers']['q75']))
    query.bindValue(":Rrs_q75", float(dObj['Rrs']['q75']))
    query.bindValue(":PEEP_q75", float(dObj['PEEP']['q75']))
    query.bindValue(":PIP_q75", float(dObj['PIP']['q75']))
    query.bindValue(":TV_q75", float(dObj['TV']['q75']))
    query.bindValue(":DP_q75", float(dObj['DP']['q75']))
    
    query.bindValue(":Ers_q95", float(dObj['Ers']['q95']))
    query.bindValue(":Rrs_q95", float(dObj['Rrs']['q95']))
    query.bindValue(":PEEP_q95", float(dObj['PEEP']['q95']))
    query.bindValue(":PIP_q95", float(dObj['PIP']['q95']))
    query.bindValue(":TV_q95", float(dObj['TV']['q95']))
    query.bindValue(":DP_q95", float(dObj['DP']['q95']))
    
    query.bindValue(":Ers_min", float(dObj['Ers']['min']))
    query.bindValue(":Rrs_min", float(dObj['Rrs']['min']))
    query.bindValue(":PEEP_min", float(dObj['PEEP']['min']))
    query.bindValue(":PIP_min", float(dObj['PIP']['min']))
    query.bindValue(":TV_min", int(dObj['TV']['min']))
    query.bindValue(":DP_min", float(dObj['DP']['min']))
    
    query.bindValue(":Ers_max", float(dObj['Ers']['max']))
    query.bindValue(":Rrs_max", float(dObj['Rrs']['max']))
    query.bindValue(":PEEP_max", float(dObj['PEEP']['max']))
    query.bindValue(":PIP_max", float(dObj['PIP']['max']))
    query.bindValue(":TV_max", int(dObj['TV']['max']))
    query.bindValue(":DP_max", float(dObj['DP']['max']))

    query.bindValue(":AI_Norm_cnt", Norm_cnt)
    query.bindValue(":AI_Asyn_cnt", Asyn_cnt)
    query.bindValue(":AI_Index", AI_index)
    if query.exec_():
        logger.info("DB entry query successful")
    else:
        logger.error(f"Error: {query.lastError().text()}")