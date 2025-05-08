from website import create_app, db

app = create_app()

def init_db_from_sql():
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    with open('schema.sql', 'r') as f:
        sql = f.read()
    cursor.executescript(sql)
    connection.commit()
    cursor.close()
    connection.close()
    print("SQL schema loaded successfully.")

with app.app_context():
    init_db_from_sql()
