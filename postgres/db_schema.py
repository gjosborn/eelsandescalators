#!/usr/bin/env python3
"""
Database schema creation script for Eels and Escalators game
Creates all necessary tables for the SpongeBob-themed board game
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import json
from datetime import datetime
import sys

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'eels_escalators')
}

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_CONFIG['database']}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Database '{DB_CONFIG['database']}' created successfully")
        else:
            print(f"ℹ️  Database '{DB_CONFIG['database']}' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

def get_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)

def create_tables():
    """Create all tables for the Eels and Escalators game"""
    
    # SQL statements for table creation
    sql_statements = [
        # Players table
        """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            display_name VARCHAR(100),
            avatar_url VARCHAR(255),
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
        """,
        
        # Rooms table
        """
        CREATE TABLE IF NOT EXISTS rooms (
            id SERIAL PRIMARY KEY,
            room_code VARCHAR(10) UNIQUE NOT NULL,
            room_name VARCHAR(100) NOT NULL,
            host_player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
            max_players INTEGER DEFAULT 4,
            current_players INTEGER DEFAULT 0,
            is_private BOOLEAN DEFAULT FALSE,
            room_password VARCHAR(255),
            status VARCHAR(20) DEFAULT 'waiting', -- waiting, playing, finished
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            finished_at TIMESTAMP
        )
        """,
        
        # Board configuration table
        """
        CREATE TABLE IF NOT EXISTS board_config (
            id SERIAL PRIMARY KEY,
            config_name VARCHAR(50) UNIQUE NOT NULL,
            board_size INTEGER DEFAULT 100,
            eels JSONB NOT NULL, -- Array of {start: number, end: number, name: string}
            escalators JSONB NOT NULL, -- Array of {start: number, end: number, name: string}
            theme_data JSONB, -- SpongeBob theme customizations
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Games table
        """
        CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
            board_config_id INTEGER REFERENCES board_config(id),
            status VARCHAR(20) DEFAULT 'active', -- active, completed, abandoned
            current_turn INTEGER DEFAULT 1,
            current_player_index INTEGER DEFAULT 0,
            player_order JSONB NOT NULL, -- Array of player IDs in turn order
            player_positions JSONB NOT NULL, -- {player_id: position} mapping
            winner_id INTEGER REFERENCES players(id),
            total_moves INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            game_duration_seconds INTEGER
        )
        """,
        
        # Game moves table (for history and replay)
        """
        CREATE TABLE IF NOT EXISTS game_moves (
            id SERIAL PRIMARY KEY,
            game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
            player_id INTEGER REFERENCES players(id),
            move_number INTEGER NOT NULL,
            dice_roll INTEGER NOT NULL,
            start_position INTEGER NOT NULL,
            end_position INTEGER NOT NULL,
            special_action VARCHAR(50), -- 'eel', 'escalator', 'normal', 'win'
            special_details JSONB, -- Additional info about eels/escalators hit
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Room participants table (many-to-many relationship)
        """
        CREATE TABLE IF NOT EXISTS room_participants (
            id SERIAL PRIMARY KEY,
            room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
            player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            left_at TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            player_color VARCHAR(20), -- 'yellow', 'pink', 'blue', 'green'
            UNIQUE(room_id, player_id)
        )
        """,
        
        # Player statistics table
        """
        CREATE TABLE IF NOT EXISTS player_statistics (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
            stat_date DATE DEFAULT CURRENT_DATE,
            games_played_today INTEGER DEFAULT 0,
            games_won_today INTEGER DEFAULT 0,
            total_moves_today INTEGER DEFAULT 0,
            average_game_duration INTEGER DEFAULT 0,
            eels_hit INTEGER DEFAULT 0,
            escalators_hit INTEGER DEFAULT 0,
            UNIQUE(player_id, stat_date)
        )
        """
    ]
    
    # Index creation statements
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_players_username ON players(username)",
        "CREATE INDEX IF NOT EXISTS idx_players_email ON players(email)",
        "CREATE INDEX IF NOT EXISTS idx_rooms_code ON rooms(room_code)",
        "CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status)",
        "CREATE INDEX IF NOT EXISTS idx_games_room_id ON games(room_id)",
        "CREATE INDEX IF NOT EXISTS idx_games_status ON games(status)",
        "CREATE INDEX IF NOT EXISTS idx_game_moves_game_id ON game_moves(game_id)",
        "CREATE INDEX IF NOT EXISTS idx_game_moves_player_id ON game_moves(player_id)",
        "CREATE INDEX IF NOT EXISTS idx_room_participants_room_id ON room_participants(room_id)",
        "CREATE INDEX IF NOT EXISTS idx_room_participants_player_id ON room_participants(player_id)",
        "CREATE INDEX IF NOT EXISTS idx_player_statistics_player_id ON player_statistics(player_id)",
        "CREATE INDEX IF NOT EXISTS idx_player_statistics_date ON player_statistics(stat_date)"
    ]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create tables
        print("🏗️  Creating tables...")
        for i, statement in enumerate(sql_statements, 1):
            cursor.execute(statement)
            table_name = statement.split("CREATE TABLE IF NOT EXISTS ")[1].split(" (")[0]
            print(f"   {i}. Created table: {table_name}")
        
        # Create indexes
        print("\n📊 Creating indexes...")
        for i, statement in enumerate(index_statements, 1):
            cursor.execute(statement)
            index_name = statement.split("CREATE INDEX IF NOT EXISTS ")[1].split(" ON")[0]
            print(f"   {i}. Created index: {index_name}")
        
        # Insert default board configuration
        print("\n🎮 Inserting default board configuration...")
        default_board_sql = """
        INSERT INTO board_config (config_name, board_size, eels, escalators, theme_data, is_default)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (config_name) DO NOTHING
        """
        
        # SpongeBob themed eels and escalators
        eels_data = [
            {"start": 16, "end": 6, "name": "Giant Eel's Mouth"},
            {"start": 47, "end": 26, "name": "Slippery Kelp Forest"},
            {"start": 49, "end": 11, "name": "Moray Eel's Lair"},
            {"start": 56, "end": 53, "name": "Electric Eel Shock"},
            {"start": 62, "end": 19, "name": "Sea Snake Slide"},
            {"start": 64, "end": 60, "name": "Jellyfish Sting"},
            {"start": 87, "end": 24, "name": "King Neptune's Wrath"},
            {"start": 93, "end": 73, "name": "Conger Eel Canyon"},
            {"start": 95, "end": 75, "name": "Plankton's Trap"},
            {"start": 98, "end": 78, "name": "The Abyss"}
        ]
        
        escalators_data = [
            {"start": 1, "end": 38, "name": "Krabby Patty Express"},
            {"start": 4, "end": 14, "name": "Bubble Elevator"},
            {"start": 9, "end": 21, "name": "SpongeBob's Spatula Lift"},
            {"start": 21, "end": 42, "name": "Gary's Shell Escalator"},
            {"start": 28, "end": 84, "name": "Patrick's Rock Rocket"},
            {"start": 36, "end": 44, "name": "Sandy's Acorn Lift"},
            {"start": 51, "end": 67, "name": "Squidward's Clarinet Climb"},
            {"start": 71, "end": 91, "name": "Mr. Krabs' Money Tower"},
            {"start": 80, "end": 100, "name": "Bikini Bottom Express"}
        ]
        
        theme_data = {
            "background_color": "#87CEEB",
            "water_effects": True,
            "bubble_animations": True,
            "character_tokens": ["spongebob", "patrick", "squidward", "sandy"],
            "sound_effects": {
                "eel": "eel_hiss.mp3",
                "escalator": "bubble_pop.mp3",
                "dice_roll": "water_splash.mp3",
                "win": "krabby_patty_jingle.mp3"
            }
        }
        
        cursor.execute(default_board_sql, (
            "spongebob_classic",
            100,
            json.dumps(eels_data),
            json.dumps(escalators_data),
            json.dumps(theme_data),
            True
        ))
        
        print("   ✅ Default SpongeBob board configuration added")
        
        # Commit all changes
        conn.commit()
        print(f"\n🎉 Database schema created successfully!")
        print(f"📊 Total tables created: {len(sql_statements)}")
        print(f"📈 Total indexes created: {len(index_statements)}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def verify_schema():
    """Verify that all tables were created successfully"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n✅ Schema verification complete!")
        print(f"📋 Tables found ({len(tables)}):")
        for table in tables:
            print(f"   • {table[0]}")
            
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function to create the database schema"""
    print("🐙 Eels and Escalators Database Setup")
    print("=" * 40)
    
    # Create database
    create_database()
    
    # Create tables and indexes
    create_tables()
    
    # Verify schema
    verify_schema()
    
    print(f"\n🎮 Ready to play Eels and Escalators!")
    print(f"🔗 Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

if __name__ == "__main__":
    main()