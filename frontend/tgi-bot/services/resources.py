import os
from typing import Optional

import aiofiles
import aiofiles.os


class ResourcesService:
    def __init__(self):
        self.resources_base_dir: str = os.path.join(os.getcwd(), "resources")

    async def get_text_resource(self, resource_name):
        html_resource: Optional[str] = await self._load_resource(
            os.path.join("text", resource_name + ".html")
        )
        if html_resource is not None:
            return html_resource

        txt_resource: Optional[str] = await self._load_resource(
            os.path.join("text", resource_name + ".txt")
        )
        if txt_resource is not None:
            return txt_resource

        raise FileNotFoundError(f'Resource "{resource_name}" not found.')

    async def _load_resource(self, resource_rel_path: str) -> Optional[str]:
        resource_path: str = os.path.join(self.resources_base_dir, resource_rel_path)
        if await aiofiles.os.path.exists(resource_path) is False:
            return None

        async with aiofiles.open(resource_path, "r") as f:
            return await f.read()
