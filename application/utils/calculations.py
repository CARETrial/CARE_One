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
Calculations module.
- Calculates Respiratory Mechanics (Elastance/Resistance) & Ventilation parameters
- Runs others mathematical calculations
"""

# =============================================================================
# Standard library imports
# =============================================================================
from scipy import integrate
import numpy as np
import logging
import math

#==============================================================================
# Setup Logging
#==============================================================================
# Get the logger specified in the file
logger = logging.getLogger(__name__)


class Elastance():


    def calcRespMechanics(self, path):
        """Responsible for opening text file, extracting breath number,
            splitting pressure and flow data, data filtering, and combine
            all metrics together.

        Args:
            path (string): file path

        Returns:
            P, Q, P_A, Q_A, Ers_A, Rrs_A, b_count, PEEP_A, PIP_A, TV_A, DP_A, b_num_all
        """
        pressure, flow, b_num_all, b_len, rejected = [], [], [], [], []
        P, Q, Ers_A, Rrs_A, P_A, Q_A, PEEP_A, PIP_A, TV_A, DP_A = [],[],[],[],[],[],[],[],[],[]
        b_count = 0
        b_counter = [0,0,0,0,0,0]
        import time
        start = time.process_time()
        with open(path, "r") as f:
            for num, line in enumerate(f):
                if ("BS," in line) == True:
                    b_num = self._extractBNum(line)
                elif ("BE" in line) == True:
                    # return this no matter what
                    b_count += 1
                    b_len.append(len(pressure))
                    P.extend(pressure)          # for plotting purpose, include all 
                    Q.extend(flow)              # for plotting purpose, include all 
                    b_num_all.append(b_num)

                    # Calc and filter breath
                    if len(pressure) >= 20:
                        if len(pressure) == len(flow):
                            E, R, PEEP, PIP, TidalVolume, _, _ = self.linear_r(pressure, flow, useIM=True) # calculate respiratory parameter 
                            if abs(E) < 100:
                                if abs(R) < 100:
                                    if TidalVolume < 1:
                                        P_A.append(pressure)
                                        Q_A.append(flow)
                                        Ers_A.append(E)
                                        Rrs_A.append(R)
                                        PEEP_A.append(round(PEEP,1))
                                        PIP_A.append(round(PIP,1))
                                        TV_A.append(round(TidalVolume*1000))
                                        DP_A.append(round(PIP-PEEP,1))
                                        b_counter[0] += 1
                                    else:
                                        self.add_nan(P_A, Q_A, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A)
                                        rejected.append((b_num,f'THRESHOLD: VT >= 1000ml, RAW: {round(TidalVolume*1000)}'))
                                        b_counter[1] += 1
                                else:
                                    self.add_nan(P_A, Q_A, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A)
                                    rejected.append((b_num,f'THRESHOLD: abs(R) > 100, RAW: {R}'))
                                    b_counter[2] += 1
                            else:
                                self.add_nan(P_A, Q_A, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A)
                                rejected.append((b_num,f'THRESHOLD: abs(E) > 100, RAW: {E}'))
                                b_counter[3] += 1
                        else:
                            self.add_nan(P_A, Q_A, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A)
                            rejected.append((b_num,f'THRESHOLD: len(pressure) != len(flow), RAW: {len(pressure)},{len(flow)}'))
                            b_counter[4] += 1
                    else:
                        self.add_nan(P_A, Q_A, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A)
                        rejected.append((b_num,f'THRESHOLD: len(pressure) <= 20, RAW: {len(pressure)}'))
                        b_counter[5] += 1

                    # Clear P and Q temporary list
                    pressure, flow = [], [] # reset temp list
                else:
                    if line != '': # Filter out empty lines
                        section = line.split(',') # 2.34, 5.78 -> ['2.34','5.78']
                        try:
                            p_split = float(section[1])
                            q_split = float(section[0])
                            if abs(p_split) <= 100 and abs(q_split) <= 1000:
                                if len(pressure) > 1:
                                    # Get previous point
                                    P_i = float(last_sec[1])
                                    Q_i = float(last_sec[0])
                                    last_sec = section    

                                    if abs(p_split - P_i) <= 50:
                                        if abs(q_split - Q_i) <= 100:
                                            pressure.append(round(p_split,1))
                                            flow.append(round(q_split,1))
                                        else:
                                            rejected.append((b_num,f'LINE {num}, LINE DEL: Qi-Qi-1 >= 50, RAW: {q_split}, {Q_i}'))
                                    else:
                                        rejected.append((b_num,f'LINE {num}, LINE DEL: Pi-Pi-1 >= 50, RAW: {p_split}, {P_i}'))
                                else:
                                    last_sec = section
                                    pressure.append(round(p_split,1))
                                    flow.append(round(q_split,1))
                            else:
                                rejected.append((b_num,f'LINE DEL: abs(P)<=100 or abs(Q)<=1000, RAW: {p_split}, {q_split}'))
                        except Exception as e:
                            logger.info(e)
        logger.info(f'Time used to extract breath: {time.process_time() - start}')
        
        debug = {
            'rejected': rejected,
            'b_counter': b_counter
        }
        return P, Q, P_A, Q_A, Ers_A, Rrs_A, b_count, PEEP_A, PIP_A, TV_A, DP_A, b_num_all, b_len, debug
    
    def linear_r(self, P, Q, useIM):
        """Perform Linear Regression

        Args:
            P (list): Pressure list
            Q (list): Flow rate list
            useIM (boolean): True to use Integral method

        Returns:
            Ers, Rrs, PEEP_non_array, PIP, TidalVolume, IE, VE: Analysis results
        """
        temp_flow = np.array(Q)/60
        temp_pressure = P

        # get maximum pressure pip
        PIP = max(temp_pressure)

        flow_inspi,flow_expi,pressure_inspi,pressure_expi = self._seperate_breath(temp_pressure,temp_flow)
        
        b_points = np.size(pressure_inspi)
        Time = list(np.linspace(0, (b_points-1)*0.02, b_points))

        expi_b_points = np.size(flow_expi)
        expi_Time = list(np.linspace(0, (expi_b_points-1)*0.02, expi_b_points))

        b_points_total = np.size(temp_pressure)
        total_time = list(np.linspace(0, (b_points_total-1)*0.02, b_points_total))
        
        # get PEEP
        # use first inspi point as peep
        # PEEP = np.array(pressure_inspi[0]) 
        
        # use expi min as peep
        PEEP_non_array = math.floor(min(pressure_expi))
        PEEP = np.array(PEEP_non_array)  
        
        V = integrate.cumtrapz(flow_inspi, x=Time, initial=0)
        V_expi = integrate.cumtrapz(flow_expi, x=expi_Time, initial=0)
        V_total = integrate.cumtrapz(temp_flow, x=total_time, initial=0)+0.000001

        if useIM:
            # Using Integral method, reintegrate to reduce noise
            int_V = integrate.cumtrapz(V, x=Time, initial=0)
            int_Q = integrate.cumtrapz(flow_inspi, x=Time, initial=0)
            int_B = integrate.cumtrapz(pressure_inspi-PEEP, x=Time, initial=0)

            # Constructing Ax=B to obtain Ers and R
            A = np.vstack((int_V, int_Q)).T  # Transpose
            B = int_B
        else:
            # Constructing Ax=B to obtain Ers and R
            A = np.vstack((V, flow_inspi)).T  # Transpose
            B = pressure_inspi-PEEP

        # linear algebra method to return least square solution
        Ers, Rrs, = np.linalg.lstsq(A, B, rcond=-1)[0]

        # round Ers, Rrs to one decimal point
        Ers = np.around(Ers,1)
        Rrs = np.around(Rrs,1)

        # get other parameters
        TidalVolume = max(V)
        IE = len(flow_expi)/len(flow_inspi)
        VE = abs(min(V_expi))

        # Limit Rrs to zero, remove negative value
        if Rrs < 0:
            Rrs = 0

        return Ers, Rrs, PEEP_non_array, PIP, TidalVolume, IE, VE
    
    def add_nan(self, P_A, Q_A, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A):
        """Add numpy nan to list."""
        P_A.append([])
        Q_A.append([])
        Ers_A.append(np.nan)
        Rrs_A.append(np.nan)
        PEEP_A.append(np.nan)
        PIP_A.append(np.nan)
        TV_A.append(np.nan)
        DP_A.append(np.nan)
        return P_A, Q_A, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A
    
    def _get_V(self, Q):
        """Cumulative trapezoital integral to get tidal volume from air flow rate"""
        b_points = np.size(Q)
        time = list(np.linspace(0, (b_points-1)*0.02, b_points))
        return integrate.cumtrapz(Q, x=time, initial=0)
    
    def _seperate_breath(self, temp_pressure, temp_flow):
        """Seperate breath to inspiration and expiration"""
        # add 5 data points in future so that will avoid the 1st digit as negative
        Fth = 5
        flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1] <= 0)
        flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]

        while (len(flow_inspi) <= 10):
            # print(len(flow_head))
            # add 5 data points in future so that will avoid the 1st digit as negative
            flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1] <= 0)
            flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]
            Fth = Fth + 1

        # add 5 data points in future so that will avoid the 1st digit as negative
        flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1] <= 0)
        flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]

        flow_expi = temp_flow[flow_inspi_loc_ends+1+Fth::]
        flow_expi_loc_starts = np.argmin(flow_expi)
        flow_expi = flow_expi[flow_expi_loc_starts::]

        # % Pressure Inspiration and expiration
        pressure_inspi = temp_pressure[0:flow_inspi_loc_ends+Fth]
        pressure_expi = temp_pressure[flow_inspi_loc_ends+1+Fth::]
        # pressure_expi_T = pressure_expi[flow_expi_loc_starts::]

        return flow_inspi,flow_expi,pressure_inspi,pressure_expi

    def _extractBNum(self, line):
        """Gets current breath number for debug.
        Returns 0000 when failed."""
        try:
            b_num = [int(s) for s in line.replace(',\n','').split(':') if s.isdigit()][0]
        except:
            try:
                b_num = [int(s) for s in line.replace(',\r\n','').split(':') if s.isdigit()][0]
            except:
                try:
                    b_num = [int(s) for s in line.replace(',','').split(':') if s.isdigit()][0]
                except:
                    b_num = 0000
        return b_num

def _calcQuartiles(E, R, PEEP_A, PIP_A, TV_A, DP_A):
    """ Calc quartiles """
    TV_A = [np.around(x,0) for x in TV_A]
    params = ['Ers','Rrs','PEEP','PIP','TV','DP']
    paramsVal = [E, R, PEEP_A, PIP_A, TV_A, DP_A]
    rounding = [1,1,1,1,0,1]
    dObj = {
        'Ers':{},
        'Rrs':{},
        'PEEP':{},
        'PIP':{},
        'TV':{},
        'DP':{},
    }
    for i in range(len(params)):
        dObj[params[i]]['q5'],dObj[params[i]]['q25'],dObj[params[i]]['q50'],dObj[params[i]]['q75'],dObj[params[i]]['q95'] = np.around(np.nanquantile(paramsVal[i],[.05,.25,.50,.75,.95]),rounding[i])
        dObj[params[i]]['min'] = round(np.nanmin(paramsVal[i]),rounding[i])
        dObj[params[i]]['max'] = round(np.nanmax(paramsVal[i]),rounding[i])
    # chg to int to rmv rounding digit
    dObj['TV']['q5'],dObj['TV']['q25'],dObj['TV']['q50'],dObj['TV']['q75'],dObj['TV']['q95'] = dObj['TV']['q5'].astype(int) ,dObj['TV']['q25'].astype(int) ,dObj['TV']['q50'].astype(int) ,dObj['TV']['q75'].astype(int) ,dObj['TV']['q95'].astype(int)
    
    return dObj



