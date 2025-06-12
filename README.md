#instalando alembic e criando a pasta migrations:
poetry add alembic/poetry run alembic init migrations

- Depois ir no env.py fazer as configurações
  #comanado para mostrar a estrutura gráfica do banco de dados:
  pipx run harlequin database.db
