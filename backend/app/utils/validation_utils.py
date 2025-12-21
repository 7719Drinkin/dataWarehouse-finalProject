"""
数据验证工具
"""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

class ValidationUtils:
    """数据验证工具类"""

    # 正则表达式模式
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
    DATETIME_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$'

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """验证必需字段"""
        errors = {}

        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                errors[field] = f"Field '{field}' is required"

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    @staticmethod
    def validate_rating(score: Any) -> Dict[str, Any]:
        """验证评分值"""
        try:
            if score is None:
                return {'valid': False, 'error': 'Score cannot be null'}

            score_val = float(score)
            if 0 <= score_val <= 5:
                return {'valid': True, 'value': score_val}
            else:
                return {'valid': False, 'error': 'Score must be between 0 and 5'}

        except (ValueError, TypeError):
            return {'valid': False, 'error': 'Invalid score format'}

    @staticmethod
    def validate_date(date_str: str) -> Dict[str, Any]:
        """验证日期格式"""
        if not date_str:
            return {'valid': False, 'error': 'Date cannot be empty'}

        # 检查格式
        if not re.match(ValidationUtils.DATE_PATTERN, date_str):
            return {'valid': False, 'error': 'Date must be in YYYY-MM-DD format'}

        # 检查有效性
        try:
            datetime.fromisoformat(date_str)
            return {'valid': True, 'value': date_str}
        except ValueError:
            return {'valid': False, 'error': 'Invalid date'}

    @staticmethod
    def validate_year(year: Any) -> Dict[str, Any]:
        """验证年份"""
        try:
            if year is None:
                return {'valid': False, 'error': 'Year cannot be null'}

            year_val = int(year)
            current_year = datetime.now().year

            if 1900 <= year_val <= current_year + 1:  # 允许明年
                return {'valid': True, 'value': year_val}
            else:
                return {'valid': False, 'error': f'Year must be between 1900 and {current_year + 1}'}

        except (ValueError, TypeError):
            return {'valid': False, 'error': 'Invalid year format'}

    @staticmethod
    def validate_string_length(text: str, min_length: int = 0, max_length: int = 1000) -> Dict[str, Any]:
        """验证字符串长度"""
        if text is None:
            text = ""

        length = len(str(text))

        if length < min_length:
            return {'valid': False, 'error': f'Text must be at least {min_length} characters long'}

        if length > max_length:
            return {'valid': False, 'error': f'Text must be no more than {max_length} characters long'}

        return {'valid': True, 'value': str(text)}

    @staticmethod
    def validate_movie_id(movie_id: Any) -> Dict[str, Any]:
        """验证电影ID"""
        if not movie_id:
            return {'valid': False, 'error': 'Movie ID cannot be empty'}

        movie_id_str = str(movie_id).strip()

        # 检查长度和格式（假设电影ID是字母数字组合）
        if not re.match(r'^[A-Za-z0-9_-]+$', movie_id_str):
            return {'valid': False, 'error': 'Movie ID contains invalid characters'}

        if len(movie_id_str) < 1 or len(movie_id_str) > 50:
            return {'valid': False, 'error': 'Movie ID length must be between 1 and 50 characters'}

        return {'valid': True, 'value': movie_id_str}

    @staticmethod
    def validate_genres(genres: Any) -> Dict[str, Any]:
        """验证电影类型"""
        if genres is None:
            return {'valid': True, 'value': []}

        if isinstance(genres, str):
            # 尝试分割字符串
            genres_list = [g.strip() for g in genres.split(',') if g.strip()]
        elif isinstance(genres, list):
            genres_list = genres
        else:
            return {'valid': False, 'error': 'Genres must be a string or list'}

        # 验证每个类型
        valid_genres = []
        for genre in genres_list:
            genre_clean = str(genre).strip()
            if genre_clean:
                # 检查是否包含有效字符
                if re.match(r'^[A-Za-z\s&\-\'()]+$', genre_clean):
                    valid_genres.append(genre_clean)
                else:
                    return {'valid': False, 'error': f'Invalid genre format: {genre}'}

        return {'valid': True, 'value': valid_genres}

    @staticmethod
    def validate_query_params(params: Dict[str, Any], param_rules: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """验证查询参数"""
        errors = {}
        validated_params = {}

        for param_name, rules in param_rules.items():
            param_value = params.get(param_name)

            # 检查必需参数
            if rules.get('required', False) and param_value is None:
                errors[param_name] = f"Parameter '{param_name}' is required"
                continue

            # 如果参数为空且非必需，跳过
            if param_value is None:
                continue

            # 类型转换和验证
            param_type = rules.get('type', str)
            try:
                if param_type == int:
                    param_value = int(param_value)
                elif param_type == float:
                    param_value = float(param_value)
                elif param_type == bool:
                    param_value = str(param_value).lower() in ('true', '1', 'yes')

                # 范围检查
                if 'min' in rules and param_value < rules['min']:
                    errors[param_name] = f"Parameter '{param_name}' must be at least {rules['min']}"
                    continue

                if 'max' in rules and param_value > rules['max']:
                    errors[param_name] = f"Parameter '{param_name}' must be no more than {rules['max']}"
                    continue

                # 自定义验证函数
                if 'validator' in rules:
                    validation_result = rules['validator'](param_value)
                    if not validation_result['valid']:
                        errors[param_name] = validation_result['error']
                        continue
                    param_value = validation_result.get('value', param_value)

            except (ValueError, TypeError):
                errors[param_name] = f"Parameter '{param_name}' must be of type {param_type.__name__}"
                continue

            validated_params[param_name] = param_value

        return {
            'valid': len(errors) == 0,
            'params': validated_params,
            'errors': errors
        }

    @staticmethod
    def sanitize_input(text: str) -> str:
        """清理输入，防止XSS等攻击"""
        if not text:
            return ""

        # 基本清理，移除危险HTML标签
        import html
        text = html.escape(text)

        # 移除潜在的脚本标签
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)  # 移除所有HTML标签

        return text.strip()

    @staticmethod
    def validate_api_request(request_data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """验证API请求数据"""
        errors = {}

        for field_name, field_rules in schema.items():
            field_value = request_data.get(field_name)

            # 必需字段检查
            if field_rules.get('required', False):
                validation = ValidationUtils.validate_required_fields(
                    {field_name: field_value}, [field_name]
                )
                if not validation['valid']:
                    errors.update(validation['errors'])
                    continue

            # 如果字段为空且非必需，跳过
            if field_value is None and not field_rules.get('required', False):
                continue

            # 类型验证
            field_type = field_rules.get('type')
            if field_type:
                try:
                    if field_type == int:
                        field_value = int(field_value)
                    elif field_type == float:
                        field_value = float(field_value)
                    elif field_type == list:
                        if isinstance(field_value, str):
                            field_value = [item.strip() for item in field_value.split(',')]
                        elif not isinstance(field_value, list):
                            field_value = [field_value]

                    # 更新验证后的值
                    request_data[field_name] = field_value

                except (ValueError, TypeError):
                    errors[field_name] = f"Must be of type {field_type.__name__}"
                    continue

            # 自定义验证
            if 'validator' in field_rules:
                validator_func = field_rules['validator']
                validation_result = validator_func(field_value)
                if not validation_result['valid']:
                    errors[field_name] = validation_result['error']
                    continue

                # 使用验证后的值
                if 'value' in validation_result:
                    request_data[field_name] = validation_result['value']

        return {
            'valid': len(errors) == 0,
            'data': request_data,
            'errors': errors
        }

