#!/usr/bin/env python3
from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
    tables = [row[0] for row in result]
    print("Tabelas criadas:")
    for table in tables:
        print(f"  - {table}")
