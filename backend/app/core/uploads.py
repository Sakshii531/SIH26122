from __future__ import annotations

from fastapi import HTTPException, UploadFile


async def read_upload_with_limit(file: UploadFile, max_bytes: int) -> bytes:
    """Read at most max_bytes plus one byte so oversized uploads are rejected early."""
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed limit of {max_bytes // (1024 * 1024)}MB.",
        )
    return content