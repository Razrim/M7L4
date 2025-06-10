import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Testlerden önce veri tabanını oluşturmak ve testlerden sonra temizlemek için kullanılan test düzeneği."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Test sırasında veri tabanı bağlantısı oluşturur ve testten sonra bağlantıyı kapatır."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Veri tabanı ve 'users' tablosunun oluşturulmasını test eder."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "'users' tablosu veri tabanında bulunmalıdır."

def test_add_new_user(setup_database, connection):
    """Yeni bir kullanıcının eklenmesini test eder."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Kullanıcı veri tabanına eklenmiş olmalıdır."

# İşte yazabileceğiniz bazı testler:
"""
Var olan bir kullanıcı adıyla kullanıcı eklemeye çalışmayı test etme.
Başarılı kullanıcı doğrulamasını test etme.
Var olmayan bir kullanıcıyla doğrulama yapmayı test etme.
Yanlış şifreyle doğrulama yapmayı test etme.
Kullanıcı listesinin doğru şekilde görüntülenmesini test etme.
"""
def test_add_duplicate_user(setup_database):
    """Aynı kullanıcı adıyla kullanıcı eklenmeye çalışıldığında başarısız olmalıdır."""
    add_user('duplicateuser', 'dup@example.com', 'abc123')
    result = add_user('duplicateuser', 'dup2@example.com', 'xyz456')
    assert result is False, "Aynı kullanıcı adıyla ikinci kez kayıt başarısız olmalıdır."

def test_authenticate_valid_user(setup_database):
    """Geçerli kullanıcı adı ve şifre ile doğrulama başarılı olmalıdır."""
    add_user('validuser', 'valid@example.com', 'pass123')
    is_authenticated = authenticate_user('validuser', 'pass123')
    assert is_authenticated is True, "Geçerli bilgilerle doğrulama başarılı olmalıdır."

def test_authenticate_invalid_user(setup_database):
    """Kullanıcı veri tabanında yoksa doğrulama başarısız olmalıdır."""
    is_authenticated = authenticate_user('nonexistentuser', 'whatever')
    assert is_authenticated is False, "Mevcut olmayan kullanıcıyla doğrulama başarısız olmalıdır."

def test_authenticate_wrong_password(setup_database):
    """Geçerli kullanıcı adı ancak yanlış şifre ile doğrulama başarısız olmalıdır."""
    add_user('wrongpassuser', 'wrongpass@example.com', 'correctpass')
    is_authenticated = authenticate_user('wrongpassuser', 'wrongpass')
    assert is_authenticated is False, "Yanlış şifre ile doğrulama başarısız olmalıdır."

def test_display_users_output(capsys, setup_database):
    """display_users fonksiyonunun çıktısının doğru formatta olup olmadığını test eder."""
    add_user('displayuser', 'display@example.com', 'disp123')
    display_users()
    captured = capsys.readouterr()
    assert "Kullanıcı adı: displayuser, E-posta: display@example.com" in captured.out
