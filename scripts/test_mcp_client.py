import asyncio
import json
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "freecad_mcp.server", "--freecadcmd", "C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Session initialized successfully!")
            
            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

if __name__ == "__main__":
    asyncio.run(main())
