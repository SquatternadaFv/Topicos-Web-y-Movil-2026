# Predicciones de trabajo antes de ejecutar los experimentos

Estas son hipótesis elaboradas con asistencia, a partir del generador del profesor; no son recuerdos de una ejecución anterior ni se atribuyen a los demás integrantes. Se conservan aunque los resultados las contradigan.

1. **Retrato.** Espero que con lluvia domine moto: dron está prohibido y bicicleta recibe una penalización. En el centro espero bicicleta por trayectos cortos. Su distancia máxima debería ser 7 km. El generador no debería emitir etiquetas inviables, pues filtra primero los medios posibles.
2. **Hora.** Espero cero drones antes de las 6 y desde las 21. Como el muestreo favorece horas laborales, la noche tendrá menos ejemplos. Una columna binaria de noche debería reducir los drones imposibles sin pedir datos adicionales al usuario.
3. **Errores.** Espero confusión moto/bicicleta y moto/dron, cuyas regiones se solapan. No puedo garantizar cero confusión bicicleta/camioneta: ruido y hojas con varios ejemplos pueden mezclar etiquetas.
4. **Columnas.** Mi orden previo es distancia, refrigerado, peso, volumen, clima, hora, zona, prioridad, frágil, tráfico, valor, largo, ancho, alto. Espero que las medidas individuales añadan poco al volumen; importancia baja no elimina su función de validación.
5. **Balanceo.** Espero mayor recall de dron al ponderarlo y más falsos positivos, por lo que la precisión puede bajar. No balancearía la prueba. La rareza del dron está justificada por las restricciones, no demuestra por sí sola un error de muestreo.
6. **Etiquetas.** Espero que óptimo y etiquetas coincidan por encima del 90 %, sin asumir que sea un techo matemático estricto. El modelo podría tener menor costo que las etiquetas al suavizar ruido, aunque no necesariamente lo hará. Entrenar con etiquetas sin ruido debería acercarlo al óptimo.
7. **Coherencia.** El peso afecta factibilidad, no puntaje; reducirlo no debería desplazar un medio que sigue siendo factible por otro que ya era factible antes. Cambiar 10:00 por 16:00 manteniendo tráfico no cambia el óptimo. El árbol sin límite podría infringir más propiedades. No doy por probada esa comparación antes de medirla.
8. **Cambio.** Espero que la nueva capacidad de los drones cause más daño que variar la mezcla de climas: cambia el concepto, no solo la frecuencia. No espero que la confianza detecte siempre ese cambio. Actualizar reglas sin reentrenar elimina prohibiciones viejas, pero no enseña al modelo nuevas preferencias.

Los resultados se guardan aparte en `ANALISIS.md` y `resultados/`; una predicción no se modifica para hacerla coincidir con las mediciones.
