import psycopg
from psycopg.rows import dict_row


class UserRepository():
    def __init__(self, db_url):
        self.db_url = db_url


    def get_connection(self):
        return psycopg.connect(self.db_url)


    def get_content(self):
        with self.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM users")
                return [dict(row) for row in cur]

    def find(self, id):
        with self.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def destroy(self, id):
        with self.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("DELETE FROM users WHERE id = %s", (id,))
            conn.commit()

    def save(self, user):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                name = user['name']
                email = user['email']
                if not user.get('id'):
                    cur.execute(
                        """INSERT INTO users (name, email)
                            VALUES (%s, %s)                            
                            RETURNING id""", (name, email)
                    )
                    row = cur.fetchone()
                    if row is not None:
                        user['id'] = row[0]
                    else:
                        raise RuntimeError("Database failed to return generated ID")
                else:
                    cur.execute("""UPDATE users 
                                SET name = %s, email = %s                            
                                WHERE id = %s""", (name, email, user['id'],))
            conn.commit()
        return user['id']