-- No secret objects. The service authenticates with its SPCS session token and CI with key-pair
-- JWT (DECISIONS.md, "The service holds no secret"). The service user's public key is set by
-- runbooks/rotate-keys.md.
SELECT 'no secrets to create' AS note;
