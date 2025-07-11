"""posts

Revision ID: 3f33f7583404
Revises: 96d325c199d0
Create Date: 2025-07-09 17:12:43.962472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f33f7583404'
down_revision: Union[str, Sequence[str], None] = '96d325c199d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('posts',
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('like_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('flight_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_flight_id'), 'posts', ['flight_id'], unique=False)
    op.create_index(op.f('ix_posts_user_id'), 'posts', ['user_id'], unique=False)
    op.create_table('comments',
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('post_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_post_id'), 'comments', ['post_id'], unique=False)
    op.create_index(op.f('ix_comments_user_id'), 'comments', ['user_id'], unique=False)
    op.create_table('post_likes',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('post_id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'post_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_likes')
    op.drop_index(op.f('ix_comments_user_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_post_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_posts_user_id'), table_name='posts')
    op.drop_index(op.f('ix_posts_flight_id'), table_name='posts')
    op.drop_table('posts')
    # ### end Alembic commands ###
