#!/usr/bin/env python3
"""
FastAPI Backend for Eels and Escalators Game
SpongeBob-themed board game with real-time multiplayer support
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import jwt
import bcrypt
import os
import random
import string
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'dbname': os.getenv('DB_NAME', 'eels_escalators')  # Changed from 'database' to 'dbname'
}

# Database connection
def get_db():
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class RoomCreate(BaseModel):
    room_name: str
    max_players: int = 4
    is_private: bool = False
    room_password: Optional[str] = None

class RoomJoin(BaseModel):
    room_code: str
    password: Optional[str] = None

class GameMove(BaseModel):
    dice_roll: int

class Player(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    games_played: int
    games_won: int

class Room(BaseModel):
    id: int
    room_code: str
    room_name: str
    host_player_id: int
    max_players: int
    current_players: int
    status: str
    is_private: bool

class GameState(BaseModel):
    id: int
    room_id: int
    status: str
    current_turn: int
    current_player_index: int
    player_order: List[int]
    player_positions: Dict[str, int]
    winner_id: Optional[int]

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_code: str):
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = []
        self.active_connections[room_code].append(websocket)
    
    def disconnect(self, websocket: WebSocket, room_code: str):
        if room_code in self.active_connections:
            self.active_connections[room_code].remove(websocket)
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_room(self, message: str, room_code: str):
        if room_code in self.active_connections:
            for connection in self.active_connections[room_code]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

# FastAPI App
app = FastAPI(title="Eels and Escalators API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Game Logic Functions
def get_board_config(conn, config_id: int = 1):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM board_config WHERE id = %s", (config_id,))
    return cursor.fetchone()

def calculate_new_position(position: int, dice_roll: int, eels: list, escalators: list) -> tuple:
    """Calculate new position after dice roll and check for eels/escalators"""
    new_position = min(position + dice_roll, 100)
    special_action = "normal"
    special_details = None
    
    # Check for escalators (go up)
    for escalator in escalators:
        if escalator["start"] == new_position:
            new_position = escalator["end"]
            special_action = "escalator"
            special_details = escalator
            break
    
    # Check for eels (go down)
    for eel in eels:
        if eel["start"] == new_position:
            new_position = eel["end"]
            special_action = "eel"
            special_details = eel
            break
    
    # Check for win
    if new_position >= 100:
        new_position = 100
        special_action = "win"
    
    return new_position, special_action, special_details

# API Endpoints

@app.get("/")
async def root():
    return {"message": "🐙 Eels and Escalators API - Ready to play!"}

# Authentication Endpoints
@app.post("/auth/register")
async def register(user: UserRegister, conn=Depends(get_db)):
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM players WHERE username = %s OR email = %s", 
                  (user.username, user.email))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user
    cursor.execute("""
        INSERT INTO players (username, email, password_hash, display_name)
        VALUES (%s, %s, %s, %s) RETURNING id
    """, (user.username, user.email, password_hash, user.display_name or user.username))
    
    user_id = cursor.fetchone()['id']
    conn.commit()
    
    # Create token
    token = create_access_token(data={"sub": user_id})
    
    return {"access_token": token, "token_type": "bearer", "user_id": user_id}

@app.post("/auth/login")
async def login(user: UserLogin, conn=Depends(get_db)):
    cursor = conn.cursor()
    
    # Get user
    cursor.execute("SELECT id, password_hash FROM players WHERE username = %s", (user.username,))
    db_user = cursor.fetchone()
    
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_access_token(data={"sub": db_user['id']})
    
    return {"access_token": token, "token_type": "bearer", "user_id": db_user['id']}

@app.get("/auth/me", response_model=Player)
async def get_current_user(user_id: int = Depends(verify_token), conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return Player(**user)

# Room Management Endpoints
@app.post("/rooms", response_model=Room)
async def create_room(room_data: RoomCreate, user_id: int = Depends(verify_token), conn=Depends(get_db)):
    cursor = conn.cursor()
    
    room_code = generate_room_code()
    password_hash = None
    if room_data.room_password:
        password_hash = bcrypt.hashpw(room_data.room_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create room
    cursor.execute("""
        INSERT INTO rooms (room_code, room_name, host_player_id, max_players, is_private, room_password, current_players)
        VALUES (%s, %s, %s, %s, %s, %s, 1) RETURNING *
    """, (room_code, room_data.room_name, user_id, room_data.max_players, room_data.is_private, password_hash))
    
    room = cursor.fetchone()
    
    # Add host as participant
    cursor.execute("""
        INSERT INTO room_participants (room_id, player_id, player_color)
        VALUES (%s, %s, %s)
    """, (room['id'], user_id, 'yellow'))
    
    conn.commit()
    
    return Room(**room)

@app.get("/rooms", response_model=List[Room])
async def list_rooms(conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM rooms 
        WHERE status = 'waiting' AND is_private = FALSE 
        ORDER BY created_at DESC
    """)
    rooms = cursor.fetchall()
    
    return [Room(**room) for room in rooms]

