# Explicación del código AWS KMS

El código realiza un cifrado en sobre utilizando AWS KMS. Primero se crea una KMS Key, luego una Data Key para cifrar el mensaje y finalmente se guardan el mensaje cifrado y la Data Key cifrada dentro de un sobre digital.

## 1. Conexión y creación de la KMS Key

kms = boto3.client("kms")
key_id = kms.create_key()["KeyMetadata"]["KeyId"]

Primero se conecta a AWS KMS mediante Boto3 y se crea una KMS Key. Esta llave será utilizada para proteger la Data Key.

## 2. Generación de la Data Key

dk = kms.generate_data_key(KeyId=key_id, KeySpec="AES_256")
data_key = base64.urlsafe_b64encode(dk["Plaintext"])

KMS genera una Data Key en dos versiones: una en texto plano para cifrar el mensaje y otra cifrada por KMS para poder guardarla de forma segura.

## 3. Cifrado del mensaje

mensaje = "Mensaje secreto"
cifrado = Fernet(data_key).encrypt(mensaje.encode())

La Data Key en texto plano se utiliza para cifrar el mensaje. `encode()` convierte el texto a bytes para poder realizar el cifrado.

## 4. Creación del sobre digital

sobre = {
    "mensaje": base64.b64encode(cifrado).decode(),
    "key": base64.b64encode(dk["CiphertextBlob"]).decode()
}
open("sobre.json", "w").write(json.dumps(sobre))

El sobre contiene el mensaje cifrado y la Data Key cifrada por KMS. Después se guarda todo en `sobre.json`.

## 5. Descifrado

key = kms.decrypt(
    CiphertextBlob=base64.b64decode(sobre["key"]),
    KeyId=key_id
)["Plaintext"]

Se toma la Data Key cifrada del sobre y se envía a KMS para recuperarla en texto plano.

mensaje = Fernet(base64.urlsafe_b64encode(key)).decrypt(
    base64.b64decode(sobre["mensaje"])
).decode()

Con la Data Key recuperada se descifra el mensaje y se obtiene nuevamente el texto original.

## 6. Eliminación de la KMS Key

kms.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=7)

Al finalizar se programa la eliminación de la KMS Key. AWS no la elimina inmediatamente, sino después del período de espera establecido.

## Resumen

El flujo es:

**KMS Key → Data Key → cifrar mensaje → crear sobre → recuperar Data Key → descifrar mensaje → programar eliminación de KMS Key.**
