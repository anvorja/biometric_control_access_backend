# app/core/validation_utils.py
import re
from typing import Optional, Tuple


class InputValidator:
    @staticmethod
    def sanitize_input(value: Optional[str]) -> Optional[str]:
        """Sanitiza la entrada para prevenir SQL injection"""
        if not value:
            return value

        # Patrones SQL peligrosos
        sql_patterns = [
            r"--",  # Comentarios SQL
            r";",  # Múltiples consultas
            r"'",  # Comillas simples
            r"/\*|\*/",  # Comentarios multilínea
            r"xp_",  # Procedimientos extendidos SQL Server
            r"EXEC\s+",  # Ejecución de procedimientos
            r"UNION\s+SELECT",  # UNION SELECT attacks
            r"DROP\s+TABLE",  # DROP TABLE attacks
            r"INSERT\s+INTO",  # INSERT INTO attacks
            r"DELETE\s+FROM",  # DELETE FROM attacks
            r"UPDATE\s+",  # UPDATE attacks
        ]

        cleaned = value
        for pattern in sql_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        return cleaned.strip()

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Valida que el nombre contenga solo caracteres permitidos.
        Retorna una tupla de (is_valid, error_message).
        """
        if not name:
            return False, "El nombre no puede estar vacío"

        # Verifica que no haya números
        if re.search(r'\d', name):
            return False, "El nombre no puede contener números"

        # Patrón que permite solo letras, espacios y tildes específicas
        valid_name_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚ\s]*$'

        if not re.match(valid_name_pattern, name):
            return False, "El nombre solo puede contener letras y espacios. Solo se permiten tildes en vocales (á, é, í, ó, ú)"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    @staticmethod
    def format_name(name: str) -> str:
        """Formatea nombres capitalizando cada palabra"""
        if not name:
            return name

        # Divide por espacios y capitaliza cada palabra
        words = name.lower().split()
        formatted_name = ' '.join(word.capitalize() for word in words)
        return formatted_name

    @staticmethod
    def format_email(email: str) -> str:
        """Formatea email a minúsculas"""
        return email.lower().strip() if email else email
