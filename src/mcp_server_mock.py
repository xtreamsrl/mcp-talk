from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hugger-server")

@mcp.tool("give_me_a_virtual_hug")
def give_me_a_virtual_hug(name: str) -> str:
    return f"Hello {name}! I'm giving you a virtual hug!"


if __name__ == "__main__":
    mcp.run(transport='stdio')
