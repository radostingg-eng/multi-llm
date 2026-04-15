"""Tests for key encryption/decryption."""


class TestEncryption:
    def test_round_trip(self, mod):
        key = "AIzaSyDfmuj_test_key_12345"
        passphrase = "my-secret"
        encrypted = mod.encrypt_key(key, passphrase)
        assert mod.decrypt_key(encrypted, passphrase) == key

    def test_wrong_passphrase_produces_garbage(self, mod):
        key = "AIzaSyDfmuj_test_key_12345"
        encrypted = mod.encrypt_key(key, "correct")
        # Wrong passphrase should either produce garbage or raise
        try:
            result = mod.decrypt_key(encrypted, "wrong")
            assert result != key
        except UnicodeDecodeError:
            pass  # Also acceptable — garbled bytes

    def test_different_keys_produce_different_ciphertext(self, mod):
        p = "same-passphrase"
        enc1 = mod.encrypt_key("key-aaa", p)
        enc2 = mod.encrypt_key("key-bbb", p)
        assert enc1 != enc2

    def test_empty_key(self, mod):
        encrypted = mod.encrypt_key("", "pass")
        assert mod.decrypt_key(encrypted, "pass") == ""

    def test_long_key(self, mod):
        key = "x" * 500
        encrypted = mod.encrypt_key(key, "pass")
        assert mod.decrypt_key(encrypted, "pass") == key
