from pathlib import Path
import joblib ,sklearn

MODEL_PATH = Path("/Users/albertorey/dev/icai-muiaap-operacion-de-modelos/semana3/assets/wine_quality_classifier.joblib")

diccionario_del_joblib = joblib.load(MODEL_PATH)
estimator = diccionario_del_joblib["estimator"]

print(diccionario_del_joblib)
print("\n")
print(diccionario_del_joblib.keys())            # qué más hay en el diccionario
print("\n")
print(type(estimator).__name__)    #type(modelo) dice que objeto es,type(modelo).__name__ si solo quieres el nombre de la clase.     
print("\n")
print(estimator.classes_)                       # etiquetas que predice
print("\n")
print(getattr(estimator, "feature_names_in_", None))  # nombres de features
print("\n")
print(estimator.n_features_in_)                 # cuántas features espera
print("\n")
print(joblib.__version__, sklearn.__version__)  # versiones
print("\n")

print(diccionario_del_joblib)

#resultado = diccionario_del_joblib.predict([[7.4, 0.7, 0, 1.9, 0.076, 11, 34, 0.9978, 3.51, 0.56, 9.4]])

#print(resultado)



