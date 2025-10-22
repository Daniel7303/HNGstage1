import hashlib
from django.db import models
from django.utils import timezone

class StringEntry(models.Model):
    sha256_hash = models.CharField(max_length=64, primary_key=True, editable=False)
    value = models.TextField(unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Normalize value before saving
        self.value = self.value.strip()

        # Compute properties
        self.length = len(self.value)
        self.is_palindrome = self._compute_palindrome()
        self.unique_characters = len(set(self.value))
        self.word_count = len(self.value.split())
        self.sha256_hash = hashlib.sha256(self.value.encode()).hexdigest()
        self.character_frequency_map = self._char_frequency_map()

        super().save(*args, **kwargs)

    def _compute_palindrome(self):
        # Case-insensitive, ignores spaces
        normalized = ''.join(self.value.lower().split())
        return normalized == normalized[::-1]

    def _char_frequency_map(self):
        freq = {}
        for char in self.value:
            freq[char] = freq.get(char, 0) + 1
        return freq

    def __str__(self):
        return self.value
