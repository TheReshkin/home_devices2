from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Генерация ключей для асимметричной криптографии
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Сериализация публичного ключа для отправки другому устройству
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Ваше устройство отправляет public_key_bytes другому устройству

# Получение public_key_bytes от устройства_1

# Другое устройство загружает публичный ключ
loaded_public_key = serialization.load_pem_public_key(public_key_bytes)

# Генерация ключа для симметричного шифрования (AES)
key = Fernet.generate_key()

# Зашифрование ключа симметричного шифрования с использованием публичного ключа
encrypted_key = loaded_public_key.encrypt(
    key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None  # Добавьте этот аргумент label и установите его в None
    )
)

# Отправка encrypted_key другому устройству


# Получение encrypted_key от устройства_2

# Другое устройство загружает закрытый ключ
private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()  # Установите NoEncryption
)
loaded_private_key = serialization.load_pem_private_key(private_key_bytes, password=None)  # Укажите password=None

# Дешифрование ключа симметричного шифрования с использованием закрытого ключа
decrypted_key = loaded_private_key.decrypt(
    encrypted_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Теперь у вас есть симметричный ключ decrypted_key, который можно использовать для шифрования и дешифрования данных

# Пример шифрования и дешифрования данных с использованием симметричного ключа
data_to_send = "Секретная информация"
fernet = Fernet(decrypted_key)
encrypted_data = fernet.encrypt(data_to_send.encode())
decrypted_data = fernet.decrypt(encrypted_data).decode()

print("Исходные данные:", data_to_send)
print("Расшифрованные данные:", decrypted_data)
