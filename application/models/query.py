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

"""Database table model"""

from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import logging

logger = logging.getLogger(__name__)
logger.info('Models module imported')

def createTable(db):
    # Create a query and execute it right away using .exec()
    logger.info('Creating db table if not exists')
    createTableQuery = QSqlQuery(db)
    createTableQuery.exec(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            p_no VARCHAR(50) NOT NULL,
            date VARCHAR(40) NOT NULL,
            hour VARCHAR(40) NOT NULL,
            p BLOB,
            q BLOB,
            Ers_raw BLOB,
            Rrs_raw BLOB,
            PEEP_raw BLOB,
            PIP_raw BLOB,
            TV_raw BLOB,
            DP_raw BLOB,
            AM_raw BLOB,
            b_type BLOB,
            b_count INTEGER,
            b_num_all BLOB,
            b_len BLOB,
            debug BLOB,
            
            --q5 reading
            Ers_q5 REAL,
            Rrs_q5 REAL,
            PEEP_q5 REAL,
            PIP_q5 REAL,
            TV_q5 REAL,
            DP_q5 REAL,

            --q25 reading
            Ers_q25 REAL,
            Rrs_q25 REAL,
            PEEP_q25 REAL,
            PIP_q25 REAL,
            TV_q25 REAL,
            DP_q25 REAL,

            --q50 reading
            Ers_q50 REAL,
            Rrs_q50 REAL,
            PEEP_q50 REAL,
            PIP_q50 REAL,
            TV_q50 REAL,
            DP_q50 REAL,

            --q75 reading
            Ers_q75 REAL,
            Rrs_q75 REAL,
            PEEP_q75 REAL,
            PIP_q75 REAL,
            TV_q75 REAL,
            DP_q75 REAL,

            --q95 reading
            Ers_q95 REAL,
            Rrs_q95 REAL,
            PEEP_q95 REAL,
            PIP_q95 REAL,
            TV_q95 REAL,
            DP_q95 REAL,

            --min reading
            Ers_min REAL,
            Rrs_min REAL,
            PEEP_min REAL,
            PIP_min REAL,
            TV_min REAL,
            DP_min REAL,

            --max reading
            Ers_max REAL,
            Rrs_max REAL,
            PEEP_max REAL,
            PIP_max REAL,
            TV_max REAL,
            DP_max REAL,

            --AI data
            AI_Norm_cnt INTEGER,
            AI_Asyn_cnt INTEGER,
            AI_Index REAL
            
        )
        """
    )