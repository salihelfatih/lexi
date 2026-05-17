"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('format', sa.Enum('PDF', 'DOCX', 'JPEG', 'PNG', name='documentformat'), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('storage_mode', sa.Enum('EPHEMERAL', 'PERSISTENT', name='storagemode'), nullable=False),
        sa.Column('s3_key', sa.String(length=512), nullable=True),
        sa.Column('document_type', sa.Enum('ONTARIO_RESIDENTIAL_LEASE', 'UNKNOWN', name='documenttype'), nullable=True),
        sa.Column('classification_confidence', sa.Float(), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('extraction_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)

    # Create consent_records table
    op.create_table(
        'consent_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('processing_consent', sa.Boolean(), nullable=False),
        sa.Column('processing_consent_at', sa.DateTime(), nullable=True),
        sa.Column('storage_consent', sa.Boolean(), nullable=False),
        sa.Column('storage_consent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )

    # Create job_statuses table
    op.create_table(
        'job_statuses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'UPLOADING', 'EXTRACTING_TEXT', 'CLASSIFYING', 'EXTRACTING_CLAUSES', 'COMPLETE', 'FAILED', name='jobstatusenum'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )

    # Create document_metadata table
    op.create_table(
        'document_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lease_start_date', sa.String(length=50), nullable=True),
        sa.Column('lease_start_date_confidence', sa.Float(), nullable=True),
        sa.Column('lease_end_date', sa.String(length=50), nullable=True),
        sa.Column('lease_end_date_confidence', sa.Float(), nullable=True),
        sa.Column('tenant_names', sa.Text(), nullable=True),
        sa.Column('landlord_names', sa.Text(), nullable=True),
        sa.Column('property_address', sa.Text(), nullable=True),
        sa.Column('monthly_rent', sa.String(length=50), nullable=True),
        sa.Column('monthly_rent_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )

    # Create clauses table
    op.create_table(
        'clauses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clause_number', sa.String(length=50), nullable=False),
        sa.Column('clause_type', sa.Enum('TERMINATION', 'FEES', 'ACCESS', 'MAINTENANCE', 'UTILITIES', 'PETS', 'SUBLETTING', 'OTHER', name='clausetype'), nullable=False),
        sa.Column('clause_text', sa.Text(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('indentation_level', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clauses_document_id'), 'clauses', ['document_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_clauses_document_id'), table_name='clauses')
    op.drop_table('clauses')
    op.drop_table('document_metadata')
    op.drop_table('job_statuses')
    op.drop_table('consent_records')
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_table('documents')
