from sqlmodel import Session, select

from ..models import AccessToken


class AccessTokenDatabase:
    def __init__(self, session):
        self.session: Session = session

    async def create(self, access_token: AccessToken):
        with self.session as session:
            session.add(access_token)
            session.commit()
            session.refresh(access_token)
            return access_token

    async def get_by_token(self, token: str):
        with self.session as session:
            statement = select(AccessToken).where(AccessToken.token == token)
            return session.execute(statement).scalar_one_or_none()

    async def delete(self, token: str):
        with self.session as session:
            statement = select(AccessToken).where(AccessToken.token == token)
            access_token = session.execute(statement).scalar_one_or_none()
            if access_token:
                session.delete(access_token)
                session.commit()
