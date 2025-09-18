# Dockerfile

# Etapa 1: Usar uma imagem base oficial do Python.
# Usamos a versão 'slim' por ser menor e mais otimizada.
FROM python:3.9-slim

# Etapa 2: Definir o diretório de trabalho dentro do contêiner.
# Todos os comandos a seguir serão executados a partir deste diretório.
WORKDIR /app

# Etapa 3: Copiar o arquivo de dependências e instalá-las.
# Copiamos este arquivo primeiro para aproveitar o cache do Docker.
# Se o requirements.txt não mudar, o Docker não reinstala tudo de novo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 4: Copiar o resto do código da aplicação para o contêiner.
COPY . .

# Etapa 5: Expor a porta que a aplicação vai rodar dentro do contêiner.
# O Gunicorn vai rodar na porta 5000.
EXPOSE 5000

# Etapa 6: Comando para iniciar a aplicação quando o contêiner rodar.
# Usamos o Gunicorn para iniciar o servidor de produção.
# '--bind 0.0.0.0:5000' faz o servidor aceitar conexões de fora do contêiner.
# 'app:app' refere-se ao arquivo app.py e à variável app = Flask(__name__)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]