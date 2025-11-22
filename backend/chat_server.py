"""
WebSocket Chat Server for ColdVault Community
Handles real-time messaging between multiple users
"""

import asyncio
import json
from datetime import datetime
from typing import Set, Dict
from fastapi import WebSocket, WebSocketDisconnect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Store active connections: {websocket: username}
        self.active_connections: Dict[WebSocket, str] = {}
        # Message history (last 50 messages)
        self.message_history = []
        
    async def connect(self, websocket: WebSocket, username: str):
        """Accept new connection and broadcast join message"""
        await websocket.accept()
        self.active_connections[websocket] = username
        
        # Send message history to new user
        if self.message_history:
            await websocket.send_json({
                "type": "history",
                "messages": self.message_history
            })
        
        # Broadcast join message
        join_message = {
            "type": "system",
            "text": f"{username} joined the community!",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        await self.broadcast(join_message)
        
        # Send updated user list
        await self.broadcast_user_list()
        
        logger.info(f"User {username} connected. Total users: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection and broadcast leave message"""
        if websocket in self.active_connections:
            username = self.active_connections[websocket]
            del self.active_connections[websocket]
            logger.info(f"User {username} disconnected. Total users: {len(self.active_connections)}")
            return username
        return None
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific user"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        # Add to history if it's a user message
        if message.get("type") in ["message", "system"]:
            self.message_history.append(message)
            # Keep only last 50 messages
            if len(self.message_history) > 50:
                self.message_history = self.message_history[-50:]
        
        # Send to all connected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to user: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_user_list(self):
        """Send updated user list to all clients"""
        user_list = list(self.active_connections.values())
        await self.broadcast({
            "type": "user_list",
            "users": user_list
        })
    
    def get_online_users(self) -> list:
        """Get list of online usernames"""
        return list(self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()


async def handle_chat_websocket(websocket: WebSocket):
    """Handle WebSocket connection for chat"""
    username = None
    
    try:
        # Accept WebSocket connection first
        await websocket.accept()
        
        # Wait for initial message with username
        data = await websocket.receive_json()
        
        if data.get("type") == "join":
            username = data.get("username", "Anonymous")
            
            # Check if username is already taken
            if username in manager.get_online_users():
                await websocket.send_json({
                    "type": "error",
                    "message": "Username already taken"
                })
                await websocket.close()
                return
            
            # Add user to connections (connection already accepted)
            manager.active_connections[websocket] = username
            
            # Send message history to new user
            if manager.message_history:
                await websocket.send_json({
                    "type": "history",
                    "messages": manager.message_history
                })
            
            # Broadcast join message
            join_message = {
                "type": "system",
                "text": f"{username} joined the community!",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            await manager.broadcast(join_message)
            
            # Send updated user list
            await manager.broadcast_user_list()
            
            logger.info(f"User {username} connected. Total users: {len(manager.active_connections)}")
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_json()
                    
                    if data.get("type") == "message":
                        # Broadcast user message
                        message = {
                            "type": "message",
                            "user": username,
                            "text": data.get("text", ""),
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        }
                        await manager.broadcast(message)
                        
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    break
                    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected during setup")
    except Exception as e:
        logger.error(f"Error in chat websocket: {e}")
    finally:
        # Cleanup on disconnect
        if username:
            left_username = manager.disconnect(websocket)
            if left_username:
                # Broadcast leave message
                leave_message = {
                    "type": "system",
                    "text": f"{left_username} left the community",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                await manager.broadcast(leave_message)
                await manager.broadcast_user_list()
