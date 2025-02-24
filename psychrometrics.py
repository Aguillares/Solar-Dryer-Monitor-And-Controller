class Psychometric():
    def __init__(self,Z):
        # Z: Altitude [m]
        self.get_pressure(Z)

    def get_pressure(self,Z):
        # With the altitude in meters, we get the pressure in Pascals
        # P: Pressure [Pa]
        # Z: Altitude [m]
        P = 101325*((1-(2.25577*10**-5)*self.Z)**-5.2559)
        return P

    def get_ratio_PvPa(self,mv,ma):
        # --Formula 1
        # Pv_Pa: Ratio between Water Vapour Pressure and Dried Air Pressure ["Pa" of Pv/"Pa" of Pa]
        # Pv : Water Vapour Pressure [Pa]
        # Pa : Dried Air Pressure [Pa]
        # Rv : Water Vapour Contanst [J/kg·K]
        # Ra : Dried Vapour Contanst [J/kg·K]
        # mv : Water Vapour Mass [kg]
        # ma : Dried Vapour Mass [kg]

        Pv_Pa = mv*461.52/(ma*287.055)
        
        return Pv_Pa

    def get_dv(self,mv,V):
        # --Formula 6
        # Absolute humidity : dv [kg/m^3]
        # Water vapour mass : mv [kg]
        # Total volume : V [m^3]
        dv = mv/V
        return dv

    def get_RH_mu(self,mu,Pvs,P):
        # --Formula 10
        # phi: Relative Humidity ["Pa" of Pv/ "Pa" of Pvs]
        # mu: Saturation Degree (w/ws) [adimensional]
        # Pvs: Water Vapour Pressure to Saturation [Pa]
        # P: Total pressure [Pa]
        phi = mu/(1-(1-mu)*(Pvs/P))

        return phi

    

    def get_Tpr(self,Tbs,Pv):
        #  -*-*- Formula 17 and Formula 18 -*-*-
        # If the specific takes as basis the humid air
        # Dew point temperature : Tpr [ºC]
        # Vapour pressure : Pv [Pa]
        # Temperature : Tbs [C]
        
        cond1 = find((-60<=Tbs)and(Tbs<=0));
        cond2 = find((0<Tbs)&(Tbs<=70));
        if ~isempty(cond1)
        Tpr(cond1) = -60.45 + 7.0322.*log(Pv(cond1)) + 0.37.*((log(Pv(cond1))).^2);
        end
        if ~isempty(cond2)
        Tpr(cond2) = -35.957 - 1.8726*log(Pv(cond2)) + 1.1689.*((log(Pv(cond2))).^2);




    def get_h(self,ha,hv,w):
        # --Formula 21
        # Enthalpy of humid air, we can say it's the internal energy
        # this divided by dried air mass, with respect to certain reference temperature.
        # Specific enthalpy of humid air : h [J/kg]
        # Specific dired air enthalpy : ha [J/kg]
        # Specific vapour water enthalpy : hv [J/kg]

        h = ha + w*hv

        return h  