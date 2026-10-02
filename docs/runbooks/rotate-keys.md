# Key rotation runbook

## Quarterly rotation schedule
Service account RSA key pairs are rotated quarterly.

## Steps
1. Generate a new RSA key pair:
   ```bash
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out new_rsa_key.p8 -nocrypt
   openssl rsa -in new_rsa_key.p8 -pubout -out new_rsa_key.pub
   ```

2. Set the new public key on the service user:
   ```sql
   ALTER USER SCM_SERVICE_USER SET RSA_PUBLIC_KEY_2 = '<new_public_key>';
   ```

3. Update the secret in Snowflake:
   ```sql
   ALTER SECRET SCM_DEV.AGENT.SCM_SERVICE_KEY SET SECRET_STRING = '<new_private_key>';
   ```

4. Verify the new key works:
   ```bash
   snow connection test --connection scm_service
   ```

5. Remove the old key:
   ```sql
   ALTER USER SCM_SERVICE_USER UNSET RSA_PUBLIC_KEY;
   ALTER USER SCM_SERVICE_USER SET RSA_PUBLIC_KEY = '<new_public_key>';
   ALTER USER SCM_SERVICE_USER UNSET RSA_PUBLIC_KEY_2;
   ```

6. Record the rotation in OPS.KEY_ROTATIONS (create if needed).

## Verification
- Service continues to respond on /health.
- A governed query succeeds through the API.
