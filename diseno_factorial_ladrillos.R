# ==============================================================================
# DISEÑO FACTORIAL 2^4 — RESISTENCIA MECÁNICA DE LADRILLOS TEXTILES
# Empresa: Egipcia Vestidos | Universidad del Magdalena | 2026
#
# Variable respuesta: Resistencia mecánica (MPa o kgf/cm²)
#
# FACTORES (2 niveles cada uno):
#   A: Tamaño de fibra triturada  → Nivel bajo (-1): 7 mm  | Alto (+1): 40 mm
#   B: Proporción de pegamento    → Nivel bajo (-1): 15%   | Alto (+1): 25%
#   C: Presión de compresión      → Nivel bajo (-1): 5 ton | Alto (+1): 10 ton
#   D: Tiempo de secado           → Nivel bajo (-1): 8 días| Alto (+1): 10 días
# ==============================================================================


# --- 0. INSTALAR Y CARGAR PAQUETES -------------------------------------------
paquetes <- c("FrF2", "ggplot2", "dplyr", "gridExtra")
instalados <- paquetes[!paquetes %in% installed.packages()[, "Package"]]
if (length(instalados)) install.packages(instalados, dependencies = TRUE)

library(FrF2)
library(ggplot2)
library(dplyr)
library(gridExtra)


# --- 1. GENERAR MATRIZ DE DISEÑO 2^4 (16 corridas) ---------------------------
diseno <- FrF2(
  nruns       = 16,
  nfactors    = 4,
  factor.names = list(
    A_fibra     = c("7mm",  "40mm"),
    B_pegamento = c("15%",  "25%"),
    C_presion   = c("5ton", "10ton"),
    D_secado    = c("8dias","10dias")
  ),
  randomize = FALSE   # FALSE = orden estándar Yates; cambiar a TRUE en laboratorio
)

cat("=== MATRIZ DE DISEÑO 2^4 ===\n")
print(diseno)


# --- 2. INGRESAR RESULTADOS DE RESISTENCIA ------------------------------------
# *** REEMPLAZA ESTOS 16 VALORES CON TUS MEDICIONES REALES (en MPa o kgf/cm²) ***
# El orden corresponde al orden estándar de Yates (A-B-C-D combinaciones)

resistencia_MPa <- c(
  # A-  B-  C-  D-       A+  B-  C-  D-       A-  B+  C-  D-       A+  B+  C-  D-
    1.8,                  2.6,                  2.2,                  3.1,
  # A-  B-  C+  D-       A+  B-  C+  D-       A-  B+  C+  D-       A+  B+  C+  D-
    2.4,                  3.3,                  2.9,                  4.0,
  # A-  B-  C-  D+       A+  B-  C-  D+       A-  B+  C-  D+       A+  B+  C-  D+
    2.0,                  2.8,                  2.5,                  3.4,
  # A-  B-  C+  D+       A+  B-  C+  D+       A-  B+  C+  D+       A+  B+  C+  D+
    2.6,                  3.5,                  3.2,                  4.5
)

# Asociar respuesta al diseño
diseno$Resistencia <- resistencia_MPa

cat("\n=== DISEÑO CON RESPUESTA ===\n")
print(diseno)


# --- 3. CALCULAR EFECTOS ESTIMADOS -------------------------------------------
# En un 2^k sin réplicas el modelo queda saturado (sin grados de libertad
# para el error puro). Se usa el método gráfico de Daniel para discriminar
# efectos reales del ruido.

modelo_completo <- lm(
  Resistencia ~ A_fibra * B_pegamento * C_presion * D_secado,
  data = diseno
)

efectos <- coef(modelo_completo)[-1] * 2   # multiplicar x2: convención efectos
efectos_df <- data.frame(
  Termino    = names(efectos),
  Efecto     = efectos,
  AbsEfecto  = abs(efectos)
) %>% arrange(desc(AbsEfecto))

cat("\n=== EFECTOS ESTIMADOS (ordenados por magnitud) ===\n")
print(efectos_df, row.names = FALSE)


# --- 4. GRÁFICA DE PROBABILIDAD NORMAL DE EFECTOS (Método de Daniel) ---------
# Los efectos que se desvían de la línea recta son los significativos.

n_ef <- nrow(efectos_df)
efectos_ord <- sort(efectos_df$Efecto)
etiquetas   <- efectos_df$Termino[order(efectos_df$Efecto)]
probs       <- (seq_len(n_ef) - 0.5) / n_ef
z_teorico   <- qnorm(probs)

df_normal <- data.frame(
  Z       = z_teorico,
  Efecto  = efectos_ord,
  Termino = etiquetas
)

