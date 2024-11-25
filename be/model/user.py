import jwt
import time
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from be.model import error
from be.model import db_conn
from be.model.store import init_completed_event

def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded

def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded

class User(db_conn.DBConn):
    token_lifetime: int = 3600

    def __init__(self):
        init_completed_event.wait()
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            
            insert_user_sql = text("""
                INSERT INTO "user" (user_id, password, balance, token, terminal)
                VALUES (:user_id, :password, 0, :token, :terminal)
            """)
            
            self.session.execute(insert_user_sql, {
                "user_id": user_id,
                "password": password,
                "token": token,
                "terminal": terminal
            })
            self.session.commit()
            
        except SQLAlchemyError:
            self.session.rollback()
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        try:
            check_token_sql = text("""
                SELECT token FROM "user" WHERE user_id = :user_id
            """)
            result = self.session.execute(check_token_sql, {"user_id": user_id})
            user = result.fetchone()

            if user is None:
                return error.error_authorization_fail()

            if not user.token or not self.__check_token(user_id, user.token, token):
                return error.error_authorization_fail()

            return 200, "ok"
        except SQLAlchemyError:
            return error.error_authorization_fail()

    def check_password(self, user_id: str, password: str) -> (int, str):
        try:
            check_pwd_sql = text("""
                SELECT password FROM "user" WHERE user_id = :user_id
            """)
            result = self.session.execute(check_pwd_sql, {"user_id": user_id})
            user = result.fetchone()
            
            if user is None or user.password != password:
                return error.error_authorization_fail()
            return 200, "ok"
        except SQLAlchemyError:
            return error.error_authorization_fail()

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            
            update_token_sql = text("""
                UPDATE "user" 
                SET token = :token, terminal = :terminal
                WHERE user_id = :user_id
                RETURNING 1
            """)
            result = self.session.execute(update_token_sql, {
                "token": token,
                "terminal": terminal,
                "user_id": user_id
            })
            
            if not result.scalar():
                return error.error_authorization_fail() + ("",)
                
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation() + ("",)
        except BaseException as e:
            return error.error_and_message(530, str(e)) + ("",)
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            
            update_token_sql = text("""
                UPDATE "user" 
                SET token = :token, terminal = :terminal
                WHERE user_id = :user_id
                RETURNING 1
            """)
            result = self.session.execute(update_token_sql, {
                "token": dummy_token,
                "terminal": terminal,
                "user_id": user_id
            })
            
            if not result.scalar():
                return error.error_authorization_fail()
                
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            delete_user_sql = text("""
                DELETE FROM "user"
                WHERE user_id = :user_id
                RETURNING 1
            """)
            result = self.session.execute(delete_user_sql, {"user_id": user_id})
            
            if not result.scalar():
                return error.error_authorization_fail()
                
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            
            update_pwd_sql = text("""
                UPDATE "user"
                SET password = :new_password, token = :token, terminal = :terminal
                WHERE user_id = :user_id
                RETURNING 1
            """)
            result = self.session.execute(update_pwd_sql, {
                "new_password": new_password,
                "token": token,
                "terminal": terminal,
                "user_id": user_id
            })
            
            if not result.scalar():
                return error.error_authorization_fail()
                
            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            return error.error_database_operation()
        except BaseException as e:
            return error.error_and_message(530, str(e))
        return 200, "ok"