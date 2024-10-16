"""Database creation

Revision ID: 147a0842a462
Revises: 
Create Date: 2024-09-25 11:58:29.327771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '147a0842a462'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('students_courses_course_id_fkey', 'students_courses', type_='foreignkey')
    op.drop_constraint('students_courses_student_id_fkey', 'students_courses', type_='foreignkey')
    op.drop_constraint('students_group_id_fkey', 'students', type_='foreignkey')

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('last_activity_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('students_courses')
    op.drop_table('courses')
    op.drop_table('groups')
    op.drop_table('students')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('students',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('students_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], name='students_group_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='students_pkey'),
    sa.UniqueConstraint('first_name', 'last_name', name='students_first_name_last_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('groups',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('groups_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='groups_pkey'),
    sa.UniqueConstraint('name', name='groups_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('courses',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('courses_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='courses_pkey'),
    sa.UniqueConstraint('name', name='courses_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('students_courses',
    sa.Column('student_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('course_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name='students_courses_course_id_fkey'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name='students_courses_student_id_fkey')
    )
    op.drop_table('users')
    # ### end Alembic commands ###
