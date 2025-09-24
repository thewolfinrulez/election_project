from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Integer, text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Candidates(Base):
    __tablename__ = "t_candidates"

    c_id = Column(Integer, primary_key=True)
    c_active = Column(Boolean, nullable=False, default=True)
    c_name = Column(String(255), unique=False, nullable=False)
    c_created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))


class Students(Base):
    __tablename__ = "t_students"

    s_id = Column(Integer, primary_key=True)
    s_code = Column(String(255), unique=True, nullable=False)
    s_name = Column(String(255), unique=False, nullable=False)
    s_chat_id = Column(String(255), unique=True, nullable=True)
    s_active = Column(Boolean, nullable=False, default=True)
    s_specialization = Column(String(255), unique=False, nullable=True)
    s_created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))


class Votes(Base):
    __tablename__ = "t_votes"

    v_candidate_id = Column(ForeignKey('t_candidates.c_id'), nullable=False, unique=False)
    v_student_id = Column(ForeignKey('t_students.s_id'), nullable=False, unique=True, primary_key=True)
    v_created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))
