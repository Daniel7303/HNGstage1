from rest_framework import serializers
from .models import StringEntry

class CreateStringSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringEntry
        fields = ['value']

class StringEntrySerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = StringEntry
        fields = [
            'sha256_hash',
            'value',
            'properties',
            'created_at'
        ]
        read_only_fields = ['sha256_hash', 'created_at']

    def get_properties(self, obj):
        return {
            "length": obj.length,
            "is_palindrome": obj.is_palindrome,
            "unique_characters": obj.unique_characters,
            "word_count": obj.word_count,
            "sha256_hash": obj.sha256_hash,
            "character_frequency_map": obj.character_frequency_map,
        }
