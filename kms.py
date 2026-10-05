import boto3, json, base64
from cryptography.fernet import Fernet

kms = boto3.client("kms")

# 1. Crear la KMS Key
key_id = kms.create_key()["KeyMetadata"]["KeyId"]

# 2. Generar Data Key
dk = kms.generate_data_key(KeyId=key_id, KeySpec="AES_256")
data_key = base64.urlsafe_b64encode(dk["Plaintext"])

# 3. Cifrar mensaje
mensaje = "Mensaje secreto del examen"
cifrado = Fernet(data_key).encrypt(mensaje.encode())

# 4. Crear el sobre
sobre = {
    "mensaje": base64.b64encode(cifrado).decode(),
    "key": base64.b64encode(dk["CiphertextBlob"]).decode()
}
open("sobre.json", "w").write(json.dumps(sobre))

# 5. Función para descifrar
def descifrar(sobre):
    key = kms.decrypt(
        CiphertextBlob=base64.b64decode(sobre["key"]),
        KeyId=key_id
    )["Plaintext"]
    mensaje = Fernet(base64.urlsafe_b64encode(key)).decrypt(
        base64.b64decode(sobre["mensaje"])
    ).decode()
    print("Mensaje:", mensaje)
    print("Key:", key.hex())

descifrar(sobre)

# 6. Programar eliminación de la KMS Key
kms.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=7)
