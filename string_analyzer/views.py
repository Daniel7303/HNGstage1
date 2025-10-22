import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StringEntry
from .serializers import CreateStringSerializer, StringEntrySerializer


# Utility: SHA-256 hash generator
def sha256_hash(value: str):
    return hashlib.sha256(value.encode()).hexdigest()


class StringListCreateView(APIView):
    """Handles POST /strings and GET /strings (with filters)"""

    def post(self, request):
        serializer = CreateStringSerializer(data=request.data)
        value = serializer.initial_data.get("value")

        # Validation
        if value is None:
            return Response({"details": "Missing 'value' field"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(value, str):
            return Response({"details": "Value must be a string"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if serializer.is_valid():
            # Check for duplicates
            existing = StringEntry.objects.filter(value=value.strip()).first()
            if existing:
                return Response({"details": "String already exists in the system"}, status=status.HTTP_409_CONFLICT)

            entry = serializer.save()
            return Response(StringEntrySerializer(entry).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        queryset = StringEntry.objects.all()

        # Query filters
        is_palindrome = request.query_params.get("is_palindrome")
        min_length = request.query_params.get("min_length")
        max_length = request.query_params.get("max_length")
        word_count = request.query_params.get("word_count")
        contains_char = request.query_params.get("contains_character")

        try:
            if is_palindrome is not None:
                queryset = queryset.filter(is_palindrome=is_palindrome.lower() == "true")
            if min_length is not None:
                queryset = queryset.filter(length__gte=int(min_length))
            if max_length is not None:
                queryset = queryset.filter(length__lte=int(max_length))
            if word_count is not None:
                queryset = queryset.filter(word_count=int(word_count))
            if contains_char is not None and len(contains_char) == 1:
                queryset = queryset.filter(value__icontains=contains_char)
        except ValueError:
            return Response({"details": "Invalid query parameter values"}, status=status.HTTP_400_BAD_REQUEST)

        data = StringEntrySerializer(queryset, many=True).data
        return Response(
            {
                "data": data,
                "count": len(data),
                "filters_applied": {
                    "is_palindrome": is_palindrome,
                    "min_length": min_length,
                    "max_length": max_length,
                    "word_count": word_count,
                    "contains_character": contains_char,
                },
            },
            status=status.HTTP_200_OK,
        )


class StringDetailView(APIView):
    """Handles GET /strings/{string_value} and DELETE /strings/{string_value}"""

    def get_object(self, string_value):
        return StringEntry.objects.filter(value=string_value).first()

    def get(self, request, string_value):
        entry = self.get_object(string_value)
        if not entry:
            return Response({"details": "String not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(StringEntrySerializer(entry).data, status=status.HTTP_200_OK)

    def delete(self, request, string_value):
        entry = self.get_object(string_value)
        if not entry:
            return Response({"details": "String not found"}, status=status.HTTP_404_NOT_FOUND)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NaturalLanguageFilterView(APIView):
    """Handles GET /strings/filter-by-natural-language?query=..."""

    def get(self, request):
        query = request.query_params.get("query")
        if not query:
            return Response({"details": "Missing query parameter"}, status=status.HTTP_400_BAD_REQUEST)

        q = query.lower()
        filters = {}

        # Basic keyword interpretation
        if "palindromic" in q or "palindrome" in q:
            filters["is_palindrome"] = True
        if "single word" in q:
            filters["word_count"] = 1
        if "longer than" in q:
            try:
                num = int(q.split("longer than")[1].split()[0])
                filters["min_length"] = num + 1
            except Exception:
                pass
        if "containing the letter" in q:
            try:
                filters["contains_character"] = q.split("containing the letter")[1].strip().split()[0]
            except Exception:
                pass

        # Apply filters
        queryset = StringEntry.objects.all()
        if "is_palindrome" in filters:
            queryset = queryset.filter(is_palindrome=True)
        if "word_count" in filters:
            queryset = queryset.filter(word_count=filters["word_count"])
        if "min_length" in filters:
            queryset = queryset.filter(length__gt=filters["min_length"])
        if "contains_character" in filters:
            queryset = queryset.filter(value__icontains=filters["contains_character"])

        data = StringEntrySerializer(queryset, many=True).data
        return Response(
            {
                "data": data,
                "count": len(data),
                "interpreted_query": {
                    "original": query,
                    "parsed_filters": filters,
                },
            },
            status=status.HTTP_200_OK,
        )


class DeleteStringView(APIView):
    """Handles DELETE /strings/{string_value} via SHA-256 key"""

    def delete(self, request, string_value):
        key = sha256_hash(string_value)
        entry = StringEntry.objects.filter(pk=key).first()
        if not entry:
            return Response({"details": "String does not exist in the system"}, status=status.HTTP_404_NOT_FOUND)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
