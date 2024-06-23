FROM python:3.9

# Instalar dependencias
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código de la aplicación
COPY . /app

# Establecer el directorio de trabajo
WORKDIR /app

# Exponer el puerto 8080
EXPOSE 8080

# Ejecutar el script
CMD ["python", "tu_script.py"]
