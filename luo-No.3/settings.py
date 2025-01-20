import os


DATABASE_CONFIG = {
    'dialect': 'mysql+pymysql',
    'username': 'root',
    'password': 'HYW',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'houyanwu',
}


def get_database_url(config):
    return f"{config['dialect']}://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

DATABASE_URL = get_database_url(DATABASE_CONFIG)


from sqlalchemy import create_engine


engine = create_engine(DATABASE_URL, echo=True)


from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)


session = Session()
