% -*-*- Formula 4 and Formula 5 -*-*-
% Humidity ratio (mv/ma) (to saturation): w (ws)  [kg_mv/kg_ma]
% Vapour pressure (to saturation) : Pv (Pvs) [Pa]
% Total pressure : P [Pa]

function w = humidityRatio(Pv,P)
w = 0.622*Pv./(P-Pv);
end