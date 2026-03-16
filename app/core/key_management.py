from http import HTTPStatus
import subprocess
from pathlib import Path

from loguru import logger

from app.core.settings import settings
from app.modules.shared.presentation.exceptions import StandardException


async def init_security_keys() -> None:
    try:
        logger.info("Checking security keys...")

        keys_dir = Path("secrets/keys")
        if not keys_dir.exists():
            logger.info(f"Creating directory: {keys_dir}")
            keys_dir.mkdir(parents=True, exist_ok=True)

        signing_private = Path(settings.JWT_SIGNING_PRIVATE_KEY_PATH)
        signing_public = Path(settings.JWT_SIGNING_PUBLIC_KEY_PATH)
        encryption_private = Path(settings.JWT_ENCRYPTION_PRIVATE_KEY_PATH)
        encryption_public = Path(settings.JWT_ENCRYPTION_PUBLIC_KEY_PATH)

        if not signing_private.exists() or not signing_public.exists():
            logger.info("Signing keys not found. Generating...")
            _generate_signing_keys(signing_private, signing_public)
            logger.info("Signing keys generated successfully.")
        else:
            logger.info("Signing keys already exist.")

        if not encryption_private.exists() or not encryption_public.exists():
            logger.info("Encryption keys not found. Generating...")
            _generate_encryption_keys(encryption_private, encryption_public)
            logger.info("Encryption keys generated successfully.")
        else:
            logger.info("Encryption keys already exist.")

    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred while initializing security keys."
        )
        raise


def _generate_signing_keys(private_path: Path, public_path: Path) -> None:
    try:
        subprocess.run(
            [
                "openssl",
                "genpkey",
                "-algorithm",
                "RSA",
                "-out",
                str(private_path),
                "-aes256",
                "-pass",
                f"pass:{settings.JWT_SIGNING_KEY_PASSWORD}",
                "-pkeyopt",
                "rsa_keygen_bits:4096",
            ],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "openssl",
                "pkey",
                "-in",
                str(private_path),
                "-out",
                str(public_path),
                "-pubout",
                "-passin",
                f"pass:{settings.JWT_SIGNING_KEY_PASSWORD}",
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate signing keys: {e.stderr.decode()}")
        raise StandardException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Failed to generate signing keys.",
        )


def _generate_encryption_keys(private_path: Path, public_path: Path) -> None:
    try:
        subprocess.run(
            [
                "openssl",
                "genpkey",
                "-algorithm",
                "RSA",
                "-out",
                str(private_path),
                "-aes256",
                "-pass",
                f"pass:{settings.JWT_ENCRYPTION_KEY_PASSWORD}",
                "-pkeyopt",
                "rsa_keygen_bits:4096",
            ],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "openssl",
                "pkey",
                "-in",
                str(private_path),
                "-out",
                str(public_path),
                "-pubout",
                "-passin",
                f"pass:{settings.JWT_ENCRYPTION_KEY_PASSWORD}",
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate encryption keys: {e.stderr.decode()}")
        raise StandardException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Failed to generate encryption keys.",
        )