@app.post("/rooms/join")
async def join_room(room_data: RoomJoin, user_id: int = Depends(verify_token), conn=Depends(get_db)):
    cursor = conn.cursor()
    
    # Get room
    cursor.execute("SELECT * FROM rooms WHERE room_code = %s", (room_data.room_code,))
    room = cursor.fetchone()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room['status'] != 'waiting':
        raise HTTPException(status_code=400, detail="Room is not accepting players")
    
    if room['current_players'] >= room['max_players']:
        raise HTTPException(status_code=400, detail="Room is full")
    
    # Check password if private
    if room['is_private'] and room['room_password']:
        if not room_data.password or not bcrypt.checkpw(room_data.password.encode('utf-8'), room['room_password'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid room password")
    
    # Check if already in room
    cursor.execute("SELECT id FROM room_participants WHERE room_id = %s AND player_id = %s AND is_active = TRUE", 
                  (room['id'], user_id))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Already in this room")
    
    # Available colors
    colors = ['yellow', 'pink', 'blue', 'green']
    cursor.execute("SELECT player_color FROM room_participants WHERE room_id = %s AND is_active = TRUE", (room['id'],))
    used_colors = [row['player_color'] for row in cursor.fetchall()]
    available_colors = [color for color in colors if color not in used_colors]
    
    if not available_colors:
        raise HTTPException(status_code=400, detail="No available player colors")
    
    # Join room
    cursor.execute("""
        INSERT INTO room_participants (room_id, player_id, player_color)
        VALUES (%s, %s, %s)
    """, (room['id'], user_id, available_colors[0]))
    
    # Update room player count
    cursor.execute("""
        UPDATE rooms SET current_players = current_players + 1
        WHERE id = %s
    """, (room['id'],))
    
    conn.commit()
    
    # Broadcast to room
    await manager.broadcast_to_room(json.dumps({
        "type": "player_joined",
        "player_id": user_id,
        "color": available_colors[0]
    }), room_data.room_code)
    
    return {"message": "Joined room successfully", "color": available_colors[0]}

@app.get("/rooms/{room_code}/players")
async def get_room_players(room_code: str, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.username, p.display_name, rp.player_color, rp.joined_at
        FROM room_participants rp
        JOIN players p ON rp.player_id = p.id
        JOIN rooms r ON rp.room_id = r.id
        WHERE r.room_code = %s AND rp.is_active = TRUE
        ORDER BY rp.joined_at
    """, (room_code,))
    
    players = cursor.fetchall()
    return [dict(player) for player in players]

# Game Endpoints
@app.post("/rooms/{room_code}/start")
async def start_game(room_code: str, user_id: int = Depends(verify_token), conn=Depends(get_db)):
    cursor = conn.cursor()
    
    # Get room and verify host
    cursor.execute("SELECT * FROM rooms WHERE room_code = %s", (room_code,))
    room = cursor.fetchone()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room['host_player_id'] != user_id:
        raise HTTPException(status_code=403, detail="Only host can start the game")
    
    if room['current_players'] < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 players to start")
    
    # Get players in room
    cursor.execute("""
        SELECT player_id FROM room_participants 
        WHERE room_id = %s AND is_active = TRUE 
        ORDER BY joined_at
    """, (room['id'],))
    
    player_ids = [row['player_id'] for row in cursor.fetchall()]
    
    # Initialize player positions
    player_positions = {str(pid): 0 for pid in player_ids}
    
    # Create game
    cursor.execute("""
        INSERT INTO games (room_id, board_config_id, player_order, player_positions)
        VALUES (%s, %s, %s, %s) RETURNING *
    """, (room['id'], 1, json.dumps(player_ids), json.dumps(player_positions)))
    
    game = cursor.fetchone()
    
    # Update room status
    cursor.execute("""
        UPDATE rooms SET status = 'playing', started_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (room['id'],))
    
    conn.commit()
    
    # Broadcast game start
    await manager.broadcast_to_room(json.dumps({
        "type": "game_started",
        "game_id": game['id'],
        "player_order": player_ids,
        "player_positions": player_positions
    }), room_code)
    
    return {"message": "Game started", "game_id": game['id']}

@app.get("/games/{game_id}/state", response_model=GameState)
async def get_game_state(game_id: int, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
    game = cursor.fetchone()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return GameState(**game)

@app.post("/games/{game_id}/move")
async def make_move(game_id: int, move: GameMove, user_id: int = Depends(verify_token), conn=Depends(get_db)):
    cursor = conn.cursor()
    
    # Get game
    cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
    game = cursor.fetchone()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game['status'] != 'active':
        raise HTTPException(status_code=400, detail="Game is not active")
    
    # Check if it's player's turn
    player_order = game['player_order']
    current_player = player_order[game['current_player_index']]
    
    if current_player != user_id:
        raise HTTPException(status_code=400, detail="Not your turn")
    
    # Get board configuration
    board_config = get_board_config(conn, game['board_config_id'])
    eels = board_config['eels']
    escalators = board_config['escalators']
    
    # Calculate move
    player_positions = game['player_positions']
    current_position = player_positions[str(user_id)]
    new_position, special_action, special_details = calculate_new_position(
        current_position, move.dice_roll, eels, escalators
    )
    
    # Update player position
    player_positions[str(user_id)] = new_position
    
    # Record move
    cursor.execute("""
        INSERT INTO game_moves (game_id, player_id, move_number, dice_roll, start_position, end_position, special_action, special_details)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (game_id, user_id, game['total_moves'] + 1, move.dice_roll, current_position, new_position, special_action, json.dumps(special_details)))
    
    # Check for win
    winner_id = None
    game_status = 'active'
    if new_position >= 100:
        winner_id = user_id
        game_status = 'completed'
    
    # Update game
    next_player_index = (game['current_player_index'] + 1) % len(player_order)
    cursor.execute("""
        UPDATE games SET 
            player_positions = %s,
            current_player_index = %s,
            current_turn = current_turn + 1,
            total_moves = total_moves + 1,
            winner_id = %s,
            status = %s,
            finished_at = CASE WHEN %s = 'completed' THEN CURRENT_TIMESTAMP ELSE finished_at END
        WHERE id = %s
    """, (json.dumps(player_positions), next_player_index, winner_id, game_status, game_status, game_id))
    
    # Update player stats if game completed
    if winner_id:
        cursor.execute("UPDATE players SET games_won = games_won + 1 WHERE id = %s", (winner_id,))
        cursor.execute("""
            UPDATE players SET games_played = games_played + 1 
            WHERE id = ANY(%s)
        """, (player_order,))
    
    conn.commit()
    
    # Get room code for broadcast
    cursor.execute("SELECT room_code FROM rooms WHERE id = %s", (game['room_id'],))
    room_code = cursor.fetchone()['room_code']
    
    # Broadcast move
    await manager.broadcast_to_room(json.dumps({
        "type": "move_made",
        "player_id": user_id,
        "dice_roll": move.dice_roll,
        "start_position": current_position,
        "end_position": new_position,
        "special_action": special_action,
        "special_details": special_details,
        "player_positions": player_positions,
        "next_player": player_order[next_player_index] if game_status == 'active' else None,
        "winner_id": winner_id,
        "game_status": game_status
    }), room_code)
    
    return {
        "new_position": new_position,
        "special_action": special_action,
        "special_details": special_details,
        "winner": winner_id == user_id,
        "game_status": game_status
    }

@app.get("/games/{game_id}/history")
async def get_game_history(game_id: int, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gm.*, p.username 
        FROM game_moves gm
        JOIN players p ON gm.player_id = p.id
        WHERE gm.game_id = %s
        ORDER BY gm.move_number
    """, (game_id,))
    
    moves = cursor.fetchall()
    return [dict(move) for move in moves]

# WebSocket Endpoint
@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    await manager.connect(websocket, room_code)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo received messages (can be extended for chat, etc.)
            await manager.broadcast_to_room(data, room_code)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)

# Statistics Endpoints
@app.get("/players/{player_id}/stats")
async def get_player_stats(player_id: int, conn=Depends(get_db)):
    cursor = conn.cursor()
    
    # Basic stats
    cursor.execute("SELECT games_played, games_won, total_score FROM players WHERE id = %s", (player_id,))
    basic_stats = cursor.fetchone()
    
    # Recent games
    cursor.execute("""
        SELECT g.id, g.started_at, g.finished_at, g.winner_id, r.room_name
        FROM games g
        JOIN rooms r ON g.room_id = r.id
        JOIN room_participants rp ON r.id = rp.room_id
        WHERE rp.player_id = %s AND g.status = 'completed'
        ORDER BY g.finished_at DESC
        LIMIT 10
    """, (player_id,))
    recent_games = cursor.fetchall()
    
    return {
        "basic_stats": dict(basic_stats) if basic_stats else {},
        "recent_games": [dict(game) for game in recent_games]
    }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)