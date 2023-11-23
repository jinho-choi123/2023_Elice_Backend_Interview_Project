from sqlalchemy.orm import Session

from . import database, models

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user):
    test_salt = '1234'
    test_pwd_hash = '1234'
    test_boards = []
    db_user = models.User(fullName = "mango", 
                          email = "hello@hello.com", 
                          password_salt = test_salt,
                          password_hash = test_pwd_hash,
                          boards = test_boards)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
