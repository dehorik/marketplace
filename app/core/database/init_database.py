from typing import List
from psycopg2 import connect
from psycopg2.extensions import cursor as cursor

from auth.hashing_psw import get_password_hash
from core.settings import config


def create_role_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE role (
                role_id SERIAL PRIMARY KEY,
                role_name VARCHAR(255)
            );
        """
    )

def create_users_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE users (
                user_id SERIAL PRIMARY KEY,
                role_id INT DEFAULT 1,
                username VARCHAR(255),
                hashed_password VARCHAR(255),
                email VARCHAR(255) DEFAULT NULL,
                registration_date TIMESTAMP WITH TIME ZONE,
                photo_path VARCHAR(255) DEFAULT NULL,
                
                FOREIGN KEY (role_id) 
                REFERENCES role (role_id)
            );
            
            CREATE FUNCTION check_username()
            RETURNS TRIGGER AS $check_username$
                BEGIN
                    IF EXISTS (
                        SELECT username 
                        FROM users 
                        WHERE username = NEW.username
                    )
                    THEN 
                        RAISE EXCEPTION 'username is already taken';
                    END IF;
                RETURN NEW;
                END;
            $check_username$ LANGUAGE plpgsql;
            
            CREATE FUNCTION check_role()
            RETURNS TRIGGER AS $check_role$
                BEGIN
                    IF (
                        SELECT COUNT(user_id)
                        FROM users
                        WHERE role_id = (SELECT MAX(role_id) FROM role)
                    ) = 1 AND OLD.role_id = (SELECT MAX(role_id) FROM role)
                    THEN 
                        RAISE EXCEPTION 'deletion not available';
                    END IF;
                RETURN OLD;
                END;
            $check_role$ LANGUAGE plpgsql;
                
            CREATE TRIGGER update_username
            BEFORE UPDATE ON users
            FOR EACH ROW 
            WHEN (OLD.username IS DISTINCT FROM NEW.username)
            EXECUTE FUNCTION check_username();
            
            CREATE TRIGGER check_username
            BEFORE INSERT ON users
            FOR EACH ROW
            EXECUTE FUNCTION check_username();
            
            CREATE TRIGGER check_role
            BEFORE DELETE ON users
            FOR EACH ROW EXECUTE FUNCTION check_role();
        """
    )

def create_product_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE product (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(255),
                product_price INT,
                product_description TEXT,
                is_hidden BOOLEAN DEFAULT false,
                amount_orders INT DEFAULT 0,
                photo_path VARCHAR(255)
            );
        """
    )

def create_comment_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE comment (
                comment_id SERIAL PRIMARY KEY,
                user_id INT,
                product_id INT,
                comment_rating INT,
                comment_date TIMESTAMP WITH TIME ZONE,
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
            CREATE TABLE orders (
                order_id SERIAL PRIMARY KEY,
                user_id INT,
                product_id INT,
                date_start TIMESTAMP WITH TIME ZONE,
                date_end TIMESTAMP WITH TIME ZONE,
                delivery_address VARCHAR(255),
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id),
                
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id)
                ON DELETE CASCADE
            );
            
            CREATE FUNCTION check_product() 
            RETURNS TRIGGER AS $check_product$
                BEGIN
                    IF EXISTS (
                        SELECT product_id
                        FROM product 
                        WHERE product_id = NEW.product_id AND is_hidden = true
                    ) THEN
                        RAISE EXCEPTION 'product is hidden';
                    END IF;
                RETURN NEW;                 
                END;
            $check_product$ LANGUAGE plpgsql;
            
            CREATE FUNCTION increase_amount_orders() 
            RETURNS TRIGGER AS $increase_amount_orders$
                BEGIN 
                    UPDATE product
                    SET amount_orders = amount_orders + 1
                    WHERE product_id = NEW.product_id;
                RETURN NEW; 
                END; 
            $increase_amount_orders$ LANGUAGE plpgsql;
                
            CREATE TRIGGER check_product
            BEFORE INSERT ON orders
            FOR EACH ROW EXECUTE FUNCTION check_product(); 
            
            CREATE TRIGGER increase_amount_orders
            AFTER INSERT ON orders
            FOR EACH ROW EXECUTE FUNCTION increase_amount_orders();
        """
    )

def create_cart_item_table(sql_cursor: cursor) -> None:
    sql_cursor.execute(
        """
            CREATE TABLE cart_item (
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
                hashed_password,
                registration_date
            )    
            VALUES (
                (SELECT MAX(role_id) FROM role), %s, %s, NOW()
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
