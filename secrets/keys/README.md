# SECURITY KEYS

This folder contains the RSA key pairs (private and public) required for the application's authentication system. These keys ensure the security, integrity, and confidentiality of the JSON Web Tokens (JWT).

## 1. Purpose of Files

The application uses two sets of keys for different security aspects:

-   **Signing Keys (`signing-private.pem` & `signing-public.pem`)**
    -   Used for **JWS (JSON Web Signature)**.
    -   **Private Key**: Uses the `JWT_SIGNING_KEY_PASSWORD` to sign the token, certifying that it was issued by this application.
    -   **Public Key**: Can be used to verify the signature of the token.

-   **Encryption Keys (`encryption-private.pem` & `encryption-public.pem`)**
    -   Used for **JWE (JSON Web Encryption)**.
    -   **Private Key**: Uses the `JWT_ENCRYPTION_KEY_PASSWORD` to decrypt the token and retrieve the user information.
    -   **Public Key**: Encrypts the token payload so that sensitive data is hidden from the client.

## 2. Authentication System

The authentication flow is designed to be highly secure by implementing both signing and encryption:

1.  **Token Creation**: When a user authenticates, the application generates a JWT.
2.  **Signing**: The payload is signed using the `signing-private.pem` key. This ensures the token cannot be tampered with without invalidating the signature.
3.  **Encryption**: The signed token is then encrypted using the `encryption-public.pem` key. This wraps the token in an encrypted layer, preventing anyone without the private key from reading the claims (user ID, roles, etc.).
4.  **Verification**: Upon receiving a request, the specific middleware verifies the token by first decrypting it with `encryption-private.pem` and then validating the signature with `signing-public.pem`.

## 3. Key Generation Commands

The following commands use `openssl` to generate the required 4096-bit RSA keys. They pull the passwords directly from your `.env` file variables (`JWT_SIGNING_KEY_PASSWORD` and `JWT_ENCRYPTION_KEY_PASSWORD`).

### 3.1 Load Environment Variables

Before running the commands, export the variables from your `.env` file to your current shell session:

```bash
set -a
source .env
set +a
```

### 3.2 Generate Signing Keys

-   **Generate Private Signing Key**:
    ```bash
    openssl genpkey -algorithm RSA -out secrets/keys/signing-private.pem -aes256 -pass pass:$JWT_SIGNING_KEY_PASSWORD -pkeyopt rsa_keygen_bits:4096
    ```

-   **Extract Public Signing Key**:
    ```bash
    openssl pkey -in secrets/keys/signing-private.pem -out secrets/keys/signing-public.pem -pubout -passin pass:$JWT_SIGNING_KEY_PASSWORD
    ```

### 3.3 Generate Encryption Keys

-   **Generate Private Encryption Key**:
    ```bash
    openssl genpkey -algorithm RSA -out secrets/keys/encryption-private.pem -aes256 -pass pass:$JWT_ENCRYPTION_KEY_PASSWORD -pkeyopt rsa_keygen_bits:4096
    ```

-   **Extract Public Encryption Key**:
    ```bash
    openssl pkey -in secrets/keys/encryption-private.pem -out secrets/keys/encryption-public.pem -pubout -passin pass:$JWT_ENCRYPTION_KEY_PASSWORD
    ```
