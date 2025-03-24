import asyncio
import websockets
import pyperclip
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set of connected clients
clients = set()

#async function to handle client connections, async can perform websocker operations without blocking the main thread
async def handle_client(websocket):
    global clients
    try:
        logger.info(f"New client connected from {websocket.remote_address}")
        clients.add(websocket)
        
        async for message in websocket:
            try:
                logger.debug(f"Received message: {message}")
                pyperclip.copy(message)  # Copy received text to clipboard
                for client in clients:
                    if client != websocket: #broadcast the message to all clients except the one that sent it, creating an ecosystem of connected devices
                        await client.send(message)
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
                break
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {websocket.remote_address}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        clients.remove(websocket)
        logger.info(f"Client removed. Total clients: {len(clients)}")

async def main():
    try:
        async with websockets.serve(handle_client, "0.0.0.0", 8765):
            logger.info("WebSocket server started on ws://0.0.0.0:8765")
            await asyncio.Future()  # run forever
    except Exception as e:
        logger.error(f"Server error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
