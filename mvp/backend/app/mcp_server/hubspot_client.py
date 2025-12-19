import logging
from typing import Optional, List, Any
from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


class HubSpotClient:
    """HubSpot MCP Client - connects to HubSpot MCP server and retrieves available tools"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self._connected = False
        self.session: Optional[ClientSession] = None
        self._sse_context = None
        self._tools: Optional[List] = None

    async def connect(self):
        """Connect to HubSpot MCP server"""
        if self._connected:
            return 
        
        try:
            logger.info("Connecting to HubSpot MCP server...")
            
            # Create SSE client context
            self._sse_context = sse_client(
                url="https://mcp.hubspot.com/",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                }
            )
            
            # Enter the SSE context and get read/write streams
            read, write = await self._sse_context.__aenter__()
            
            # Create and initialize session
            self.session = ClientSession(read, write)
            await self.session.initialize()
            
            self._connected = True
            logger.info("✅ Connected to HubSpot MCP Server")
            
            # Load available tools
            await self._load_tools()
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to HubSpot MCP: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self._connected = False
            
            # Clean up SSE context on error
            if self._sse_context:
                try:
                    await self._sse_context.__aexit__(None, None, None)
                except:
                    pass
                self._sse_context = None
            
            self.session = None
            raise
    
    async def _load_tools(self) -> None:
        """Load available tools from MCP server"""
        if not self.session or not self._connected:
            return
        
        try:
            tools_result = await self.session.list_tools()
            self._tools = tools_result.tools
            logger.info(f"📦 Loaded {len(self._tools)} HubSpot tools")
            
            # Log tool names
            tool_names = [tool.name for tool in self._tools]
            logger.debug(f"Tools: {', '.join(tool_names)}")
            
        except Exception as e:
            logger.error(f"Failed to load tools: {e}")
            self._tools = []
    
    async def get_tools(self) -> List[Any]:
        """
        Get available tools from HubSpot MCP server
        
        Returns:
            List of available tools
        """
        if not self._connected:
            await self.connect()
        
        return self._tools or []
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server"""
        if self._sse_context and self._connected:
            try:
                await self._sse_context.__aexit__(None, None, None)
                self._connected = False
                self._tools = None
                self.session = None
                self._sse_context = None
                logger.info("🔌 Disconnected from HubSpot MCP Server")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected 


async def main():
    print("Getting integration config token_____")
    hubspot_token = ""

    obj = HubSpotClient(hubspot_token)  
    tools = await obj.get_tools()    

    print(f"Tools ----------- {tools}")

# Run the async function
import asyncio
asyncio.run(main())


