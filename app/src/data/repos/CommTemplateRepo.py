from typing import Optional, Dict, Any
import re
from kimera.store.StoreFactory import StoreFactory
from sqlalchemy import text


class CommTemplateRepo:
    """
    Repository for retrieving communication templates with localizations.
    """
    
    def __init__(self):
        """
        Initialize the repository with database store.
        """
        self.db = StoreFactory.get_rdb_store("postgres")
    
    async def connect(self):
        """Connect to the database."""
        await self.db.connect()
    
    @staticmethod
    def render_template(template_string: str, data: Dict[str, Any]) -> str:
        """
        Replace {{variable}} placeholders in template with values from data.
        
        Args:
            template_string: Template string with {{variable}} placeholders
            data: Dictionary with variable names as keys and replacement values as values
        
        Returns:
            Rendered template string with variables replaced
        """
        def replace_var(match):
            var_name = match.group(1).strip()
            return str(data.get(var_name, match.group(0)))
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, template_string)
    
    async def get_template_by_key_and_language(
        self, 
        key_name: str, 
        language: str = 'en'
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a communication template by key_name and language.
        
        Args:
            key_name: The template key (e.g., 'password_reset')
            language: The locale short name (e.g., 'en', 'ar')
        
        Returns:
            Dictionary containing template data with localization, or None if not found
        """
        try:
            async with self.db.session() as session:
                # First, get the locale ID from the short name
                locale_query = text("SELECT id FROM locales WHERE locale_short_name = :language")
                locale_result = await session.execute(locale_query, {"language": language})
                locale_row = locale_result.fetchone()
                
                if not locale_row:
                    print(f"[CommTemplateRepo] Locale '{language}' not found")
                    if language != 'en':
                        return await self.get_template_by_key_and_language(key_name, 'en')
                    return None
                
                locale_id = locale_row[0]
                print(f"[CommTemplateRepo] Locale '{language}' found with ID: {locale_id}")
                
                # Get template by key_name
                template_query = text("SELECT id, template_type, key_name, variables FROM comm_templates WHERE key_name = :key_name")
                template_result = await session.execute(template_query, {"key_name": key_name})
                template_row = template_result.fetchone()
                
                if not template_row:
                    print(f"[CommTemplateRepo] Template '{key_name}' not found")
                    return None
                
                template_id, template_type, template_key, variables = template_row
                print(f"[CommTemplateRepo] Template '{key_name}' found with ID: {template_id}")
                
                # Get localization for this template and locale
                localization_query = text("""
                    SELECT name, subject, content 
                    FROM comm_templates_localizations 
                    WHERE template_id = :template_id AND locale_id = :locale_id
                """)
                localization_result = await session.execute(localization_query, {"template_id": template_id, "locale_id": locale_id})
                localization_row = localization_result.fetchone()
                
                if not localization_row:
                    # Fallback to English if requested language not found
                    if language != 'en':
                        print(f"[CommTemplateRepo] Localization not found for template '{key_name}' in language '{language}', falling back to English")
                        return await self.get_template_by_key_and_language(key_name, 'en')
                    
                    print(f"[CommTemplateRepo] Localization not found for template '{key_name}' in language '{language}'")
                    return None
                
                name, subject, content = localization_row
                print(f"[CommTemplateRepo] Localization found for template '{key_name}'")
                
                # Get locale info for rtl
                locale_info_query = text("SELECT locale_short_name, rtl FROM locales WHERE id = :locale_id")
                locale_info_result = await session.execute(locale_info_query, {"locale_id": locale_id})
                locale_info_row = locale_info_result.fetchone()
                locale_short_name, rtl = locale_info_row
                
                return {
                    'id': template_id,
                    'template_type': template_type,
                    'key_name': template_key,
                    'variables': variables,
                    'localization': {
                        'locale_id': locale_id,
                        'name': name,
                        'subject': subject,
                        'content': content,
                        'locale_short_name': locale_short_name,
                        'rtl': rtl
                    }
                }
            
        except Exception as e:
            print(f"[CommTemplateRepo] Error fetching template: {e}")
            return None
    
    async def get_template_by_key(self, key_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a communication template by key_name (default language).
        
        Args:
            key_name: The template key (e.g., 'password_reset')
        
        Returns:
            Dictionary containing template data with default localization, or None if not found
        """
        try:
            # Query to get template with default locale
            query = """
                SELECT 
                    ct.id,
                    ct.template_type,
                    ct.key_name,
                    ct.variables,
                    ctl.locale_id,
                    ctl.name,
                    ctl.subject,
                    ctl.content,
                    l.locale_short_name,
                    l.rtl
                FROM comm_templates ct
                LEFT JOIN comm_templates_localizations ctl ON ct.id = ctl.template_id
                LEFT JOIN locales l ON ctl.locale_id = l.id
                WHERE ct.key_name = $1 
                  AND l.is_default = true
                LIMIT 1
            """
            
            result = await self.connection.fetchrow(query, key_name)
            
            if not result:
                print(f"[CommTemplateRepo] Template '{key_name}' not found")
                return None
            
            return {
                'id': result['id'],
                'template_type': result['template_type'],
                'key_name': result['key_name'],
                'variables': result['variables'],
                'localization': {
                    'locale_id': result['locale_id'],
                    'name': result['name'],
                    'subject': result['subject'],
                    'content': result['content'],
                    'locale_short_name': result['locale_short_name'],
                    'rtl': result['rtl']
                }
            }
            
        except Exception as e:
            print(f"[CommTemplateRepo] Error fetching template: {e}")
            return None
