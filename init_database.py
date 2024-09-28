import psycopg2

from app.core.settings import config


def init_database():
    connection = psycopg2.connect(
        dbname=config.DATABASE_NAME,
        user=config.DATABASE_USER,
        password=config.DATABASE_USER_PASSWORD,
        host=config.DATABASE_HOST,
        port=config.DATABASE_PORT
    )
    cursor = connection.cursor()

    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS role (
                role_id SERIAL PRIMARY KEY,
                role_name VARCHAR(255)
            );
            
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                role_id INT DEFAULT 1,
                user_name VARCHAR(255),
                user_hashed_password VARCHAR(255),
                user_email VARCHAR(255) DEFAULT NULL,
                user_photo_path VARCHAR(255) DEFAULT NULL,
                
                FOREIGN KEY (role_id) 
                REFERENCES role (role_id)
            );
            
            CREATE TABLE IF NOT EXISTS product (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(255),
                product_price INT,
                product_description TEXT,
                is_hidden BOOLEAN DEFAULT false,
                product_photo_path VARCHAR(255)
            );
            
            CREATE TABLE IF NOT EXISTS comment (
                comment_id SERIAL PRIMARY KEY,
                user_id INT,
                product_id INT,
                comment_rating INT,
                comment_date DATE,
                comment_text VARCHAR(255) DEFAULT NULL,
                comment_photo_path VARCHAR(255) DEFAULT NULL,
            
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id),
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id) 
            );
            
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                product_id INT,
                user_id INT,
                order_date_start DATE,
                order_date_end DATE,
                order_address VARCHAR(255),
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id),
                
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id)
            );
            
            CREATE TABLE IF NOT EXISTS shopping_bag_item (
                shopping_bag_item_id SERIAL PRIMARY KEY,
                product_id INT,
                user_id INT,
                
                FOREIGN KEY (product_id) 
                REFERENCES product (product_id),
                
                FOREIGN KEY (user_id) 
                REFERENCES users (user_id)
            ); 
        """
    )

    cursor.execute(
        """
            INSERT INTO role 
                (role_name)
            VALUES
                ('user'),
                ('admin'),
                ('owner');
        """
    )

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    init_database()
