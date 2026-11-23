# Nota de compatibilidad

Esta semana he añadido el campo served_at a la respuesta del POST /v1/predictions, que es la hora a la que se devuelve la respuesta. Este cambio es compatible porque a un cliente que ya usaba la API no le rompe nada. Simplemente le llega un campo más que no conoce y lo ignora. Por eso la versión pasa de 1.0.0 a 1.1.0 y solo cambia el número del medio.

Lo que sí rompería a los clientes de la semana 7 sería cambiar el nombre de un campo o quitarlo (por ejemplo confidence) porque el cliente lo seguiría buscando y no lo encontraría. También rompe hacer más pequeño un rango de entrada, por ejemplo que el alcohol pase de valer entre 5 y 20 a valer entre 8 y 15, porque un valor que antes era válido ahora daría 422. Yo también pondría ahí añadir un nuevo campo(o banda) a QualityBand, ya que un cliente que no la conoce podría fallar al leerla.

Para esos cambios habría que subir la versión mayor (2.0.0) y sacar una ruta nueva /v2, dejando la /v1 funcionando un tiempo para que los clientes se pasen. Si solo arreglo una descripción o un ejemplo de /docs sería un parche (1.1.1).

Para no cambiar el contrato sin querer el test de S9.4 compara la API con contracts/openapi.json. Si la API cambia tengo que generar ese archivo otra vez y subir la versión.
