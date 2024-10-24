from typing import List
from psycopg2 import connect
from psycopg2.extensions import cursor as cursor

from auth.hashing_psw import get_password_hash
from core.settings import config


def create_role_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS role (
                role_id SERIAL PRIMARY KEY,
                role_name VARCHAR(255)
            );
        """
    )

def create_users_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                role_id INT DEFAULT 1,
                username VARCHAR(255),
                hashed_password VARCHAR(255),
                email VARCHAR(255) DEFAULT NULL,
                photo_path VARCHAR(255) DEFAULT NULL,
                
                FOREIGN KEY (role_id) 
                REFERENCES role (role_id)
            );
        """
    )

def create_product_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS product (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(255),
                product_price INT,
                product_description TEXT,
                is_hidden BOOLEAN DEFAULT false,
                photo_path VARCHAR(255)
            );
        """
    )

def create_comment_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS comment (
                comment_id SERIAL PRIMARY KEY,
                user_id INT,
                product_id INT,
                comment_rating INT,
                comment_date DATE,
                comment_text VARCHAR(255) DEFAULT NULL,
                photo_path VARCHAR(255) DEFAULT NULL,
            
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id),
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id) 
                ON DELETE SET NULL
            );
        """
    )

def create_orders_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                product_id INT,
                user_id INT,
                date_start DATE,
                date_end DATE,
                delivery_address VARCHAR(255),
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id),
                
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id)
                ON DELETE CASCADE
            );
        """
    )

def create_cart_item_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS cart_item (
                cart_item_id SERIAL PRIMARY KEY,
                product_id INT,
                user_id INT,
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id)
                ON DELETE CASCADE,
                
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id)
                ON DELETE CASCADE
            ); 
        """
    )

def create_roles(sql_cursor: cursor, role_names: List[List[str]]) -> None:
    sql_cursor.executemany(
        """
            INSERT INTO role (
                role_name
            )
            VALUES (%s);
        """,
        role_names
    )

def create_owner_account(sql_cursor: cursor) -> None:
    password_hash = get_password_hash(config.SUPERUSER_PASSWORD)

    sql_cursor.execute(
        """
            INSERT INTO users (
                role_id,
                username,
                hashed_password
            )    
            VALUES (
                (SELECT MAX(role_id) FROM role), %s, %s
            );
        """,
        [config.SUPERUSER_USERNAME, password_hash]
    )


def init_database() -> None:
    connection = connect(
        dbname=config.DATABASE_NAME,
        user=config.DATABASE_USER,
        password=config.DATABASE_USER_PASSWORD,
        host=config.DATABASE_HOST,
        port=config.DATABASE_PORT
    )
    sql_cursor = connection.cursor()

    create_role_table(sql_cursor)
    create_users_table(sql_cursor)
    create_product_table(sql_cursor)
    create_comment_table(sql_cursor)
    create_orders_table(sql_cursor)
    create_cart_item_table(sql_cursor)

    create_roles(
        sql_cursor,
        [
            ["пользователь"],
            ["администратор"],
            ["суперпользователь"]
        ]
    )
    create_owner_account(sql_cursor)

    connection.commit()
    sql_cursor.close()
    connection.close()


if __name__ == "__main__":
    init_database()
