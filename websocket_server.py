import asyncio
import websockets

# List to keep track of connected clients
connected_clients = []

# Define a function to handle incoming WebSocket connections
async def handle_connection(websocket, path):
    try:
        # Append the new client to the list of connected clients
        connected_clients.append(websocket)

        async for message in websocket:
            # Handle incoming messages here
            await websocket.send(f"Received: {message}")
    except websockets.ConnectionClosedError:
        pass
    finally:
        # Remove the client from the list when the connection is closed
        connected_clients.remove(websocket)

# Create the WebSocket server
start_server = websockets.serve(handle_connection, "127.0.0.1", 7701)

# Start the WebSocket server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()




