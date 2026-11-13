# Asistente entrenado del tutorial

Clasificador de intenciones con TF-IDF y regresión logística; no es un LLM generativo ni el Proyecto 2 del dominio individual. Dataset propio: 60 frases, seis intenciones. El entrenamiento ocurre fuera de HTTP y guarda `modelo_asistente.joblib`. Se conserva el holdout estratificado de doce frases en `prueba.csv`, con métricas reales en `metricas.txt`; una prueba tan pequeña no acredita calidad de producción.

Reproducir desde la raíz:

```powershell
python -c "from laboratorio.asistente import entrenar; print(entrenar())"
```

`POST /entregas/asistente/` recibe `{"mensaje":"quiero rastrear el folio UUID_COMPLETO"}`. El clasificador identifica intención; el backend obtiene de Pedido el estado/motivo guardado. Un folio inexistente no recibe estado inventado. Una pregunta de recomendación deriva al formulario del modelo. Mensajes fuera de dominio o sin vocabulario conocido no reciben una respuesta factual improvisada.

El chat Flutter se encuentra en la sección API y chat. El artefacto se carga una vez por proceso y no se entrega a Flutter. La respuesta usa plantillas según intención **después de consultar el modelo entrenado**; no se presenta una lista fija de frases como si fuera entrenamiento.

Límites observados: el clasificador confunde algunas preguntas de recomendación en la prueba. Debe ampliarse la variedad de datos y evaluarse fuera de la muestra antes de usarlo realmente. El umbral de aclaración y el manejo de vocabulario desconocido no sustituyen esa evaluación. Para datos reales de clientes hacen falta identidad y autorización sobre el folio; este tutorial se ejecuta localmente con datos de práctica.
