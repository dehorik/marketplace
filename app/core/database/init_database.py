from typing import List
from datetime import datetime, timezone
from psycopg2 import connect
from psycopg2.extensions import cursor

from auth.hashing_psw import get_password_hash
from core.settings import config


def create_role_table(cur: cursor) -> None:
    cur.execute(
        """
            CREATE TABLE role (
                role_id SERIAL PRIMARY KEY,
                role_name VARCHAR(255)
            );
        """
    )

def create_users_table(cur: cursor) -> None:
    cur.execute(
        """
            CREATE TABLE users (
                user_id SERIAL PRIMARY KEY,
                role_id INT DEFAULT 1,
                username VARCHAR(255),
                hashed_password VARCHAR(255),
                email VARCHAR(255) DEFAULT NULL,
                registration_date DATE,
                has_photo BOOLEAN DEFAULT FALSE,
                
                FOREIGN KEY (role_id) 
                REFERENCES role (role_id)
            );   
        """
    )

def create_product_table(cur: cursor) -> None:
    cur.execute(
        """
            CREATE TABLE product (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                price INT,
                description TEXT,
                amount_orders INT DEFAULT 0,
                has_photo BOOLEAN DEFAULT TRUE
            );
        """
    )

def create_comment_table(cur: cursor) -> None:
    cur.execute(
        """
            CREATE TABLE comment (
                comment_id SERIAL PRIMARY KEY,
                user_id INT,
                product_id INT,
                rating INT,
                creation_date DATE,
                text VARCHAR(255) DEFAULT NULL,
                has_photo BOOLEAN DEFAULT FALSE,
            
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id)
                ON DELETE SET NULL,
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id) 
                ON DELETE SET NULL
            );    
        """
    )

def create_orders_table(cur: cursor) -> None:
    cur.execute(
        """
            CREATE TABLE orders (
                order_id SERIAL PRIMARY KEY,
                user_id INT,
                product_id INT,
                product_name VARCHAR(255),
                product_price INT,
                date_start DATE,
                date_end DATE,
                delivery_address VARCHAR(255),
                has_photo BOOLEAN DEFAULT TRUE,
                
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id)
                ON DELETE SET NULL,
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id)
                ON DELETE SET NULL
            );
        """
    )

def create_archived_orders_table(cur: cursor) -> None:
    cur.execute(
        """
            CREATE TABLE archived_orders (
                archived_order_id SERIAL PRIMARY KEY,
                user_id INT,
                product_id INT,
                
                FOREIGN KEY (user_id)
                REFERENCES users (user_id)
                ON DELETE CASCADE,
                
                FOREIGN KEY (product_id)
                REFERENCES product (product_id)
                ON DELETE CASCADE
            );
        """
    )

def create_cart_item_table(cur: cursor) -> None:
    cur.execute(
        """
            CREATE TABLE cart_item (
                cart_item_id SERIAL PRIMARY KEY,
                user_id INT,
                product_id INT,
                
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id)
                ON DELETE CASCADE,
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id)
                ON DELETE CASCADE
            ); 
        """
    )

def create_triggers(cur: cursor) -> None:
    cur.execute(
        """
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
        
            CREATE FUNCTION check_superusers()
            RETURNS TRIGGER AS $check_superusers$
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
            $check_superusers$ LANGUAGE plpgsql;
            
            CREATE FUNCTION increase_amount_orders() 
            RETURNS TRIGGER AS $increase_amount_orders$
                BEGIN 
                    UPDATE product
                    SET amount_orders = amount_orders + 1
                    WHERE product_id = NEW.product_id;
                RETURN NEW; 
                END; 
            $increase_amount_orders$ LANGUAGE plpgsql;
            
            CREATE FUNCTION check_cart_item()
            RETURNS TRIGGER AS $check_cart_item$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM cart_item
                        WHERE user_id = NEW.user_id AND product_id = NEW.product_id 
                    )
                    THEN RAISE EXCEPTION 'such cart item alredy exists';
                    END IF;
                RETURN NEW;
                END;
            $check_cart_item$ LANGUAGE plpgsql;
            
            CREATE FUNCTION check_comment()
            RETURNS TRIGGER AS $check_comment$
                BEGIN
                    IF NOT EXISTS (
                        SELECT order_id
                        FROM orders
                        WHERE user_id = NEW.user_id AND product_id = NEW.product_id
                        UNION
                        SELECT archived_order_id
                        FROM archived_orders
                        WHERE user_id = NEW.user_id AND product_id = NEW.product_id
                    )
                    THEN RAISE EXCEPTION 'comment creation is unavailable';
                    END IF;
                RETURN NEW;
                END;
            $check_comment$ LANGUAGE plpgsql;
            
        
            CREATE TRIGGER user_creation
            BEFORE INSERT ON users
            FOR EACH ROW
            EXECUTE FUNCTION check_username();  
                
            CREATE TRIGGER user_update
            BEFORE UPDATE ON users
            FOR EACH ROW 
            WHEN (OLD.username IS DISTINCT FROM NEW.username)
            EXECUTE FUNCTION check_username();
        
            CREATE TRIGGER user_deletion
            BEFORE DELETE ON users
            FOR EACH ROW 
            EXECUTE FUNCTION check_superusers();
            
            CREATE TRIGGER order_creation
            AFTER INSERT ON orders
            FOR EACH ROW 
            EXECUTE FUNCTION increase_amount_orders();
            
            CREATE TRIGGER cart_item_creation
            BEFORE INSERT ON cart_item
            FOR EACH ROW 
            EXECUTE FUNCTION check_cart_item(); 
            
            CREATE TRIGGER comment_creation
            BEFORE INSERT ON comment
            FOR EACH ROW
            EXECUTE FUNCTION check_comment();
        """
    )

def create_roles(cur: cursor, role_names: List[List[str]]) -> None:
    cur.executemany(
        """
            INSERT INTO role (
                role_name
            )
            VALUES (%s);
        """,
        role_names
    )

def create_superuser_account(cur: cursor) -> None:
    password_hash = get_password_hash(config.SUPERUSER_PASSWORD)

    cur.execute(
        """
            INSERT INTO users (
                role_id,
                username,
                hashed_password,
                registration_date
            )    
            VALUES (
                (SELECT MAX(role_id) FROM role), %s, %s, %s
            );
        """,
        [
            config.SUPERUSER_USERNAME,
            password_hash,
            datetime.now(timezone.utc).date()
        ]
    )


def init_database() -> None:
    connection = connect(
        dbname=config.DATABASE_NAME,
        user=config.DATABASE_USER,
        password=config.DATABASE_USER_PASSWORD,
        host=config.DATABASE_HOST,
        port=config.DATABASE_PORT
    )
    cur = connection.cursor()

    create_role_table(cur)
    create_users_table(cur)
    create_product_table(cur)
    create_comment_table(cur)
    create_orders_table(cur)
    create_archived_orders_table(cur)
    create_cart_item_table(cur)
    create_triggers(cur)

    create_roles(
        cur,
        [
            ["Пользователь"],
            ["Администратор"],
            ["Суперпользователь"]
        ]
    )
    create_superuser_account(cur)

    connection.commit()
    cur.close()
    connection.close()


if __name__ == "__main__":
    init_database()
