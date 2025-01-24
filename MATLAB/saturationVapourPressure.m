% -*-*- Formula 3 -*-*-
% Vapour pressure to saturation : Pvs [Pa]
% Dried bulb temperature Tbs: Tbs [C]

function Pvs = saturationVapourPressure(Tbs)
A = [-5.6745359*10^3 6.3925247*10^0 -9.677843*10^-3 0.6221570*10^-6 2.0747825*10^-9 -0.94844024*10^-12 4.1635019*10^0
    -5.8002206*10^3 1.3914993*10^0 -48.640239*10^-3 41.764768*10^-6 -14.452093*10^-9 0.0 6.5459673*10^0];
cond1 = find(-100<=Tbs&Tbs<0);
cond2 = find(0<=Tbs&Tbs<=200);

% From C to K
Tbs = Tbs+273.15;
if ~isempty(cond1)
    Pvs(cond1) = exp(A(1,1)*Tbs(cond1).^-1+A(1,2)*Tbs(cond1).^0+A(1,3)*Tbs(cond1).^1+A(1,4)*Tbs(cond1).^2+A(1,5)*Tbs(cond1).^3+A(1,6)*Tbs(cond1).^4+A(1,7).*log(Tbs(cond1)));
end
if ~isempty(cond2)
    Pvs(cond2) = exp(A(2,1)*Tbs(cond2).^-1+A(2,2)*Tbs(cond2).^0+A(2,3)*Tbs(cond2).^1+A(2,4)*Tbs(cond2).^2+A(2,5)*Tbs(cond2).^3+A(2,6)*Tbs(cond2).^4+A(2,7).*log(Tbs(cond2)));
end
%temp = A(row,7).*log(Tbs)+temp;

end