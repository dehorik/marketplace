import psycopg2

from app.core.config_reader import config


def init_database():
    connection = psycopg2.connect(
        dbname=config.getenv("DATABASE"),
        user=config.getenv("DATABASE_USER"),
        password=config.getenv("DATABASE_USER_PASSWORD"),
        host=config.getenv("DATABASE_HOST"),
        port=config.getenv("DATABASE_PORT")
    )
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE role (
            role_id SERIAL PRIMARY KEY,
            role_name VARCHAR(255)
        );
        
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            role_id INT DEFAULT 1,
            user_name VARCHAR(255),
            user_password VARCHAR(255),
            user_email VARCHAR(255) DEFAULT NULL,
            user_photo_path VARCHAR(255) DEFAULT NULL,
            
            FOREIGN KEY (role_id) REFERENCES role (role_id) ON UPDATE CASCADE
        );
        
        CREATE TABLE product (
            product_id SERIAL PRIMARY KEY,
            user_id INT,
            product_name VARCHAR(255),
            product_price DECIMAL(12, 2),
            product_description TEXT,
            product_photo_path VARCHAR(255),
            
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
        );
        
        CREATE TABLE comment (
            comment_id SERIAL PRIMARY KEY,
            user_id INT,
            product_id INT,
            comment_date DATE,
            comment_text VARCHAR(255) DEFAULT NULL,
            comment_rating INT,
            comment_photo_path VARCHAR(255) DEFAULT NULL,
        
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
            FOREIGN KEY (product_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
        
        CREATE TABLE order_status (
            order_status_id SERIAL PRIMARY KEY,
            order_status_name VARCHAR(255)
        );
        
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            product_id INT,
            user_id INT,
            order_status_id INT,
            date_start DATE,
            date_end DATE,
            order_address VARCHAR(255),
            product_name VARCHAR(255),
            product_photo VARCHAR(255),
            product_price NUMERIC(12, 2),
            
            FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY (order_status_id) REFERENCES order_status (order_status_id) ON UPDATE CASCADE
        );
        
        CREATE TABLE orders_archive (
            order_archive_id SERIAL PRIMARY KEY,
            product_id INT,
            user_id INT,
            order_status_id INT,
            date_start DATE,
            date_end DATE,
            order_address VARCHAR(255),
            product_name VARCHAR(255),
            product_photo VARCHAR(255),
            product_price NUMERIC(12, 2),
            
            FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY (order_status_id) REFERENCES order_status (order_status_id) ON UPDATE CASCADE
        );
        
        CREATE TABLE shopping_bag (
            shopping_bag_id SERIAL PRIMARY KEY,
            product_id INT,
            user_id INT,
            
            FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
        
        
        # database setup
        INSERT INTO order_status
            (order_status_name)
        VALUES
            ('В доставке'),
            ('Доставлено'),
            ('Отменено');
        
        INSERT INTO role 
            (role_name)
        VALUES
            ('user'),
            ('admin'),
            ('owner');
            
        
        # auth
        CREATE TABLE session (
            session_id SERIAL PRIMARY KEY,
            session_key VARCHAR(255),
            user_id INT,
            
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
        """
    )

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    init_database()