p_normal <- ggplot(df_normal, aes(x = Z, y = Efecto, label = Termino)) +
  geom_point(color = "steelblue", size = 3) +
  geom_smooth(method = "lm", se = FALSE, color = "gray50", linetype = "dashed",
              linewidth = 0.8) +
  geom_label(size = 2.8, hjust = -0.1, fill = "white", label.size = 0.2) +
  labs(
    title    = "Gráfica de Probabilidad Normal de Efectos",
    subtitle = "Ladrillos Textiles Egipcia — Resistencia Mecánica",
    x        = "Cuantil Normal Teórico",
    y        = "Efecto Estimado"
  ) +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold"))

print(p_normal)
ggsave("normal_efectos_ladrillos.png", p_normal, width = 9, height = 6, dpi = 150)
cat("Guardada: normal_efectos_ladrillos.png\n")


# --- 5. DIAGRAMA DE PARETO DE EFECTOS ----------------------------------------
# Muestra cuáles efectos tienen mayor magnitud absoluta.

p_pareto <- ggplot(efectos_df, aes(x = reorder(Termino, AbsEfecto), y = AbsEfecto)) +
  geom_col(fill = "steelblue", color = "black", alpha = 0.85) +
  coord_flip() +
  labs(
    title    = "Diagrama de Pareto de Efectos",
    subtitle = "Variable respuesta: Resistencia mecánica (MPa)",
    x        = "Factor / Interacción",
    y        = "Magnitud del Efecto |βi|"
  ) +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold"))

print(p_pareto)
ggsave("pareto_efectos_ladrillos.png", p_pareto, width = 9, height = 6, dpi = 150)
cat("Guardada: pareto_efectos_ladrillos.png\n")


# --- 6. MODELO REDUCIDO (solo efectos significativos) -------------------------
# Después de identificar visualmente los efectos significativos en la gráfica
# normal, se incluyen solo esos términos. Los efectos no significativos se
# agrupan como error residual para obtener el test F.
#
# INSTRUCCIÓN: modifica la fórmula según lo que observes en la gráfica normal.
# Ejemplo hipotético: A, C y la interacción A:C son significativos.

modelo_reducido <- lm(
  Resistencia ~ A_fibra + B_pegamento + C_presion + A_fibra:C_presion,
  data = diseno
)

cat("\n=== MODELO REDUCIDO — RESUMEN ===\n")
print(summary(modelo_reducido))

cat("\n=== MODELO REDUCIDO — ANOVA ===\n")
tabla_anova <- anova(modelo_reducido)
print(tabla_anova)


# --- 7. IDENTIFICAR FACTORES SIGNIFICATIVOS (α = 0.05) -----------------------
significativos <- rownames(tabla_anova)[
  !is.na(tabla_anova[["Pr(>F)"]]) & tabla_anova[["Pr(>F)"]] < 0.05
]

cat("\n=== FACTORES SIGNIFICATIVOS (α = 0.05) ===\n")
if (length(significativos) > 0) {
  for (s in significativos) cat(" •", s, "\n")
} else {
  cat("Ninguno significativo. Revisa el modelo reducido o aumenta réplicas.\n")
}


# --- 8. GRÁFICAS DE EFECTOS PRINCIPALES E INTERACCIONES ----------------------
# Usa las funciones nativas de FrF2 (requiere pasar la respuesta al objeto)

diseno_FrF2 <- add.response(diseno, resistencia_MPa)

cat("\n=== GRÁFICAS DE EFECTOS PRINCIPALES ===\n")
MEPlot(diseno_FrF2,
       main = "Efectos Principales — Resistencia Mecánica\nLadrillos Textiles Egipcia")

cat("\n=== GRÁFICAS DE INTERACCIONES ===\n")
IAPlot(diseno_FrF2,
       main = "Gráficas de Interacción — Resistencia Mecánica")


# --- 9. GRÁFICAS DE DIAGNÓSTICO DEL MODELO REDUCIDO -------------------------
par(mfrow = c(2, 2))
plot(modelo_reducido,
     main = "Diagnóstico Modelo Reducido — Ladrillos Textiles")
par(mfrow = c(1, 1))


# --- 10. TABLA RESUMEN FINAL --------------------------------------------------
cat("\n")
cat("=======================================================\n")
cat(" RESUMEN DISEÑO FACTORIAL 2^4 — LADRILLOS TEXTILES\n")
cat("=======================================================\n")
cat(" Empresa       : Egipcia Vestidos\n")
cat(" Resp. variable: Resistencia mecánica (MPa)\n")
cat(" Factores      : 4  |  Corridas: 16  |  Réplicas: 1\n")
cat("-------------------------------------------------------\n")
cat(" Factor A: Tamaño de fibra   (7mm  vs 40mm)\n")
cat(" Factor B: % Pegamento       (15%  vs 25% )\n")
cat(" Factor C: Presión compres.  (5ton vs 10ton)\n")
cat(" Factor D: Tiempo de secado  (8d   vs 10d  )\n")
cat("=======================================================\n")
cat(" Archivos generados:\n")
cat("   - normal_efectos_ladrillos.png\n")
cat("   - pareto_efectos_ladrillos.png\n")
cat("=======================================================\n")
