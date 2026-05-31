%% ======================================================
%   MODELO COMPLETO PREDICCIÓN LARVAS + FRASS
% ======================================================
clc; clear; close all;

%% ---- 1. Cargar archivo y limpiar nombres ----
filename = 'biodegradacion.xlsx';

opts = detectImportOptions(filename,'NumHeaderLines',0);
opts = setvartype(opts,'char'); % evita errores por celdas mixtas

raw = readtable(filename, opts);

% convertir a formato numérico donde aplique
data = readtable(filename,'PreserveVariableNames',true);

% limpieza obligatoria de nombres
rawNames = raw.Properties.VariableNames;
cleanNames = matlab.lang.makeValidName(rawNames);
data.Properties.VariableNames = cleanNames;

disp("Columnas limpias:");
disp(data.Properties.VariableNames');

%% ---- 2. Variables de entrada (todas las fisicoquímicas) ----
inputVars = {
    'Humedad___', 'pH', 'Cenizas___', 'Carbono_organico_total_oxidable___',...
    'Nitrogeno_total___','Relacion_carbono_nitrogeno_C_N','Fosforo_total___',...
    'Potasio_total___','Calcio_total___','Magnesio_total___','Densidad_g_cm3',...
    'Lignina___db','Mezcla_Humedad','Mezcla_pH','Mezcla_Cenizas','Mezcla_C_Org',...
    'Mezcla_N_Total','Mezcla_C_N','Mezcla_P_Total','Mezcla_K_Total',...
    'Mezcla_Ca_Total','Mezcla_Mg_Total','Mezcla_Densidad','Mezcla_Lignina',...
    'Temperatura','Relacion_C_N'
};

inputVars = intersect(inputVars, data.Properties.VariableNames);
X = data{:, inputVars};

%% ---- 3. Variables de salida larvas ----
Y_larvas = table();
Y_larvas.Humedad = data.Larva_Humedad;
Y_larvas.N = data.Larva_N_Organico;
Y_larvas.Grasa = data.Larva_Extracto_Etereo;
Y_larvas.Proteina = data.Larva_Proteina;

%% ---- 4. Variables de salida frass ----
Y_frass = table();
Y_frass.Humedad = data.Frass_Humedad;
Y_frass.pH = data.Frass_pH;
Y_frass.Cenizas = data.Frass_Cenizas;
Y_frass.C_Org = data.Frass_C_Organico;
Y_frass.N_Total = data.Frass_N_Total;
Y_frass.C_N = data.Frass_C_N;
Y_frass.P = data.Frass_Fosforo;
Y_frass.Potasio = data.Frass_Potasio;
Y_frass.Densidad = data.Frass_Densidad;

%% ---- 5. Crear modelos múltiples ----
modelos_larvas = struct();
modelos_frass = struct();

% entrenar modelos para larvas
outNamesL = Y_larvas.Properties.VariableNames;
for i = 1:length(outNamesL)
    modelos_larvas.(outNamesL{i}) = fitlm(X, Y_larvas.(outNamesL{i}));
end

% entrenar modelos para frass
outNamesF = Y_frass.Properties.VariableNames;
for i = 1:length(outNamesF)
    modelos_frass.(outNamesF{i}) = fitlm(X, Y_frass.(outNamesF{i}));
end

disp("Modelos entrenados correctamente.");

%% ---- 6. Predicciones ----
pred_larvas = Y_larvas;
pred_frass = Y_frass;

for i = 1:length(outNamesL)
    pred_larvas.(outNamesL{i}) = predict(modelos_larvas.(outNamesL{i}), X);
end

for i = 1:length(outNamesF)
    pred_frass.(outNamesF{i}) = predict(modelos_frass.(outNamesF{i}), X);
end

%% ---- 7. Temperatura óptima ----
temp = data.Temperatura;
tasa = data.Tasa_Bioconversion;

[crec_max, idx] = max(tasa);
temp_opt = temp(idx);

fprintf("\n>>> Temperatura óptima: %.2f °C\n", temp_opt);
fprintf(">>> Máxima tasa observada: %.4f\n\n", crec_max);

%% ---- 8. Graficar crecimiento observado vs predicho ----
figure; hold on;
plot(tasa,'bo','LineWidth',2);
plot(pred_larvas.Proteina,'r','LineWidth',2);
legend("Crecimiento real","Predicción proteína larval");
title("Crecimiento vs Predicción");
xlabel("Ensayos"); ylabel("Valor");
grid on;

%% ---- 9. Exportar todo ----
allResults = [
    dataset2table(struct2dataset(Y_larvas)) ...
    dataset2table(struct2dataset(pred_larvas)) ...
    dataset2table(struct2dataset(Y_frass)) ...
    dataset2table(struct2dataset(pred_frass))
];

writetable(allResults,'predicciones_larvas_frass.xlsx');
disp("Archivo exportado: predicciones_larvas_frass.xlsx");
